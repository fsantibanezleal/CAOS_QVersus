"""Cirq adapter, real Cirq, a THIRD independent QAOA implementation for MaxCut.

This is the extensibility claim proven a third time: a new framework is one adapter + one registry line,
no change to core/pipeline/web. With Qiskit + PennyLane + Cirq all attacking the same graph, agreement on
the cut value is a strong three-way cross-check (disagreement would be a bug). Cirq builds the QAOA ansatz
natively; the cut expectation ⟨C⟩ = Σ_x p(x)·cut(x) is read straight off the statevector, so the exact gate
convention is irrelevant, what is reported is the true cut of the actual state.
"""

from __future__ import annotations

import time

import numpy as np

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult

try:
    import cirq

    CIRQ_VERSION = cirq.__version__
except Exception:  # pragma: no cover
    cirq = None
    CIRQ_VERSION = "unknown"


@register_solver
class CirqQAOA(Solver):
    name = "qaoa-cirq"
    label = {"en": "QAOA (p=1) · Cirq", "es": "QAOA (p=1) · Cirq"}
    framework = "cirq"
    paradigm = QUANTUM_SIM
    GRID = 24

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "maxcut" and cirq is not None

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        n, edges = instance.params["n"], instance.params["edges"]
        qubits = cirq.LineQubit.range(n)
        sim = cirq.Simulator()
        cuts = np.array(
            [problem.cut_value(edges, format(i, f"0{n}b")) for i in range(2**n)], dtype=float
        )  # cirq is big-endian: basis index i ⇒ bit 0 (MSB) = qubit 0 = position 0 → cut_value(bits[u]=qubit u)

        def ansatz(gamma: float, beta: float) -> "cirq.Circuit":
            c = cirq.Circuit()
            c.append(cirq.H.on_each(*qubits))
            for u, v in edges:
                c.append(cirq.ZZ(qubits[u], qubits[v]) ** gamma)
            c.append(cirq.rx(2.0 * beta).on_each(*qubits))
            return c

        def probs(gamma: float, beta: float) -> np.ndarray:
            sv = sim.simulate(ansatz(gamma, beta)).final_state_vector
            return np.abs(np.asarray(sv)) ** 2

        t0 = time.perf_counter()
        gammas = np.linspace(0, np.pi, self.GRID)
        betas = np.linspace(0, np.pi, self.GRID)
        best = (gammas[0], betas[0], -np.inf)
        for g in gammas:
            for b in betas:
                e = float(np.dot(probs(g, b), cuts))   # ⟨C⟩ = Σ p(x) cut(x)
                if e > best[2]:
                    best = (g, b, e)
        g_best, b_best, exp_best = best
        p = probs(g_best, b_best)
        idx = int(np.argmax(p))
        bits = format(idx, f"0{n}b")
        cut = problem.cut_value(edges, bits)
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"cut": cut, "bitstring": bits, "expectation": round(exp_best, 4)},
            cost={"wall_ms": round(wall, 1), "qubits": n, "evaluations": self.GRID ** 2},
            notes={"en": "Independent QAOA on cirq.Simulator (same (γ,β) grid as Qiskit/PennyLane); "
                         f"most-probable bitstring cuts {cut} edges, third cross-check.",
                   "es": "QAOA independiente en cirq.Simulator (misma malla (γ,β) que Qiskit/PennyLane); "
                         f"la cadena más probable corta {cut} aristas, tercera verificación cruzada."},
        )
