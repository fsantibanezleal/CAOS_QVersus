"""Circuit compilation: the same unitary in fewer two-qubit gates and less depth.

A quantum algorithm is written in convenient gates (H, controlled phases, Toffolis, swaps); a device runs a small
native set, here the IBM-like {CX, RZ, SX, X}. Translating gate by gate is always correct but wasteful; an
optimising compiler resynthesises the circuit, cancels redundancies and folds trailing swaps into a relabelling
of the output wires. Two-qubit gates dominate the error of today's devices, so their count is the metric. Every
compiled circuit is checked to be the source unitary up to a global phase. This is classical software for
quantum hardware: no quantum advantage is claimed, only the cost a good compiler saves.

The circuits are framework-free op lists ({"gate", "targets", "params"}, Qiskit's little-endian convention); this
module simulates them with NumPy, so the equivalence check depends on none of the compilers it checks.
"""

from __future__ import annotations

import math

import numpy as np

from qversus.core.rng import make_rng
from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

BASIS = ("cx", "rz", "sx", "x")

_S2 = 1 / math.sqrt(2)
_FIXED = {
    "h": np.array([[_S2, _S2], [_S2, -_S2]], dtype=complex),
    "x": np.array([[0, 1], [1, 0]], dtype=complex),
    "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "z": np.diag([1, -1]).astype(complex),
    "s": np.diag([1, 1j]),
    "sdg": np.diag([1, -1j]),
    "t": np.diag([1, np.exp(1j * math.pi / 4)]),
    "tdg": np.diag([1, np.exp(-1j * math.pi / 4)]),
    "sx": 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]]),
}


def _one_qubit(gate: str, params: list[float]) -> np.ndarray:
    if gate in _FIXED:
        return _FIXED[gate]
    a = params[0]
    if gate == "rz":
        return np.diag([np.exp(-0.5j * a), np.exp(0.5j * a)])
    if gate == "p":
        return np.diag([1, np.exp(1j * a)])
    c, s = math.cos(a / 2), math.sin(a / 2)
    if gate == "rx":
        return np.array([[c, -1j * s], [-1j * s, c]])
    if gate == "ry":
        return np.array([[c, -s], [s, c]], dtype=complex)
    raise ValueError(f"unknown gate {gate!r}")


def _controlled(u: np.ndarray, controls: int) -> np.ndarray:
    """The gate u on the last wire, applied when every control wire is 1 (wire j is index bit j)."""
    k = controls + 1
    m = np.eye(2**k, dtype=complex)
    base = 2**controls - 1                      # all controls set, target 0
    idx = [base, base + 2**controls]
    m[np.ix_(idx, idx)] = u
    return m


def gate_matrix(gate: str, params: list[float]) -> np.ndarray:
    """The matrix of an op on its target wires, index bit j = targets[j] (Qiskit's convention)."""
    if gate == "cx":
        return _controlled(_FIXED["x"], 1)
    if gate == "cz":
        return _controlled(_FIXED["z"], 1)
    if gate == "cp":
        return _controlled(_one_qubit("p", params), 1)
    if gate == "ccx":
        return _controlled(_FIXED["x"], 2)
    if gate == "swap":
        return np.eye(4, dtype=complex)[[0, 2, 1, 3]]
    return _one_qubit(gate, params)


def unitary(ops: list[dict], n: int) -> np.ndarray:
    """The 2ⁿ x 2ⁿ unitary of an op list (basis index i has qubit 0 as its least-significant bit)."""
    u = np.eye(2**n, dtype=complex).reshape([2] * n + [2**n])
    for op in ops:
        wires = op["targets"]
        k = len(wires)
        m = gate_matrix(op["gate"], op.get("params") or []).reshape([2] * (2 * k))
        axes = [n - 1 - w for w in reversed(wires)]        # tensor axis of each matrix index, MSB first
        u = np.tensordot(m, u, axes=(list(range(k, 2 * k)), axes))
        u = np.moveaxis(u, list(range(k)), axes)
    return u.reshape(2**n, 2**n)


def equivalent(a: np.ndarray, b: np.ndarray, tol: float = 1e-8) -> bool:
    """Equal up to a global phase: |Tr(A†B)| / dim = 1."""
    return abs(abs(np.trace(a.conj().T @ b)) / a.shape[0] - 1) < tol


def metrics(ops: list[dict], n: int) -> dict:
    """Two-qubit count, depth (longest chain of gates on any wire) and total gates."""
    layer = [0] * n
    for op in ops:
        top = max(layer[w] for w in op["targets"]) + 1
        for w in op["targets"]:
            layer[w] = top
    return {"two_qubit": sum(len(op["targets"]) >= 2 for op in ops), "depth": max(layer, default=0),
            "gates": len(ops)}


