"""Superposition, measurement statistics & the quantum RNG, true vs pseudo randomness.

A Hadamard on |0⟩ makes a 50/50 superposition; measuring it gives a random bit. Apply H to n qubits and
measure: you get uniform random n-bit numbers, the histogram filling out as shots accumulate, with Shannon
entropy n bits. A biased rotation RY(θ) tilts the coin. qversus samples these and compares to a classical
pseudo-random generator. The honest distinction: statistically the two are indistinguishable at this scale,
but quantum randomness is *fundamental* (from measurement collapse) and can be **certified**, while a PRNG
is deterministic given its seed. So the quantum advantage here is certifiable true randomness (useful for
cryptography), not better statistics, and note the committed trace fixes a seed for reproducibility, even
though real-hardware measurement would be irreducibly random.
"""

from __future__ import annotations

import math

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class QRNG(Problem):
    id = "qrng"
    category = "fundamentals"
    live_capable = True
    title = {"en": "Superposition & quantum RNG", "es": "Superposición y RNG cuántico"}
    concept = {
        "en": (
            "H|0⟩ = (|0⟩+|1⟩)/√2, a coin that is genuinely 50/50, and measuring it yields a random bit. "
            "Hadamard on n qubits gives a uniform superposition over all 2ⁿ strings; sampling fills a flat "
            "histogram with Shannon entropy n bits. A rotation RY(θ) makes a biased coin. We compare quantum "
            "sampling to a classical pseudo-random generator: statistically they match, but quantum "
            "randomness comes from measurement collapse, it is fundamental and certifiable, whereas a PRNG "
            "is fully deterministic from its seed. That certifiability (not better statistics) is the real "
            "quantum value, and it underlies quantum-secure random beacons."
        ),
        "es": (
            "H|0⟩ = (|0⟩+|1⟩)/√2, una moneda genuinamente 50/50, y medirla da un bit aleatorio. Hadamard en "
            "n qubits da una superposición uniforme sobre las 2ⁿ cadenas; muestrear llena un histograma plano "
            "con entropía de Shannon n bits. Una rotación RY(θ) hace una moneda sesgada. Comparamos el "
            "muestreo cuántico con un generador pseudoaleatorio clásico: estadísticamente coinciden, pero la "
            "aleatoriedad cuántica viene del colapso de la medición, es fundamental y certificable, mientras "
            "un PRNG es totalmente determinista desde su semilla. Esa certificabilidad (no mejores "
            "estadísticas) es el valor cuántico real, y sustenta los faros de aleatoriedad cuántico-seguros."
        ),
    }
    metric = {"en": "Shannon entropy (bits)", "es": "entropía de Shannon (bits)"}
    references = [
        {"label": "Herrero-Collantes & Garcia-Escartin, Quantum random number generators, Rev. Mod. Phys. (2017)",
         "doi": "10.1103/RevModPhys.89.015004"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("qrng-1", "1 qubit · H → 50/50", {"n": 1}),
            ("qrng-2", "2 qubits · uniform /4", {"n": 2}),
            ("qrng-3", "3 qubits · uniform /8", {"n": 3}),
            ("qrng-4", "4 qubits · uniform /16", {"n": 4}),
            ("qrng-bias30", "1 qubit · RY(π/3) biased coin", {"n": 1, "theta": math.pi / 3}),
            ("qrng-bias60", "1 qubit · RY(2π/3) biased coin", {"n": 1, "theta": 2 * math.pi / 3}),
        ]
        out = []
        for iid, label, params in defs:
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"Sample {label.split(' · ')[0]}, uniform entropy n bits (or less if biased).",
                 "es": f"Muestrea {label.split(' · ')[0]}, entropía uniforme n bits (o menos si está sesgado)."},
            ))
        return out
