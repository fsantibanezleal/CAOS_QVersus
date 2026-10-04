"""State preparation, the entanglement concept demos (Bell, GHZ, W).

A concept problem: the "answer" is the prepared statevector itself. It teaches superposition and the two
inequivalent kinds of tripartite entanglement (GHZ vs W). The honest framing (its classical baseline): at
2–4 qubits a classical computer writes down all 2^n amplitudes instantly, entanglement here is the
*concept*, not a computational advantage. Solvers build the same target on different frameworks.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class StatePrep(Problem):
    id = "state-prep"
    category = "entanglement"
    title = {"en": "State preparation & entanglement", "es": "Preparación de estados y entrelazamiento"}
    concept = {
        "en": (
            "Build canonical multi-qubit states from gates and watch entanglement appear. A Bell pair "
            "(H then CNOT) cannot be written as two independent qubits; GHZ and W are the two "
            "inequivalent species of three-qubit entanglement. Every solver prepares the same target, "
            "the point is the state, not the framework."
        ),
        "es": (
            "Construye estados multi-qubit canónicos a partir de compuertas y observa aparecer el "
            "entrelazamiento. Un par de Bell (H y luego CNOT) no se puede escribir como dos qubits "
            "independientes; GHZ y W son las dos especies no equivalentes de entrelazamiento de tres "
            "qubits. Cada solver prepara el mismo objetivo: lo importante es el estado, no el framework."
        ),
    }
    metric = {"en": "prepared state fidelity", "es": "fidelidad del estado preparado"}
    references = [
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
        {"label": "Dür, Vidal & Cirac, Three qubits can be entangled in two inequivalent ways (2000)",
         "doi": "10.1103/PhysRevA.62.062314"},
    ]

    def instances(self) -> list[Instance]:
        return [
            Instance("bell-phi-plus", {"en": "Bell Φ⁺", "es": "Bell Φ⁺"},
                     {"kind": "bell", "variant": "phi_plus", "n": 2},
                     {"en": "(|00⟩+|11⟩)/√2, the canonical entangled pair.",
                      "es": "(|00⟩+|11⟩)/√2, el par entrelazado canónico."}),
            Instance("bell-phi-minus", {"en": "Bell Φ⁻", "es": "Bell Φ⁻"},
                     {"kind": "bell", "variant": "phi_minus", "n": 2},
                     {"en": "(|00⟩−|11⟩)/√2, a relative phase flips the correlation.",
                      "es": "(|00⟩−|11⟩)/√2, una fase relativa invierte la correlación."}),
            Instance("bell-psi-plus", {"en": "Bell Ψ⁺", "es": "Bell Ψ⁺"},
                     {"kind": "bell", "variant": "psi_plus", "n": 2},
                     {"en": "(|01⟩+|10⟩)/√2, anti-correlated outcomes.",
                      "es": "(|01⟩+|10⟩)/√2, resultados anticorrelacionados."}),
            Instance("bell-psi-minus", {"en": "Bell Ψ⁻", "es": "Bell Ψ⁻"},
                     {"kind": "bell", "variant": "psi_minus", "n": 2},
                     {"en": "(|01⟩−|10⟩)/√2, the singlet, rotationally invariant.",
                      "es": "(|01⟩−|10⟩)/√2, el singlete, invariante ante rotaciones."}),
            Instance("ghz-3", {"en": "GHZ (3)", "es": "GHZ (3)"},
                     {"kind": "ghz", "n": 3},
                     {"en": "(|000⟩+|111⟩)/√2, maximal, fragile global entanglement.",
                      "es": "(|000⟩+|111⟩)/√2, entrelazamiento global máximo y frágil."}),
            Instance("ghz-4", {"en": "GHZ (4)", "es": "GHZ (4)"},
                     {"kind": "ghz", "n": 4},
                     {"en": "Four-qubit cat state (|0000⟩+|1111⟩)/√2.",
                      "es": "Estado de gato de cuatro qubits (|0000⟩+|1111⟩)/√2."}),
            Instance("w-3", {"en": "W (3)", "es": "W (3)"},
                     {"kind": "w", "n": 3},
                     {"en": "(|001⟩+|010⟩+|100⟩)/√3, robust to losing one qubit.",
                      "es": "(|001⟩+|010⟩+|100⟩)/√3, robusto ante la pérdida de un qubit."}),
        ]