def compiled_value(source: list[dict], compiled: list[dict], n: int, ok: bool, output_wires: list[int]) -> dict:
    """The uniform result of a compiler: its counts, the check, and the source and rebase-only counts beside it."""
    got, base = metrics(compiled, n), metrics(rebase(source), n)
    return {**got, "equivalent": bool(ok), "output_wires": [int(w) for w in output_wires],
            "relabels_wires": list(output_wires) != list(range(n)), "source": metrics(source, n), "rebased": base,
            "two_qubit_saved": base["two_qubit"] - got["two_qubit"]}


def _op(gate: str, targets, params=()) -> dict:
    return {"gate": gate, "targets": [int(t) for t in targets], "params": [float(p) for p in params]}


_PI = math.pi
# One gate in terms of simpler ones; `rebase` applies these until only BASIS gates remain.
_RULES = {
    "h": lambda q, p: [_op("rz", q, [_PI / 2]), _op("sx", q), _op("rz", q, [_PI / 2])],
    "y": lambda q, p: [_op("rz", q, [_PI]), _op("x", q)],
    "z": lambda q, p: [_op("rz", q, [_PI])],
    "s": lambda q, p: [_op("rz", q, [_PI / 2])],
    "sdg": lambda q, p: [_op("rz", q, [-_PI / 2])],
    "t": lambda q, p: [_op("rz", q, [_PI / 4])],
    "tdg": lambda q, p: [_op("rz", q, [-_PI / 4])],
    "p": lambda q, p: [_op("rz", q, p)],
    "rx": lambda q, p: [_op("h", q), _op("rz", q, p), _op("h", q)],
    "ry": lambda q, p: [_op("sdg", q), _op("rx", q, p), _op("s", q)],
    "cz": lambda q, p: [_op("h", [q[1]]), _op("cx", q), _op("h", [q[1]])],
    "swap": lambda q, p: [_op("cx", q), _op("cx", q[::-1]), _op("cx", q)],
    "cp": lambda q, p: [_op("p", [q[0]], [p[0] / 2]), _op("cx", q), _op("p", [q[1]], [-p[0] / 2]), _op("cx", q),
                        _op("p", [q[1]], [p[0] / 2])],
    # Nielsen & Chuang, Fig. 4.9: the Toffoli in six CNOTs and single-qubit gates.
    "ccx": lambda q, p: [
        _op("h", [q[2]]), _op("cx", [q[1], q[2]]), _op("tdg", [q[2]]), _op("cx", [q[0], q[2]]), _op("t", [q[2]]),
        _op("cx", [q[1], q[2]]), _op("tdg", [q[2]]), _op("cx", [q[0], q[2]]), _op("t", [q[1]]), _op("t", [q[2]]),
        _op("h", [q[2]]), _op("cx", [q[0], q[1]]), _op("t", [q[0]]), _op("tdg", [q[1]]), _op("cx", [q[0], q[1]])],
}


def rebase(ops: list[dict]) -> list[dict]:
    """Gate-by-gate translation into BASIS, with no optimisation at all: the baseline every compiler must beat."""
    out: list[dict] = []
    for op in ops:
        if op["gate"] in BASIS:
            out.append(op)
        else:
            out.extend(rebase(_RULES[op["gate"]](op["targets"], op.get("params") or [])))
    return out


