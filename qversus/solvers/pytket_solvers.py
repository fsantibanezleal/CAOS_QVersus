"""pytket adapter: Quantinuum's t|ket⟩ compiler on the compilation problem.

The source op list becomes a pytket `Circuit`; `FullPeepholeOptimise` resynthesises it (two-qubit blocks, Clifford
simplification, trailing swaps folded into an implicit wire permutation), `AutoRebase` maps it onto {CX, RZ, SX, X}
and `RemoveRedundancies` clears what the rebase leaves. The check compares pytket's own unitary of the result
(which applies the implicit permutation) with the NumPy unitary of the source.
"""

from __future__ import annotations

import math
import time

import numpy as np
from pytket import Circuit, OpType
from pytket.passes import AutoRebase, FullPeepholeOptimise, RemoveRedundancies

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult

try:
    from importlib.metadata import version

    PYTKET_VERSION = version("pytket")
except Exception:  # pragma: no cover
    PYTKET_VERSION = "unknown"

# Source gate -> pytket op type; angles go to pytket in half-turns (radians / π).
_TO_TKET = {
    "h": OpType.H, "x": OpType.X, "y": OpType.Y, "z": OpType.Z, "s": OpType.S, "sdg": OpType.Sdg, "t": OpType.T,
    "tdg": OpType.Tdg, "rx": OpType.Rx, "ry": OpType.Ry, "rz": OpType.Rz, "p": OpType.U1, "cx": OpType.CX,
    "cz": OpType.CZ, "cp": OpType.CU1, "swap": OpType.SWAP, "ccx": OpType.CCX,
}
_FROM_TKET = {OpType.CX: "cx", OpType.Rz: "rz", OpType.SX: "sx", OpType.X: "x"}


def _big_to_little_endian(u: np.ndarray, n: int) -> np.ndarray:
    """pytket orders basis states with qubit 0 most significant; qversus with qubit 0 least significant."""
    t = u.reshape([2] * (2 * n))
    axes = list(reversed(range(n))) + [n + i for i in reversed(range(n))]
    return t.transpose(axes).reshape(2**n, 2**n)


@register_solver
class PytketCompile(Solver):
    name = "compile-pytket"
    label = {"en": "FullPeepholeOptimise · pytket", "es": "FullPeepholeOptimise · pytket"}
    framework = "pytket"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "compilation"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.problems.compilation import BASIS, compiled_value, source_circuit, unitary
        from qversus.problems.compilation import equivalent as same_unitary

        n = instance.params["n"]
        src = source_circuit(instance.params)
        circ = Circuit(n)
        for op in src:
            circ.add_gate(_TO_TKET[op["gate"]], [p / math.pi for p in op["params"]], op["targets"])
        t0 = time.perf_counter()
        FullPeepholeOptimise().apply(circ)
        AutoRebase({OpType.CX, OpType.Rz, OpType.SX, OpType.X}).apply(circ)
        RemoveRedundancies().apply(circ)
        wall = (time.perf_counter() - t0) * 1e3

        ops = []
        for cmd in circ.get_commands():
            gate = _FROM_TKET[cmd.op.type]
            ops.append({"gate": gate, "targets": [q.index[0] for q in cmd.qubits],
                        "params": [round(float(p) * math.pi, 9) for p in cmd.op.params]})
        assert {op["gate"] for op in ops} <= set(BASIS)
        perm = circ.implicit_qubit_permutation()
        wires = [perm[q].index[0] for q in sorted(perm, key=lambda q: q.index[0])]
        ok = same_unitary(_big_to_little_endian(np.asarray(circ.get_unitary()), n), unitary(src, n))
        value = compiled_value(src, ops, n, ok, wires)
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value=value,
            cost={"wall_ms": round(wall, 3), "qubits": n},
            notes={"en": f"pytket {PYTKET_VERSION}, FullPeepholeOptimise then a rebase to {{CX, RZ, SX, X}}: "
                         f"{value['two_qubit']} CX (against {value['rebased']['two_qubit']} gate by gate), depth "
                         f"{value['depth']}, {value['gates']} gates; same unitary: {'yes' if ok else 'NO'}.",
                   "es": f"pytket {PYTKET_VERSION}, FullPeepholeOptimise y luego una rebase a {{CX, RZ, SX, X}}: "
                         f"{value['two_qubit']} CX (frente a {value['rebased']['two_qubit']} compuerta a compuerta), "
                         f"profundidad {value['depth']}, {value['gates']} compuertas; mismo unitario: "
                         f"{'sí' if ok else 'NO'}."},
            extra={"engine_version": PYTKET_VERSION, "compiled_ops": ops},
        )
