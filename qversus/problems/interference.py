"""Phase & interference, the single-qubit interferometer (H · P(φ) · H).

Interference is the actual engine of quantum computing: amplitudes, not probabilities, add, and they can
cancel. The cleanest demonstration is a one-qubit Mach–Zehnder: H splits |0⟩ into two paths, a phase gate
P(φ) delays one path, and a second H recombines them. The probability of measuring 0 is cos²(φ/2): at φ=0
the paths add (P0=1, fully constructive); at φ=π they cancel (P0=0, fully destructive). Sweeping φ traces
the interference fringe. The honest framing: a classical wave (light in an optical Mach–Zehnder) produces
the exact same cos²(φ/2) intensity, so interference itself is not uniquely quantum. What IS quantum is that
it happens for single particles (one photon interferes with itself, in probability amplitude), and that this
amplitude interference is the resource every quantum algorithm (Grover, QFT, Deutsch–Jozsa) steers to make
wrong answers cancel and right answers add. Alone, it is not a computational advantage.
"""

from __future__ import annotations

import math

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

PI = math.pi


@register_problem
class Interference(Problem):
    id = "interference"
    category = "fundamentals"
    live_capable = True
    title = {"en": "Phase & interference", "es": "Fase e interferencia"}
    concept = {
        "en": (
            "Amplitudes, not probabilities, add, and they can cancel. The one-qubit Mach–Zehnder "
            "H · P(φ) · H makes it visible: H splits |0⟩ into two paths, the phase gate P(φ) delays one, and "
            "the second H recombines them, giving P(measure 0) = cos²(φ/2). At φ=0 the paths interfere "
            "constructively (P0=1); at φ=π they cancel completely (P0=0). Sweep φ and the probability "
            "oscillates, the interference fringe. A classical wave (an optical Mach–Zehnder) gives the same "
            "cos²(φ/2), so interference is not by itself quantum; what is quantum is that it happens for a "
            "single particle's probability amplitude, and steering that interference so wrong answers cancel "
            "is exactly how Grover, the QFT and the oracle algorithms work."
        ),
        "es": (
            "Las amplitudes, no las probabilidades, se suman, y pueden cancelarse. El Mach–Zehnder de un "
            "qubit H · P(φ) · H lo hace visible: H divide |0⟩ en dos caminos, la compuerta de fase P(φ) "
            "retrasa uno, y el segundo H los recombina, dando P(medir 0) = cos²(φ/2). En φ=0 los caminos "
            "interfieren constructivamente (P0=1); en φ=π se cancelan por completo (P0=0). Barre φ y la "
            "probabilidad oscila, la franja de interferencia. Una onda clásica (un Mach–Zehnder óptico) da "
            "el mismo cos²(φ/2), así que la interferencia no es por sí sola cuántica; lo cuántico es que "
            "ocurre para la amplitud de probabilidad de una sola partícula, y dirigir esa interferencia para "
            "que las respuestas erróneas se cancelen es exactamente cómo funcionan Grover, la QFT y los "
            "algoritmos de oráculo."
        ),
    }
    metric = {"en": "P(0) = cos²(φ/2), the interference fringe", "es": "P(0) = cos²(φ/2), la franja de interferencia"}
    references = [
        {"label": "Feynman, Leighton & Sands, The Feynman Lectures on Physics, Vol. III, ch. 1 (1965)",
         "url": "https://www.feynmanlectures.caltech.edu/III_01.html"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information, §1.4 (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        # H · P(φ) · H on |0⟩; sweep the relative phase φ to trace the interference fringe P0 = cos²(φ/2).
        defs = [
            ("itf-0", "φ = 0 · fully constructive", 0.0),
            ("itf-pi4", "φ = π/4", PI / 4),
            ("itf-pi2", "φ = π/2 · half", PI / 2),
            ("itf-2pi3", "φ = 2π/3", 2 * PI / 3),
            ("itf-3pi4", "φ = 3π/4", 3 * PI / 4),
            ("itf-pi", "φ = π · fully destructive", PI),
        ]
        out = []
        for iid, label, phi in defs:
            p0 = math.cos(phi / 2) ** 2
            out.append(Instance(
                iid, {"en": label, "es": label}, {"n": 1, "phi": phi},
                {"en": f"{label}, recombine the two paths; P(0) = cos²(φ/2) = {p0:.3f}.",
                 "es": f"{label}, recombina los dos caminos; P(0) = cos²(φ/2) = {p0:.3f}."},
            ))
        return out