def source_circuit(params: dict) -> list[dict]:
    """The circuit an instance compiles, as an op list."""
    kind, n = params["kind"], params["n"]
    ops: list[dict] = []
    if kind == "qft":
        for j in reversed(range(n)):
            ops.append(_op("h", [j]))
            for k in reversed(range(j)):
                ops.append(_op("cp", [k, j], [_PI / 2 ** (j - k)]))
        ops += [_op("swap", [i, n - 1 - i]) for i in range(n // 2)]
    elif kind == "grover":                                   # one iteration marking `marked`, n = 3
        zeros = [q for q in range(n) if not (params["marked"] >> q) & 1]
        mcz = [_op("h", [n - 1]), _op("ccx", [0, 1, n - 1]), _op("h", [n - 1])]
        ops += [_op("h", [q]) for q in range(n)]
        ops += [_op("x", [q]) for q in zeros] + mcz + [_op("x", [q]) for q in zeros]
        ops += [_op("h", [q]) for q in range(n)] + [_op("x", [q]) for q in range(n)] + mcz
        ops += [_op("x", [q]) for q in range(n)] + [_op("h", [q]) for q in range(n)]
    elif kind == "ghz-redundant":                            # GHZ with gates that cancel, as careless code writes
        ops += [_op("h", [0]), _op("t", [0]), _op("tdg", [0]), _op("cx", [1, 2]), _op("cx", [1, 2])]
        for i in range(n - 1):
            ops.append(_op("cx", [i, i + 1]))
            ops += [_op("rz", [i + 1], [0.4]), _op("rz", [i + 1], [-0.4])] if i % 2 == 0 else \
                [_op("x", [i + 1]), _op("x", [i + 1])]
        ops += [_op("cz", [n - 2, n - 1]), _op("cz", [n - 2, n - 1]), _op("h", [n - 1]), _op("h", [n - 1])]
    elif kind == "adder":                                    # full adder: a, b in superposition, carry-in 1
        ops += [_op("h", [0]), _op("h", [1]), _op("x", [2])]
        ops += [_op("ccx", [0, 1, 3]), _op("cx", [0, 1]), _op("ccx", [1, 2, 3]), _op("cx", [1, 2]), _op("cx", [0, 1])]
    elif kind == "random":
        rng = make_rng(params["seed"])
        one, two = ("h", "x", "s", "t", "sdg", "rz", "rx"), ("cx", "cz", "cp")
        for _ in range(params["gates"]):
            if rng.random() < 0.4:
                a, b = rng.choice(n, size=2, replace=False)
                g = two[rng.integers(len(two))]
                ops.append(_op(g, [a, b], [round(float(rng.uniform(0, 2 * _PI)), 6)] if g == "cp" else []))
            else:
                g = one[rng.integers(len(one))]
                q = int(rng.integers(n))
                ops.append(_op(g, [q], [round(float(rng.uniform(0, 2 * _PI)), 6)] if g in ("rz", "rx") else []))
    else:
        raise ValueError(f"unknown circuit kind {kind!r}")
    return ops


@register_problem
class Compilation(Problem):
    id = "compilation"
    category = "compilation"
    live_capable = False  # compilers run offline; the result is committed
    title = {"en": "Circuit compilation", "es": "Compilación de circuitos"}
    concept = {
        "en": (
            "An algorithm is written in convenient gates; a device runs a small native set, here {CX, RZ, SX, X}. "
            "Translating gate by gate is always correct but wasteful. An optimising compiler resynthesises the "
            "circuit, cancels redundant gates and folds trailing swaps into a relabelling of the output wires, "
            "while every result is checked to be the same unitary up to a global phase. Two-qubit gates dominate "
            "the error of today's devices, so their count is the metric. This is classical software serving "
            "quantum hardware: no quantum advantage is claimed, only the cost a good compiler saves."
        ),
        "es": (
            "Un algoritmo se escribe con compuertas cómodas; un dispositivo ejecuta un conjunto nativo pequeño, "
            "aquí {CX, RZ, SX, X}. Traducir compuerta a compuerta siempre es correcto pero derrochador. Un "
            "compilador optimizador resintetiza el circuito, cancela compuertas redundantes y convierte los "
            "intercambios finales en un reetiquetado de los cables de salida, y cada resultado se verifica como el "
            "mismo unitario salvo una fase global. Las compuertas de dos qubits dominan el error de los "
            "dispositivos actuales, así que su conteo es la métrica. Es software clásico al servicio del hardware "
            "cuántico: no se afirma ventaja cuántica, solo el costo que un buen compilador ahorra."
        ),
    }
    metric = {"en": "two-qubit gates after compilation", "es": "compuertas de dos qubits tras compilar"}
    references = [
        {"label": "Sivarajah et al., t|ket⟩: a retargetable compiler for NISQ devices, Quantum Sci. Technol. 6 "
                  "(2021)",
         "doi": "10.1088/2058-9565/ab8e92"},
        {"label": "Javadi-Abhari et al., Quantum computing with Qiskit (2024), arXiv:2405.08810",
         "url": "https://arxiv.org/abs/2405.08810"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010), §4.3 and Fig. 4.9",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("comp-qft3", "QFT on 3 qubits", "QFT de 3 qubits", {"kind": "qft", "n": 3}),
            ("comp-qft4", "QFT on 4 qubits", "QFT de 4 qubits", {"kind": "qft", "n": 4}),
            ("comp-grover3", "One Grover iteration, 3 qubits", "Una iteración de Grover, 3 qubits",
             {"kind": "grover", "n": 3, "marked": 5}),
            ("comp-ghz5", "GHZ-5 with redundant gates", "GHZ-5 con compuertas redundantes",
             {"kind": "ghz-redundant", "n": 5}),
            ("comp-adder", "Full adder (two Toffolis)", "Sumador completo (dos Toffoli)", {"kind": "adder", "n": 4}),
            ("comp-random4", "Random 4-qubit circuit, 30 gates", "Circuito aleatorio de 4 qubits, 30 compuertas",
             {"kind": "random", "n": 4, "gates": 30, "seed": 7}),
        ]
        out = []
        for iid, en, es, params in defs:
            src = source_circuit(params)
            m, r = metrics(src, params["n"]), metrics(rebase(src), params["n"])
            out.append(Instance(
                iid, {"en": en, "es": es}, params,
                {"en": f"{m['gates']} source gates ({m['two_qubit']} on two or more qubits); translated gate by gate "
                       f"into {{CX, RZ, SX, X}} it takes {r['two_qubit']} CX and depth {r['depth']}.",
                 "es": f"{m['gates']} compuertas fuente ({m['two_qubit']} sobre dos o más qubits); traducido compuerta "
                       f"a compuerta a {{CX, RZ, SX, X}} toma {r['two_qubit']} CX y profundidad {r['depth']}."},
            ))
        return out
