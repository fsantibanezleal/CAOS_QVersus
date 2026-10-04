"""Simon's algorithm, find a hidden period of a 2-to-1 function.

Given f:{0,1}ⁿ→{0,1}ⁿ promised 2-to-1 with a hidden period s (f(x)=f(x⊕s) for all x), recover s. Simon's
algorithm needs O(n) quantum queries; any classical algorithm needs ~O(2^{n/2}) (birthday-collision). It is
the first problem in qversus with a genuine *exponential* query separation, and it is honestly a hybrid: the
quantum circuit samples bit-strings y with y·s = 0 (mod 2), and a classical GF(2) solve over those y's
recovers s. The honest nuance stands: at these tiny n the classical collision search is still instant.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class Simon(Problem):
    id = "simon"
    category = "oracle-algorithms"
    live_capable = False  # needs many shots + a classical GF(2) post-process → precompute
    title = {"en": "Simon, hidden period (exponential separation)",
             "es": "Simon, período oculto (separación exponencial)"}
    concept = {
        "en": (
            "An oracle hides a 2-to-1 function with period s: f(x)=f(x⊕s). Simon's circuit entangles an "
            "input register with f's output, and a final layer of Hadamards makes the input register yield, "
            "on each run, a random string y with y·s = 0 (mod 2). About n−1 independent y's pin down s by "
            "Gaussian elimination over GF(2), O(n) quantum queries. Classically you must hunt for a "
            "collision f(x₁)=f(x₂), needing ~2^{n/2} queries (birthday bound). This is the first provably "
            "exponential quantum query advantage, the conceptual ancestor of Shor."
        ),
        "es": (
            "Un oráculo oculta una función 2-a-1 con período s: f(x)=f(x⊕s). El circuito de Simon entrelaza "
            "un registro de entrada con la salida de f, y una capa final de Hadamards hace que el registro "
            "de entrada dé, en cada ejecución, una cadena aleatoria y con y·s = 0 (mod 2). Unas n−1 cadenas y "
            "independientes determinan s por eliminación gaussiana sobre GF(2), O(n) consultas. "
            "Clásicamente hay que buscar una colisión f(x₁)=f(x₂), con ~2^{n/2} consultas (cota del "
            "cumpleaños). Es la primera ventaja cuántica exponencial demostrable, el ancestro de Shor."
        ),
    }
    metric = {"en": "recovered period s", "es": "período recuperado s"}
    references = [
        {"label": "Simon, On the power of quantum computation, SIAM J. Comput. 26(5) (1997)",
         "doi": "10.1137/S0097539796298637"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    @staticmethod
    def evaluate(params: dict, x: int) -> int:
        """f(x) for the period-s oracle: f(x)=x if x_j=0 else x⊕s, where j = least-significant set bit of s.
        This is 2-to-1 with f(x)=f(x⊕s). `s` is a bit-string with s[i] = bit of qubit i (LSB = qubit 0)."""
        n, s = params["n"], params["secret"]
        sval = sum(int(s[i]) << i for i in range(n))
        j = min(i for i in range(n) if s[i] == "1")
        xj = (x >> j) & 1
        return x ^ (sval if xj else 0)

    def instances(self) -> list[Instance]:
        defs = [
            ("simon-2-11", "s=11 (n=2)", {"n": 2, "secret": "11"}),
            ("simon-3-001", "s=001 (n=3)", {"n": 3, "secret": "001"}),
            ("simon-3-101", "s=101 (n=3)", {"n": 3, "secret": "101"}),
            ("simon-3-110", "s=110 (n=3)", {"n": 3, "secret": "110"}),
            ("simon-3-011", "s=011 (n=3)", {"n": 3, "secret": "011"}),
            ("simon-3-111", "s=111 (n=3)", {"n": 3, "secret": "111"}),
        ]
        out = []
        for iid, label, params in defs:
            n = params["n"]
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"period {params['secret']} ({2 * n} qubits), O(n) quantum vs ~2^(n/2) classical.",
                 "es": f"período {params['secret']} ({2 * n} qubits), O(n) cuántico vs ~2^(n/2) clásico."},
            ))
        return out
