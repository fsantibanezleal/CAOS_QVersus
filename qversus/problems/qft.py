"""Quantum Fourier Transform, the flagship subroutine (and an honesty lesson).

The QFT maps a basis state |k⟩ to a phase-ramp superposition (1/√N) Σ_j e^{2πi kj/N} |j⟩, the quantum
analogue of the discrete Fourier transform. It applies the transform in O(n²) gates vs the classical
FFT's O(N log N) = O(n·2ⁿ) operations: exponentially cheaper to *apply*. But measurement collapses the
output to a single sample, you CANNOT read out the 2ⁿ Fourier amplitudes. That is exactly why the QFT is
a *subroutine* (inside phase estimation / Shor), not a standalone speedup: the classical FFT, by contrast,
hands you the full readable spectrum. qversus validates the QFT against the analytic DFT and shows this honestly.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class QFT(Problem):
    id = "qft"
    category = "flagship-algorithms"
    live_capable = True
    title = {"en": "Quantum Fourier Transform", "es": "Transformada cuántica de Fourier"}
    concept = {
        "en": (
            "The QFT is the quantum discrete Fourier transform: it sends |k⟩ to a uniform superposition "
            "with a phase ramp e^{2πi kj/N}. Built from Hadamards and a ladder of controlled-phase "
            "rotations (plus output swaps), it uses only O(n²) gates, exponentially fewer than the "
            "classical FFT's O(n·2ⁿ). The catch: a measurement returns one sample, so you cannot extract "
            "the full transformed amplitudes. The QFT is therefore the engine *inside* phase estimation and "
            "Shor, not a way to compute a readable spectrum faster, that is what the classical FFT is for."
        ),
        "es": (
            "La QFT es la transformada de Fourier discreta cuántica: envía |k⟩ a una superposición uniforme "
            "con una rampa de fase e^{2πi kj/N}. Construida con Hadamards y una escalera de rotaciones de "
            "fase controladas (más swaps de salida), usa solo O(n²) compuertas, exponencialmente menos que "
            "el O(n·2ⁿ) de la FFT clásica. El truco: una medición devuelve una sola muestra, así que no "
            "puedes extraer todas las amplitudes transformadas. Por eso la QFT es el motor *dentro* de la "
            "estimación de fase y de Shor, no una forma de obtener un espectro legible más rápido, eso lo "
            "hace la FFT clásica."
        ),
    }
    metric = {"en": "Fourier transform of the input state", "es": "transformada de Fourier del estado"}
    references = [
        {"label": "Coppersmith, An approximate Fourier transform useful in quantum factoring (1994/2002)",
         "url": "https://arxiv.org/abs/quant-ph/0201067"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("qft-3-k0", "n=3, input |000⟩", {"n": 3, "k": 0}),
            ("qft-3-k1", "n=3, input |001⟩", {"n": 3, "k": 1}),
            ("qft-3-k4", "n=3, input |100⟩", {"n": 3, "k": 4}),
            ("qft-3-k5", "n=3, input |101⟩", {"n": 3, "k": 5}),
            ("qft-4-k1", "n=4, input |0001⟩", {"n": 4, "k": 1}),
            ("qft-4-k6", "n=4, input |0110⟩", {"n": 4, "k": 6}),
        ]
        out = []
        for iid, label, params in defs:
            n = params["n"]
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"QFT of |{params['k']}⟩ on {n} qubits → uniform |amp|²=1/{2 ** n} with a phase ramp.",
                 "es": f"QFT de |{params['k']}⟩ en {n} qubits → uniforme |amp|²=1/{2 ** n} con rampa de fase."},
            ))
        return out
