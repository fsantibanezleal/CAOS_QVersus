"""Single-qubit gates & the Bloch sphere, the foundation of everything.

A qubit's pure state is a point on the Bloch sphere; single-qubit gates are rotations of that sphere.
X/Y/Z are π-rotations about the axes, H maps the poles to the equator (superposition), S and T add phase
(rotations about Z), and RX/RY/RZ are continuous rotations. qversus walks |0⟩ through these gates and shows
the Bloch vector move. The honest framing: this is the substrate, not an advantage, one qubit can sit
anywhere on the sphere, but a measurement still yields a single classical bit (Holevo's bound), so a lone
qubit stores no more classical information than a bit. Superposition and phase only pay off through
interference across many qubits (the later cases).
"""

from __future__ import annotations

import math

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

PI = math.pi


@register_problem
class SingleQubit(Problem):
    id = "single-qubit"
    category = "fundamentals"
    live_capable = True
    title = {"en": "Single-qubit gates & the Bloch sphere", "es": "Compuertas de un qubit y la esfera de Bloch"}
    concept = {
        "en": (
            "Every pure qubit state is a point on the Bloch sphere; the gates are rotations of it. X flips "
            "|0⟩↔|1⟩ (a π-rotation about X); H takes a pole to the equator (superposition); Z, S and T are "
            "Z-rotations that add phase (visible only once you're off the poles); RX/RY/RZ rotate by any "
            "angle. Step |0⟩ through a gate and watch the Bloch vector move. It is the foundation of "
            "everything later, but not, by itself, an advantage: a measurement collapses the qubit to one "
            "classical bit, and a single qubit stores no more classical information than a bit (Holevo). "
            "The richness of the sphere only becomes powerful through interference across many qubits."
        ),
        "es": (
            "Todo estado puro de un qubit es un punto en la esfera de Bloch; las compuertas son rotaciones de "
            "ella. X voltea |0⟩↔|1⟩ (rotación π sobre X); H lleva un polo al ecuador (superposición); Z, S y "
            "T son rotaciones sobre Z que agregan fase (visible solo fuera de los polos); RX/RY/RZ rotan "
            "cualquier ángulo. Lleva |0⟩ por una compuerta y observa moverse el vector de Bloch. Es la base de "
            "todo lo que sigue, pero no, por sí mismo, una ventaja: una medición colapsa el qubit a un bit "
            "clásico, y un qubit no guarda más información clásica que un bit (Holevo). La riqueza de la "
            "esfera solo se vuelve poderosa por interferencia entre muchos qubits."
        ),
    }
    metric = {"en": "Bloch vector of the prepared state", "es": "vector de Bloch del estado preparado"}
    references = [
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information, §1.3 (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
        {"label": "Holevo, Bounds for the quantity of information transmitted by a quantum channel (1973)",
         "url": "http://mi.mathnet.ru/eng/ppi903"},
    ]

    def instances(self) -> list[Instance]:
        # each variant = a short gate sequence on |0⟩; the trace shows the Bloch vector after each gate
        defs = [
            ("sq-x", "X · bit-flip → |1⟩", [["x"]]),
            ("sq-h", "H · superposition → |+⟩", [["h"]]),
            ("sq-hz", "H, Z · phase-flip → |−⟩", [["h"], ["z"]]),
            ("sq-hs", "H, S · S-phase → |+i⟩", [["h"], ["s"]]),
            ("sq-ry", "RY(π/3) · partial rotation", [["ry", PI / 3]]),
            ("sq-rx", "RX(π/2) · X-rotation → −Y", [["rx", PI / 2]]),
        ]
        out = []
        for iid, label, gates in defs:
            out.append(Instance(
                iid, {"en": label, "es": label}, {"n": 1, "gates": gates},
                {"en": f"Apply {label.split(' · ')[0]} to |0⟩, watch the Bloch vector.",
                 "es": f"Aplica {label.split(' · ')[0]} a |0⟩, observar el vector de Bloch."},
            ))
        return out
