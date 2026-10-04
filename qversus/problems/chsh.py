"""CHSH / Bell inequality, where quantum GENUINELY beats classical (and where it doesn't).

Two parties share an entangled pair and each measures in one of two settings. The CHSH correlator
S = E(a₀,b₀) + E(a₀,b₁) + E(a₁,b₀) − E(a₁,b₁) is bounded by |S| ≤ 2 for ANY local-hidden-variable
(classical) theory, but quantum mechanics reaches the Tsirelson bound |S| = 2√2 ≈ 2.83 with the right
angles on a Bell state. qversus computes S from the real quantum state across several angle settings. This is
the rare, honest case where quantum *does* beat classical, but it is a **nonlocality** advantage (ruling
out local realism; the basis of the 2022 Nobel Prize), NOT a computational speedup. It also shows the
necessary ingredient: a separable (unentangled) state cannot violate the bound.
"""

from __future__ import annotations

import math

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

PI = math.pi


@register_problem
class CHSH(Problem):
    id = "chsh"
    category = "entanglement"
    live_capable = True
    title = {"en": "CHSH / Bell inequality", "es": "Desigualdad CHSH / Bell"}
    concept = {
        "en": (
            "Share a Bell pair; Alice measures at angle a₀ or a₁, Bob at b₀ or b₁. The CHSH quantity "
            "S = E(a₀,b₀)+E(a₀,b₁)+E(a₁,b₀)−E(a₁,b₁) cannot exceed 2 for any classical (local-hidden-"
            "variable) theory, yet a Bell state with optimal angles reaches the Tsirelson bound 2√2 ≈ 2.83. "
            "Violating |S|≤2 rules out local realism, a real, experimentally confirmed quantum effect (2022 "
            "Nobel). But it is a foundational/nonlocality advantage, not a faster computation; and a "
            "separable state cannot violate the bound at all, so entanglement is the necessary ingredient."
        ),
        "es": (
            "Comparte un par de Bell; Alice mide en ángulo a₀ o a₁, Bob en b₀ o b₁. La cantidad CHSH "
            "S = E(a₀,b₀)+E(a₀,b₁)+E(a₁,b₀)−E(a₁,b₁) no puede superar 2 en ninguna teoría clásica (de "
            "variables ocultas locales), pero un estado de Bell con ángulos óptimos alcanza la cota de "
            "Tsirelson 2√2 ≈ 2.83. Violar |S|≤2 descarta el realismo local, un efecto cuántico real y "
            "confirmado experimentalmente (Nobel 2022). Pero es una ventaja fundacional/de no-localidad, no "
            "un cálculo más rápido; y un estado separable no puede violar la cota, así que el entrelazamiento "
            "es el ingrediente necesario."
        ),
    }
    metric = {"en": "CHSH value S (classical ≤ 2, quantum ≤ 2√2)", "es": "valor CHSH S (clásico ≤ 2, cuántico ≤ 2√2)"}
    references = [
        {"label": "Clauser, Horne, Shimony & Holt, Proposed experiment to test local hidden-variable theories (1969)",
         "doi": "10.1103/PhysRevLett.23.880"},
        {"label": "Aspect, Nobel Prize in Physics 2022, Bell inequality experiments",
         "url": "https://www.nobelprize.org/prizes/physics/2022/summary/"},
    ]

    def instances(self) -> list[Instance]:
        # angles (a0, a1, b0, b1) in radians; `entangled` toggles Bell vs product state.
        opt = (0.0, PI / 2, PI / 4, -PI / 4)
        defs = [
            ("chsh-optimal", "Bell, optimal angles → 2√2", opt, True),
            ("chsh-suboptimal", "Bell, sub-optimal angles", (0.0, PI / 2, PI / 6, -PI / 6), True),
            ("chsh-weak", "Bell, weak angles", (0.0, PI / 3, PI / 8, -PI / 8), True),
            ("chsh-aligned", "Bell, aligned bases → S=2", (0.0, 0.0, 0.0, PI / 2), True),
            ("chsh-rotated", "Bell, rotated optimal (still 2√2)", (PI / 8, PI / 8 + PI / 2, PI / 8 + PI / 4, PI / 8 - PI / 4), True),
            ("chsh-product", "Separable state (no entanglement)", opt, False),
        ]
        out = []
        for iid, label, angles, ent in defs:
            out.append(Instance(
                iid, {"en": label, "es": label},
                {"n": 2, "a0": angles[0], "a1": angles[1], "b0": angles[2], "b1": angles[3], "entangled": ent},
                {"en": f"{'Bell pair' if ent else 'product state'}, see whether S exceeds the classical 2.",
                 "es": f"{'par de Bell' if ent else 'estado producto'}, muestra si S supera el clásico 2."},
            ))
        return out
