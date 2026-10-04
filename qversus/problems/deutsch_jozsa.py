"""Deutsch–Jozsa, decide constant vs balanced in one query.

Promised that f:{0,1}^n→{0,1} is either constant (same output for all inputs) or balanced (0 on exactly
half the inputs), Deutsch–Jozsa decides which with a SINGLE quantum oracle query. Deterministically,
classically you may need 2^{n-1}+1 queries (just over half the inputs) to be certain, an exponential
query-complexity gap. The honest nuance (the comparison panel says it): it is an oracle-model, query-count
advantage; at these sizes the classical decision is still instant.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class DeutschJozsa(Problem):
    id = "deutsch-jozsa"
    category = "oracle-algorithms"
    live_capable = True
    title = {"en": "Deutsch–Jozsa, constant vs balanced", "es": "Deutsch–Jozsa, constante vs balanceada"}
    concept = {
        "en": (
            "An oracle hides a function f that is promised constant or balanced. Deutsch–Jozsa puts the "
            "input register in uniform superposition with the answer qubit in |−⟩, queries the oracle once "
            "(phase kickback stamps (−1)^{f(x)}), and a final layer of Hadamards interferes the branches: "
            "the input register collapses to all-zeros iff f is constant, and to something non-zero iff f "
            "is balanced. One quantum query decides it; a deterministic classical algorithm may need "
            "2^{n-1}+1."
        ),
        "es": (
            "Un oráculo oculta una función f que se promete constante o balanceada. Deutsch–Jozsa pone el "
            "registro de entrada en superposición uniforme con el qubit de respuesta en |−⟩, consulta el "
            "oráculo una vez (el phase kickback marca (−1)^{f(x)}), y una capa final de Hadamards interfiere "
            "las ramas: el registro de entrada colapsa a todo-ceros si f es constante, y a algo no nulo si f "
            "es balanceada. Una consulta cuántica lo decide; un algoritmo clásico determinista puede "
            "necesitar 2^{n-1}+1."
        ),
    }
    metric = {"en": "constant-or-balanced verdict", "es": "veredicto constante-o-balanceada"}
    references = [
        {"label": "Deutsch & Jozsa, Rapid solution of problems by quantum computation, Proc. R. Soc. A 439 (1992)",
         "doi": "10.1098/rspa.1992.0167"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    @staticmethod
    def evaluate(params: dict, x: int) -> int:
        """The oracle f(x). constant → fixed value; balanced → parity of (secret AND x), secret ≠ 0."""
        if params["kind"] == "constant":
            return params["value"]
        n, s = params["n"], params["secret"]
        bits = [(x >> i) & 1 for i in range(n)]
        return sum(int(s[i]) & bits[i] for i in range(n)) % 2

    def instances(self) -> list[Instance]:
        defs = [
            ("dj-const0-3", "constant f=0 (n=3)", {"n": 3, "kind": "constant", "value": 0}),
            ("dj-const1-3", "constant f=1 (n=3)", {"n": 3, "kind": "constant", "value": 1}),
            ("dj-bal-101", "balanced s=101 (n=3)", {"n": 3, "kind": "balanced", "secret": "101"}),
            ("dj-bal-parity", "balanced full parity (n=3)", {"n": 3, "kind": "balanced", "secret": "111"}),
            ("dj-const0-4", "constant f=0 (n=4)", {"n": 4, "kind": "constant", "value": 0}),
            ("dj-bal-1011", "balanced s=1011 (n=4)", {"n": 4, "kind": "balanced", "secret": "1011"}),
        ]
        out = []
        for iid, label, params in defs:
            kind = "constant" if params["kind"] == "constant" else "balanced"
            worst = 2 ** (params["n"] - 1) + 1
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"f is {kind}, 1 quantum query vs up to {worst} classical (worst case).",
                 "es": f"f es {kind}, 1 consulta cuántica vs hasta {worst} clásicas (peor caso)."},
            ))
        return out
