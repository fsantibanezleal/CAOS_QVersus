"""Grover's search, amplitude amplification over an unstructured database.

Find a marked item in an unstructured set of N = 2ⁿ items. Grover needs ~(π/4)√(N/M) oracle queries
(M = number of marked items) vs the (N+1)/(M+1) a random classical scan needs on average. The famous quadratic
speedup, but honestly: it is
*quadratic, asymptotic*, and at the tiny n a laptop simulates exactly, the classical scan still wins on
wall-time. What it teaches beautifully is amplitude amplification: each iteration tips probability toward
the marked state, and over-rotating (too many iterations) tips it back.
"""

from __future__ import annotations

import math

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class Grover(Problem):
    id = "grover"
    category = "flagship-algorithms"
    live_capable = True
    title = {"en": "Grover, unstructured search", "es": "Grover, búsqueda no estructurada"}
    concept = {
        "en": (
            "Grover searches N = 2ⁿ unstructured items for the M marked ones. Start in uniform "
            "superposition; each Grover iteration applies the oracle (a phase flip on the marked states) "
            "then the diffuser (inversion about the mean), rotating amplitude toward the marked subspace. "
            "After ~(π/4)√(N/M) iterations a measurement returns a marked item with high probability, a "
            "quadratic speedup over a random classical scan, which needs (N+1)/(M+1) queries on average. Run "
            "too many iterations and you *over-rotate* past the target."
        ),
        "es": (
            "Grover busca entre N = 2ⁿ ítems no estructurados los M marcados. Parte en superposición "
            "uniforme; cada iteración de Grover aplica el oráculo (un cambio de fase en los estados "
            "marcados) y luego el difusor (inversión respecto a la media), rotando la amplitud hacia el "
            "subespacio marcado. Tras ~(π/4)√(N/M) iteraciones una medición devuelve un ítem marcado con "
            "alta probabilidad, un speedup cuadrático sobre un barrido clásico aleatorio, que necesita "
            "(N+1)/(M+1) consultas en promedio. Con demasiadas iteraciones te *pasas* del objetivo "
            "(sobre-rotación)."
        ),
    }
    metric = {"en": "marked item found", "es": "ítem marcado encontrado"}
    references = [
        {"label": "Grover, A fast quantum mechanical algorithm for database search, STOC '96 (1996)",
         "doi": "10.1145/237814.237866"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("grover-2-3", "n=2, mark |11⟩", {"n": 2, "marked": [3]}),
            ("grover-3-5", "n=3, mark |101⟩", {"n": 3, "marked": [5]}),
            ("grover-3-2", "n=3, mark |010⟩", {"n": 3, "marked": [2]}),
            ("grover-3-2marked", "n=3, mark |011⟩,|101⟩", {"n": 3, "marked": [3, 5]}),
            ("grover-4-10", "n=4, mark |1010⟩", {"n": 4, "marked": [10]}),
            ("grover-4-0", "n=4, mark |0000⟩", {"n": 4, "marked": [0]}),
        ]
        out = []
        for iid, label, params in defs:
            n, m = params["n"], len(params["marked"])
            N = 2 ** n
            k = self.optimal_iterations(N, m)
            expected = (N + 1) / (m + 1)
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"N={N}, M={m} marked: Grover's {k} iteration{'s' if k != 1 else ''} against the "
                       f"{expected:g} queries a random classical scan needs on average, (N+1)/(M+1).",
                 "es": f"N={N}, M={m} marcados: {k} iteración{'es' if k != 1 else ''} de Grover frente a las "
                       f"{expected:g} consultas que un barrido clásico aleatorio necesita en promedio, (N+1)/(M+1)."},
            ))
        return out

    @staticmethod
    def optimal_iterations(N: int, M: int) -> int:
        """⌊(π/4)√(N/M)⌋, at least one: the iteration count the Qiskit solver runs."""
        return max(1, math.floor(math.pi / 4 * math.sqrt(N / M)))
