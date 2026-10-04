"""MaxCut, the flagship "complex case attacked by many solvers".

Partition a graph's vertices into two sets to maximize the number of edges crossing the cut. It is the
canonical QAOA benchmark, and the canonical honesty lesson: QAOA (a quantum variational heuristic, run
here on Qiskit AND PennyLane) is compared head-to-head with the classical baselines on the same graph, 
exact brute force (provably optimal, microseconds at this scale) and a greedy heuristic. The dossier
verdict holds: at these sizes classical wins decisively. The variant-bar exposes a family of graphs.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class MaxCut(Problem):
    id = "maxcut"
    category = "variational"
    live_capable = False  # QAOA carries an offline classical optimization loop → precompute lane
    title = {"en": "MaxCut, QAOA vs classical", "es": "MaxCut, QAOA vs clásico"}
    concept = {
        "en": (
            "MaxCut splits a graph's vertices into two groups to cut as many edges as possible, NP-hard "
            "in general. QAOA encodes it as an Ising cost Hamiltonian and alternates cost/mixer layers, "
            "optimizing the angles (γ, β) classically. We run QAOA on Qiskit and PennyLane and put it "
            "next to exact brute force and a greedy heuristic on the same graph. The honest result: at "
            "these sizes the classical optimum is found in microseconds and QAOA does not win."
        ),
        "es": (
            "MaxCut divide los vértices de un grafo en dos grupos para cortar la mayor cantidad de aristas "
            "posible, NP-difícil en general. QAOA lo codifica como un Hamiltoniano de costo tipo Ising y "
            "alterna capas de costo/mezcla, optimizando los ángulos (γ, β) de forma clásica. Ejecutamos QAOA "
            "en Qiskit y PennyLane y lo ponemos junto a la fuerza bruta exacta y una heurística voraz sobre "
            "el mismo grafo. El resultado honesto: a estos tamaños el óptimo clásico se encuentra en "
            "microsegundos y QAOA no gana."
        ),
    }
    metric = {"en": "cut value (edges crossing)", "es": "valor del corte (aristas cruzadas)"}
    references = [
        {"label": "Farhi, Goldstone & Gutmann, A Quantum Approximate Optimization Algorithm (2014)",
         "url": "https://arxiv.org/abs/1411.4028"},
        {"label": "Goemans & Williamson, .878-approximation for MaxCut via SDP (1995)",
         "doi": "10.1145/227683.227684"},
        {"label": "Barak & Marwaha, Classical algorithms vs low-depth QAOA on high-girth graphs (2021)",
         "url": "https://arxiv.org/abs/2106.05900"},
    ]

    @staticmethod
    def cut_value(edges: list[list[int]], bitstring: str) -> int:
        """Edges whose endpoints fall on opposite sides of the partition encoded by `bitstring`."""
        return sum(1 for (u, v) in edges if bitstring[u] != bitstring[v])

    def instances(self) -> list[Instance]:
        return [
            Instance("triangle", {"en": "Triangle K₃", "es": "Triángulo K₃"},
                     {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
                     {"en": "Odd cycle, at most 2 of 3 edges can be cut (frustration).",
                      "es": "Ciclo impar, a lo más 2 de 3 aristas se cortan (frustración)."}),
            Instance("square", {"en": "Square C₄", "es": "Cuadrado C₄"},
                     {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [0, 3]]},
                     {"en": "Even cycle, fully cuttable (max cut = 4).",
                      "es": "Ciclo par, totalmente cortable (corte máx = 4)."}),
            Instance("square-diag", {"en": "Square + diagonal", "es": "Cuadrado + diagonal"},
                     {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [0, 3], [0, 2]]},
                     {"en": "Adds frustration to the 4-cycle.",
                      "es": "Agrega frustración al ciclo de 4."}),
            Instance("bowtie", {"en": "Bow-tie", "es": "Corbatín"},
                     {"n": 5, "edges": [[0, 1], [1, 2], [0, 2], [2, 3], [3, 4], [2, 4]]},
                     {"en": "Two triangles sharing a vertex.",
                      "es": "Dos triángulos que comparten un vértice."}),
            Instance("pentagon", {"en": "Pentagon C₅", "es": "Pentágono C₅"},
                     {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]]},
                     {"en": "Odd 5-cycle, max cut = 4, one edge always frustrated.",
                      "es": "Ciclo impar de 5, corte máx = 4, una arista siempre frustrada."}),
            Instance("petersen-ish", {"en": "6-node 3-regular", "es": "3-regular de 6 nodos"},
                     {"n": 6, "edges": [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [0, 3], [1, 4], [2, 5]]},
                     {"en": "Prism graph, denser, a harder landscape for low-depth QAOA.",
                      "es": "Grafo prisma, más denso, un paisaje más difícil para QAOA de baja profundidad."}),
        ]
