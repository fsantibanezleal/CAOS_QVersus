"""Bernstein–Vazirani, recover a hidden bit-string from an oracle.

Given an oracle f(x) = s·x (mod 2) for a hidden string s, the Bernstein–Vazirani algorithm recovers s with
a SINGLE quantum oracle query via phase kickback + interference, where any classical algorithm needs n
queries (one per bit). It is the cleanest demonstration of a genuine, if oracle-model, quantum query
advantage. The honest nuance (the comparison panel makes it explicit): the advantage is in *query count*,
not wall-clock; at these sizes a classical computer answers instantly.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class BernsteinVazirani(Problem):
    id = "bernstein-vazirani"
    category = "oracle-algorithms"
    live_capable = True
    title = {"en": "Bernstein–Vazirani, 1 query vs n", "es": "Bernstein–Vazirani, 1 consulta vs n"}
    concept = {
        "en": (
            "A hidden string s is encoded in an oracle f(x) = s·x mod 2. Bernstein–Vazirani puts the input "
            "register in uniform superposition, the answer qubit in |−⟩, queries the oracle once, phase "
            "kickback stamps (−1)^{s·x} onto each branch, and a final layer of Hadamards interferes the "
            "branches so that measuring the input register yields s exactly. Classically you must query the "
            "oracle n times (once per bit). One quantum query vs n classical queries."
        ),
        "es": (
            "Una cadena oculta s se codifica en un oráculo f(x) = s·x mod 2. Bernstein–Vazirani pone el "
            "registro de entrada en superposición uniforme, el qubit de respuesta en |−⟩, consulta el "
            "oráculo una vez, el phase kickback marca (−1)^{s·x} en cada rama, y una capa final de "
            "Hadamards interfiere las ramas de modo que medir el registro de entrada da s exactamente. "
            "Clásicamente hay que consultar el oráculo n veces (una por bit). Una consulta cuántica vs n."
        ),
    }
    metric = {"en": "recovered hidden string", "es": "cadena oculta recuperada"}
    references = [
        {"label": "Bernstein & Vazirani, Quantum complexity theory, SIAM J. Comput. 26(5) (1997)",
         "doi": "10.1137/S0097539796300921"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    @staticmethod
    def oracle(secret: str, x: int) -> int:
        """f(x) = parity of (secret AND x), the classically queryable oracle. `secret[i]` is bit of qubit i."""
        n = len(secret)
        bits = [(x >> i) & 1 for i in range(n)]            # bit i of x ↔ qubit i
        return sum(int(secret[i]) & bits[i] for i in range(n)) % 2

    def instances(self) -> list[Instance]:
        secrets = [
            ("101", "bv-101"),
            ("0111", "bv-0111"),
            ("1101", "bv-1101"),
            ("11010", "bv-11010"),
            ("101101", "bv-101101"),
            ("111111", "bv-111111"),
        ]
        out = []
        for s, iid in secrets:
            out.append(Instance(
                iid, {"en": f"s = {s}", "es": f"s = {s}"},
                {"n": len(s), "secret": s},
                {"en": f"Hidden string {s} ({len(s)} bits), recovered in 1 query vs {len(s)} classical.",
                 "es": f"Cadena oculta {s} ({len(s)} bits), recuperada en 1 consulta vs {len(s)} clásicas."},
            ))
        return out
