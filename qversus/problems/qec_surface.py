"""Surface code, the leading fault-tolerance architecture (and a clean threshold demo).

The rotated surface code is the front-runner for building a fault-tolerant qubit: data + measure qubits on
a 2-D lattice, X- and Z-stabilizers measured every round, decoded by minimum-weight matching. Unlike the
repetition code (bit-flips only), it corrects BOTH X and Z errors. qversus runs the real Stim + PyMatching
pipeline for distance 3 and 5 across noise rates spanning the ~1% threshold, so you can watch the textbook
behavior: below threshold a bigger code is better; above threshold a bigger code is worse (more qubits =
more places to fail). This is exactly the regime Google's Willow chip entered in 2024, and a sober
reminder that one good logical qubit is still ~1000 physical qubits and many orders of magnitude from a
useful machine.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class QECSurface(Problem):
    id = "qec-surface"
    category = "noise-and-qec"
    live_capable = False  # Monte-Carlo sampling + matching decode → precompute
    title = {"en": "QEC, surface code (threshold)", "es": "QEC, código de superficie (umbral)"}
    concept = {
        "en": (
            "The rotated surface code places data and measure qubits on a 2-D lattice and measures X- and "
            "Z-parity stabilizers every round, correcting both bit- and phase-flips. We run the real "
            "toolchain, Stim simulates the noisy circuit, PyMatching decodes, for distance 3 (≈26 qubits) "
            "and 5 (≈64 qubits) at noise rates around the ~1% threshold. Below threshold the distance-5 "
            "logical error is lower than distance-3 (adding qubits helps); above threshold it is HIGHER "
            "(adding qubits hurts). Seeing that crossover is the whole game of fault tolerance, and the "
            "honest scale check: a single useful logical qubit is ~1000 physical qubits, and a useful "
            "machine needs thousands of them."
        ),
        "es": (
            "El código de superficie rotado coloca qubits de datos y de medición en una red 2-D y mide "
            "estabilizadores de paridad X y Z cada ronda, corrigiendo bit- y phase-flips. Ejecutamos el stack "
            "real, Stim simula el circuito ruidoso, PyMatching decodifica, para distancia 3 (≈26 qubits) y "
            "5 (≈64 qubits) a tasas de ruido alrededor del umbral del ~1%. Bajo umbral el error lógico de "
            "distancia-5 es menor que el de distancia-3 (agregar qubits ayuda); sobre umbral es mayor "
            "(agregar qubits empeora). Ver ese cruce es la esencia de la tolerancia a fallos, y la "
            "verificación honesta de escala: un qubit lógico útil son ~1000 físicos, y una máquina útil "
            "necesita miles."
        ),
    }
    metric = {"en": "logical error rate", "es": "tasa de error lógico"}
    references = [
        {"label": "Fowler et al., Surface codes: Towards practical large-scale quantum computation (2012)",
         "doi": "10.1103/PhysRevA.86.032324"},
        {"label": "Google Quantum AI, Quantum error correction below the surface code threshold (2024)",
         "url": "https://arxiv.org/abs/2408.13687"},
    ]

    def instances(self) -> list[Instance]:
        task = "surface_code:rotated_memory_z"
        defs = [(3, 0.005), (5, 0.005), (3, 0.01), (5, 0.01), (3, 0.02), (5, 0.02)]
        out = []
        for d, p in defs:
            out.append(Instance(
                f"surf-d{d}-p{p}", {"en": f"distance {d}, p={p}", "es": f"distancia {d}, p={p}"},
                {"distance": d, "p": p, "rounds": d, "code_task": task},
                {"en": f"d={d} rotated surface code, circuit noise p={p}, {'below' if p < 0.01 else 'near' if p == 0.01 else 'above'} threshold.",
                 "es": f"código de superficie rotado d={d}, ruido de circuito p={p}, {'bajo' if p < 0.01 else 'cerca del' if p == 0.01 else 'sobre'} umbral."},
            ))
        return out
