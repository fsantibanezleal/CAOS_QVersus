"""Quantum error correction, the repetition (bit-flip) code, and the below-threshold idea.

Unlike error *mitigation* (which only reduces bias and does not scale), error *correction* encodes one
logical qubit in many physical qubits, measures stabilizers to detect errors, and decodes them, and it
*scales*: below a noise threshold, adding more physical qubits makes the logical qubit BETTER. The
repetition code (the quantum version of the classical "repeat the bit 3×") protects against bit-flips. qversus
runs the real QEC toolchain, Stim (Clifford circuit + sampling) + PyMatching (minimum-weight matching
decoder), for distances 3 and 5 across noise levels, and compares the encoded logical error to an
unprotected qubit. You can watch a bigger code beat a smaller one below threshold (the miniature of Google
Willow's 2024 result), and stay honest that this is one logical qubit, ~8 orders of magnitude of physical
qubits from breaking crypto.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class QECRepetition(Problem):
    id = "qec-repetition"
    category = "noise-and-qec"
    live_capable = False  # Monte-Carlo sampling + decoding → precompute
    title = {"en": "QEC, repetition (bit-flip) code", "es": "QEC, código de repetición (bit-flip)"}
    concept = {
        "en": (
            "The repetition code encodes one logical qubit in d physical qubits and corrects bit-flips by "
            "measuring parity (Z₀Z₁, Z₁Z₂, …) stabilizers and majority-decoding. We run the real QEC stack, "
            "Stim simulates the noisy stabilizer circuit, PyMatching decodes the syndromes, for distance 3 "
            "and 5 over several noise rates, and compare the encoded logical error to an unprotected qubit. "
            "Below a noise threshold the logical error drops and a larger code beats a smaller one, adding "
            "qubits makes the logical qubit better. That is the whole premise of fault tolerance, and the "
            "miniature of Google's Willow below-threshold result; the honest caveat is that this is one "
            "logical qubit, vastly short of the thousands needed for anything useful."
        ),
        "es": (
            "El código de repetición codifica un qubit lógico en d qubits físicos y corrige bit-flips "
            "midiendo estabilizadores de paridad (Z₀Z₁, Z₁Z₂, …) y decodificando por mayoría. Ejecutamos el "
            "stack real de QEC, Stim simula el circuito ruidoso de estabilizadores, PyMatching decodifica "
            "los síndromes, para distancia 3 y 5 con varias tasas de ruido, y comparamos el error LÓGICO "
            "codificado con un qubit sin proteger. Bajo un umbral de ruido el error lógico baja Y un código "
            "más grande supera a uno más chico, agregar qubits mejora el qubit lógico. Esa es la premisa "
            "de la tolerancia a fallos, y la miniatura del resultado below-threshold de Willow de Google; la "
            "salvedad honesta es que esto es un qubit lógico, lejísimos de los miles necesarios para algo útil."
        ),
    }
    metric = {"en": "logical error rate", "es": "tasa de error lógico"}
    references = [
        {"label": "Google Quantum AI, Quantum error correction below the surface code threshold (2024)",
         "url": "https://arxiv.org/abs/2408.13687"},
        {"label": "Gidney, Stim: a fast stabilizer circuit simulator (2021)",
         "doi": "10.22331/q-2021-07-06-497"},
    ]

    def instances(self) -> list[Instance]:
        # pair distance-3 vs distance-5 at three noise rates: see distance help below threshold
        defs = [(3, 0.05), (5, 0.05), (3, 0.1), (5, 0.1), (3, 0.2), (5, 0.2)]
        out = []
        for d, p in defs:
            out.append(Instance(
                f"rep-d{d}-p{p}", {"en": f"distance {d}, p={p}", "es": f"distancia {d}, p={p}"},
                {"distance": d, "p": p, "rounds": d},
                {"en": f"d={d} repetition code, depolarizing p={p}, encoded logical error vs unprotected.",
                 "es": f"código de repetición d={d}, despolarizante p={p}, error lógico codificado vs sin proteger."},
            ))
        return out
