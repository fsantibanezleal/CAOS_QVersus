"""Shared circuit→trace tracer (Qiskit). NOT imported by qversus.core.__init__, so `import qversus.core`
stays Qiskit-free (live-thin); only the precompute solvers import this.

Given a Qiskit circuit built gate-by-gate, `evolve` replays it one instruction at a time on a
`Statevector`, recording, after every step, the full statevector, the per-qubit reduced Bloch vector,
and the basis-state probabilities. That sequence of `Step`s IS the animation a consumer replays. Any
circuit-model solver (Qiskit, Cirq via QASM, …) funnels through here so every framework yields the same
trace shape, the adapter boundary the registry depends on.

Qubit/index convention (documented once, used everywhere): Qiskit's native little-endian, basis index
`i` has qubit 0 as its least-significant bit. The web renderer uses the same arrays, never reversed.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector, partial_trace

from qversus.core.rng import sample_counts
from qversus.core.trace import ROUND, Step, amp

_PAULIS = ("X", "Y", "Z")


def bloch(sv: Statevector, n: int) -> list[list[float]]:
    """Per-qubit reduced Bloch vector [⟨X⟩, ⟨Y⟩, ⟨Z⟩] via the reduced density matrix."""
    out: list[list[float]] = []
    for q in range(n):
        others = [j for j in range(n) if j != q]
        rho = partial_trace(sv, others)
        out.append([round(float(rho.expectation_value(Pauli(p)).real), ROUND) for p in _PAULIS])
    return out


def _scalar_params(params) -> list[float]:
    """Keep only real scalar gate params (a UnitaryGate carries a matrix, not floats, skip those)."""
    out: list[float] = []
    for x in params or []:
        try:
            out.append(round(float(x), ROUND))
        except (TypeError, ValueError):
            pass
    return out


def step_of(index: int, gate: str, targets, label: dict, sv: Statevector, n: int, params=None) -> Step:
    return Step(
        index=index,
        gate=gate,
        targets=[int(t) for t in targets],
        label=label,
        statevector=[amp(z) for z in sv.data],
        bloch=bloch(sv, n),
        probabilities=[round(float(p), ROUND) for p in sv.probabilities()],
        params=_scalar_params(params),
    )


def evolve(qc: QuantumCircuit, captions: list[dict] | None = None) -> list[Step]:
    """Step-replay a circuit, returning the per-step trace (incl. an initial |0…0⟩ frame).

    `captions[k]` (optional) is the bilingual label for the k-th unitary instruction (0-based).
    """
    n = qc.num_qubits
    sv = Statevector.from_int(0, 2**n)
    steps = [step_of(0, "init", [], {"en": "Initial state |0…0⟩", "es": "Estado inicial |0…0⟩"}, sv, n)]
    k = 0
    for inst in qc.data:
        op = inst.operation
        if op.name in ("measure", "barrier"):
            continue
        qargs = [qc.find_bit(q).index for q in inst.qubits]
        sub = QuantumCircuit(n)
        sub.append(op, qargs)
        sv = sv.evolve(sub)
        label = captions[k] if (captions and k < len(captions) and captions[k]) else {
            "en": f"{op.name.upper()} q{qargs}",
            "es": f"{op.name.upper()} q{qargs}",
        }
        steps.append(step_of(k + 1, op.name.upper(), qargs, label, sv, n, list(op.params)))
        k += 1
    return steps


def circuit_ops(qc: QuantumCircuit) -> list[dict]:
    """A flat, JSON-able op list for the diagram renderer (excludes barriers)."""
    ops: list[dict] = []
    for inst in qc.data:
        op = inst.operation
        if op.name == "barrier":
            continue
        ops.append(
            {
                "gate": op.name,
                "targets": [qc.find_bit(q).index for q in inst.qubits],
                "params": _scalar_params(op.params),
            }
        )
    return ops


def measure_counts(qc: QuantumCircuit, shots: int, seed: int) -> dict:
    """Final measurement histogram, sampled deterministically from the exact final statevector."""
    sv = Statevector.from_int(0, 2**qc.num_qubits).evolve(qc)
    counts = sample_counts(np.asarray(sv.probabilities()), shots=shots, seed=seed)
    return {"counts": counts, "shots": shots}
