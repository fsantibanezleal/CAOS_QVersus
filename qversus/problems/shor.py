"""Shor's algorithm (toy: factor 15), order-finding via QPE, and the headline honesty case.

Shor factors N by finding the multiplicative order r of a random base a mod N (the smallest r with
aʳ ≡ 1), using quantum phase estimation on the modular-multiplication unitary U_a|y⟩=|a·y mod N⟩. From r,
classical gcd's give the factors. qversus runs the real order-finding (a genuine 16-dim modular-mult unitary,
not a pre-encoded answer) for N=15 across several bases. The honesty payload is huge: factoring 15 is
trivial classically, and breaking RSA-2048 needs ~10⁶ noisy physical qubits + full fault tolerance
(Gidney 2025), 3–4 orders of magnitude beyond today. "Quantum will break encryption soon" is the claim
this case is built to puncture.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class Shor(Problem):
    id = "shor"
    category = "flagship-algorithms"
    live_capable = False  # 8 qubits + continued-fractions post-process → precompute
    title = {"en": "Shor (toy: factor 15)", "es": "Shor (juguete: factorizar 15)"}
    concept = {
        "en": (
            "Shor reduces factoring N to finding the order r of a base a (smallest r with aʳ ≡ 1 mod N). "
            "Quantum phase estimation on the modular-multiplication unitary U_a|y⟩=|a·y mod N⟩ yields a "
            "phase s/r; continued fractions recover r; then gcd(a^{r/2}±1, N) gives the factors. We run the "
            "real order-finding for N=15 over several bases. It works, but factoring 15 is trivial "
            "classically, and a cryptographically relevant Shor (RSA-2048) needs on the order of a MILLION "
            "noisy physical qubits and full fault tolerance, three-to-four orders of magnitude beyond "
            "today's ~100-qubit machines. This case exists to puncture 'quantum breaks encryption soon'."
        ),
        "es": (
            "Shor reduce factorizar N a hallar el orden r de una base a (el menor r con aʳ ≡ 1 mod N). La "
            "estimación cuántica de fase sobre el unitario de multiplicación modular U_a|y⟩=|a·y mod N⟩ da "
            "una fase s/r; las fracciones continuas recuperan r; luego gcd(a^{r/2}±1, N) da los factores. "
            "Ejecutamos el order-finding real para N=15 con varias bases. Funciona, pero factorizar 15 es "
            "trivial clásicamente, y un Shor criptográficamente relevante (RSA-2048) necesita del orden de "
            "un millón de qubits físicos ruidosos y tolerancia a fallos completa, tres-a-cuatro órdenes de "
            "magnitud más allá de las máquinas de ~100 qubits de hoy. Este caso existe para desinflar el "
            "'lo cuántico romperá el cifrado pronto'."
        ),
    }
    metric = {"en": "factors of N", "es": "factores de N"}
    references = [
        {"label": "Shor, Polynomial-time algorithms for prime factorization … (1997)",
         "doi": "10.1137/S0097539795293172"},
        {"label": "Gidney, How to factor 2048-bit RSA integers with less than a million noisy qubits (2025)",
         "url": "https://arxiv.org/abs/2505.15917"},
    ]

    @staticmethod
    def order(a: int, N: int) -> int:
        r, x = 1, a % N
        while x != 1:
            x = (x * a) % N
            r += 1
        return r

    def instances(self) -> list[Instance]:
        N = 15
        bases = [2, 4, 7, 8, 11, 13]   # all give an even order with a non-trivial gcd (a=14 fails: 14≡−1)
        out = []
        for a in bases:
            r = self.order(a, N)
            out.append(Instance(
                f"shor-15-a{a}", {"en": f"N=15, base a={a}", "es": f"N=15, base a={a}"},
                {"N": N, "a": a, "t": 4},
                {"en": f"order r={r}; QPE → phase s/{r} → continued fractions → factors of 15.",
                 "es": f"orden r={r}; QPE → fase s/{r} → fracciones continuas → factores de 15."},
            ))
        return out
