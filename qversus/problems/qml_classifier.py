"""Quantum machine learning, a quantum-kernel classifier (the second learned method, and a hype check).

A quantum feature map embeds a data point x into a quantum state |φ(x)⟩; the fidelity kernel
K(x,x') = |⟨φ(x)|φ(x')⟩|² then feeds a classical SVM. qversus runs this on small 2-D datasets and puts it next
to a classical RBF-SVM on the same data. The honest, literature-backed verdict: on these toy sets both reach
high accuracy and the quantum kernel shows NO advantage; provable quantum-kernel separations are contrived
(built around problems like discrete-log), and on real data quantum kernels are competitive-at-best, usually
worse, and suffer data-loading bottlenecks. QML is one of the most over-hyped corners of the field, this
case lets you see that honestly.
"""

from __future__ import annotations

import numpy as np

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class QMLClassifier(Problem):
    id = "qml"
    category = "variational"
    live_capable = False  # quantum-kernel Gram matrix + an SVM fit → precompute
    title = {"en": "QML, quantum-kernel classifier", "es": "QML, clasificador de kernel cuántico"}
    concept = {
        "en": (
            "A quantum feature map sends a 2-D point x to a state |φ(x)⟩; the fidelity kernel "
            "K(x,x')=|⟨φ(x)|φ(x')⟩|² is estimated on the quantum device and handed to a classical SVM. We "
            "compare it to a classical RBF-SVM on the same toy datasets (linear, circles, moons, XOR). Both "
            "classify well, and that is the point: the quantum kernel buys no advantage here. The few "
            "provable quantum-kernel speedups are built around contrived problems (discrete-log); on real "
            "data quantum kernels are competitive at best, usually worse, and bottlenecked by data loading. "
            "QML is heavily over-hyped; this case shows it honestly."
        ),
        "es": (
            "Un mapa de características cuántico envía un punto 2-D x a un estado |φ(x)⟩; el kernel de "
            "fidelidad K(x,x')=|⟨φ(x)|φ(x')⟩|² se estima en el dispositivo cuántico y se pasa a un SVM "
            "clásico. Lo comparamos con un SVM-RBF clásico sobre los mismos datos de juguete (lineal, "
            "círculos, lunas, XOR). Ambos clasifican bien, y ese es el punto: el kernel cuántico NO da "
            "ventaja aquí. Las pocas separaciones demostrables se construyen sobre problemas artificiales "
            "(logaritmo discreto); en datos reales los kernels cuánticos son competitivos en el mejor caso, "
            "usualmente peores, y limitados por la carga de datos. QML está muy sobrevalorado; este caso lo "
            "muestra con honestidad."
        ),
    }
    metric = {"en": "classification accuracy", "es": "exactitud de clasificación"}
    references = [
        {"label": "Havlíček et al., Supervised learning with quantum-enhanced feature spaces (2019)",
         "doi": "10.1038/s41586-019-0980-2"},
        {"label": "Huang et al., Power of data in quantum machine learning (2021)",
         "doi": "10.1038/s41467-021-22539-9"},
    ]

    @staticmethod
    def dataset(kind: str, seed: int = 42, n: int = 40):
        """Deterministic 2-D binary dataset, features scaled to ~[0, π] for angle embedding."""
        rng = np.random.default_rng(seed)
        half = n // 2
        if kind == "linear":
            a = rng.normal([-1.0, -1.0], 0.45, (half, 2))
            b = rng.normal([1.0, 1.0], 0.45, (half, 2))
        elif kind == "linear-hard":
            a = rng.normal([-0.4, -0.4], 0.6, (half, 2))
            b = rng.normal([0.4, 0.4], 0.6, (half, 2))
        elif kind == "circles":
            t = rng.uniform(0, 2 * np.pi, half)
            a = np.c_[0.5 * np.cos(t), 0.5 * np.sin(t)] + rng.normal(0, 0.06, (half, 2))
            t2 = rng.uniform(0, 2 * np.pi, half)
            b = np.c_[1.6 * np.cos(t2), 1.6 * np.sin(t2)] + rng.normal(0, 0.06, (half, 2))
        elif kind == "moons":
            t = rng.uniform(0, np.pi, half)
            a = np.c_[np.cos(t), np.sin(t)] + rng.normal(0, 0.08, (half, 2))
            t2 = rng.uniform(0, np.pi, half)
            b = np.c_[1.0 - np.cos(t2), 0.5 - np.sin(t2)] + rng.normal(0, 0.08, (half, 2))
        elif kind == "xor":
            c = rng.normal(0, 0.35, (half, 2))
            a = np.r_[c[: half // 2] + [1, 1], c[half // 2:] + [-1, -1]]
            d = rng.normal(0, 0.35, (half, 2))
            b = np.r_[d[: half // 2] + [1, -1], d[half // 2:] + [-1, 1]]
        elif kind == "blobs":
            a = rng.normal([-1.2, 0.8], 0.4, (half, 2))
            b = rng.normal([1.0, -0.6], 0.4, (half, 2))
        else:  # pragma: no cover
            raise ValueError(kind)
        X = np.vstack([a, b]).astype(float)
        y = np.array([0] * len(a) + [1] * len(b))
        # scale each feature to [0, π] for the angle feature map
        lo, hi = X.min(0), X.max(0)
        X = (X - lo) / (hi - lo + 1e-9) * np.pi
        idx = rng.permutation(len(X))
        X, y = X[idx], y[idx]
        cut = int(0.6 * len(X))
        return X[:cut], y[:cut], X[cut:], y[cut:]

    def instances(self) -> list[Instance]:
        kinds = [
            ("linear", "linearly separable"),
            ("linear-hard", "overlapping (hard linear)"),
            ("circles", "concentric circles"),
            ("moons", "two moons"),
            ("xor", "XOR (4 clusters)"),
            ("blobs", "two blobs"),
        ]
        out = []
        for kind, desc in kinds:
            out.append(Instance(
                f"qml-{kind}", {"en": f"dataset: {desc}", "es": f"dataset: {desc}"},
                {"kind": kind, "n": 2},
                {"en": f"2-D {desc}, quantum-kernel SVM vs classical RBF-SVM on the same split.",
                 "es": f"2-D {desc}, SVM de kernel cuántico vs SVM-RBF clásico sobre la misma partición."},
            ))
        return out
