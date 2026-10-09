"""Qulacs adapter: the circuit the Qiskit solver builds, simulated by a second, independent state-vector engine.

Qulacs (QunaSys, MIT) is a fast C++ state-vector simulator. The adapter asks the Qiskit solver for the instance's
circuit, translates every instruction into a Qulacs dense-matrix gate built from Qiskit's own matrix for it (so no
rotation-sign or qubit-order convention can differ between the two), evolves |0…0⟩ in Qulacs, and reports how far
the two final states are apart and how long Qulacs took. It needs Qiskit to build the circuit and Qulacs to run it.
"""

from __future__ import annotations

import time

import numpy as np
import qulacs
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qulacs.gate import DenseMatrix

from qversus.core.rng import sample_counts
from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult

try:
    from importlib.metadata import version

    QULACS_VERSION = version("qulacs")
except Exception:  # pragma: no cover
    QULACS_VERSION = "unknown"

# Problems whose Qiskit circuit is made of ordinary gates (no opaque state-preparation instruction).
SUPPORTED = {"single-qubit", "interference", "qft", "grover", "bernstein-vazirani", "deutsch-jozsa"}


def _rebuild(ops: list[dict], n: int) -> QuantumCircuit:
    """The Qiskit circuit from the trace's op list (gate name, qubits, parameters)."""
    qc = QuantumCircuit(n)
    for op in ops:
        g, t, p = op["gate"].lower(), op["targets"], op.get("params") or []
        if g == "barrier":
            continue
        if g == "mcx":
            qc.mcx(t[:-1], t[-1])
        else:
            getattr(qc, g)(*p, *t)
    return qc


@register_solver
class QulacsStateVector(Solver):
    name = "statevector-qulacs"
    label = {"en": "Same circuit · Qulacs", "es": "Mismo circuito · Qulacs"}
    framework = "qulacs"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id in SUPPORTED

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.registry import solvers_for

        reference = next(s for s in solvers_for(problem) if s.framework == "qiskit")
        ref = reference.run(problem, instance, seed=seed, shots=shots)
        n = ref.trace.qubits
        qc = _rebuild(ref.trace.circuit_ops, n)

        circuit = qulacs.QuantumCircuit(n)
        for inst in qc.data:
            targets = [qc.find_bit(q).index for q in inst.qubits]
            circuit.add_gate(DenseMatrix(targets, Operator(inst.operation).data))
        state = qulacs.QuantumState(n)
        t0 = time.perf_counter()
        circuit.update_quantum_state(state)
        wall = (time.perf_counter() - t0) * 1e3
        vec = np.asarray(state.get_vector())

        final = ref.trace.steps[-1].statevector
        want = np.array([a["re"] + 1j * a["im"] for a in final])
        diff = float(np.max(np.abs(vec - want)))          # the trace rounds to 6 decimals
        probs = np.abs(vec) ** 2
        counts = sample_counts(probs, shots=shots, seed=seed)
        top = max(counts, key=counts.get)
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"matches_qiskit": diff < 1e-5, "max_abs_diff": round(diff, 9), "top_outcome": top,
                   "gates": len(qc.data)},
            cost={"wall_ms": round(wall, 4), "qubits": n, "qiskit_wall_ms": ref.cost.get("wall_ms")},
            notes={"en": f"The {len(qc.data)} gates Qiskit built, simulated by Qulacs {QULACS_VERSION}: the final state "
                         f"differs from Qiskit's by at most {diff:.1e} (the trace's rounding), in {wall:.3f} ms. Two "
                         "independent engines agree; at this size neither has anything to prove on speed.",
                   "es": f"Las {len(qc.data)} compuertas que construyó Qiskit, simuladas por Qulacs {QULACS_VERSION}: el "
                         f"estado final difiere del de Qiskit en a lo más {diff:.1e} (el redondeo de la traza), en "
                         f"{wall:.3f} ms. Dos motores independientes coinciden; a este tamaño ninguno tiene nada que "
                         "demostrar en velocidad."},
            extra={"engine_version": QULACS_VERSION, "counts": counts},
        )
