"""Noise & error mitigation, what a real (noisy) device returns, and what mitigation buys.

Real quantum hardware is noisy: gates and readout introduce errors that pull expectation values toward
zero. This case runs a circuit with a known ideal value through a realistic Aer noise model (depolarizing
+ the deeper the circuit, the worse), then applies **zero-noise extrapolation (ZNE)**: run at amplified
noise (gate folding), fit, extrapolate back to zero noise. We show ideal vs noisy vs mitigated. The honest
framing: mitigation recovers *some* signal but has fundamentally **exponential** sampling overhead and is a
NISQ *bridge*, not error correction; and at any classically-simulable scale a statevector simulator returns
the exact answer for free. (Mitiq is the standard ZNE library, but it is GPL-3.0, qversus implements the core
technique directly to keep the repo permissive; Mitiq is documented as the production tool.)
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class Noise(Problem):
    id = "noise"
    category = "noise-and-qec"
    live_capable = False  # needs the Aer noise model (density matrix) → precompute
    title = {"en": "Noise & error mitigation (ZNE)", "es": "Ruido y mitigación de errores (ZNE)"}
    concept = {
        "en": (
            "A Bell circuit has ideal parity ⟨Z₀Z₁⟩ = 1, but a noisy device returns less. We model the "
            "device with an Aer depolarizing noise model (worse for deeper circuits), measure the noisy "
            "⟨Z₀Z₁⟩, then apply zero-noise extrapolation: deliberately amplify the noise by folding the "
            "circuit (U→U U† U…), measure at noise scales λ=1,3,5, and extrapolate back to λ=0. Mitigation "
            "claws back much of the lost signal, but note the honest limits: ZNE's sampling cost grows "
            "exponentially with circuit size, it is mitigation (bias reduction) not correction, and at this "
            "classically-simulable scale a statevector simulator just gives the exact 1.0 for free."
        ),
        "es": (
            "Un circuito de Bell tiene paridad ideal ⟨Z₀Z₁⟩ = 1, pero un dispositivo ruidoso devuelve menos. "
            "Modelamos el dispositivo con un modelo de ruido despolarizante de Aer (peor cuanto más profundo "
            "el circuito), medimos el ⟨Z₀Z₁⟩ ruidoso, y aplicamos extrapolación a ruido cero: AMPLIFICAMOS "
            "el ruido plegando el circuito (U→U U† U…), medimos a escalas λ=1,3,5 y extrapolamos a λ=0. La "
            "mitigación recupera buena parte de la señal perdida, pero con límites honestos: el costo de "
            "muestreo de ZNE crece exponencialmente con el tamaño, es mitigación (reducción de sesgo) no "
            "corrección, y a esta escala simulable clásicamente un simulador de vector de estado da el 1.0 "
            "exacto gratis."
        ),
    }
    metric = {"en": "⟨Z₀Z₁⟩ (ideal = 1)", "es": "⟨Z₀Z₁⟩ (ideal = 1)"}
    references = [
        {"label": "Temme, Bravyi & Gambetta, Error mitigation for short-depth quantum circuits (2017)",
         "doi": "10.1103/PhysRevLett.119.180509"},
        {"label": "Giurgica-Tiron et al., Digital zero-noise extrapolation for quantum error mitigation (2020)",
         "url": "https://arxiv.org/abs/2005.10921"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("noise-p0.01-d1", "p=0.01, depth 1", {"p": 0.01, "depth": 1, "n": 2}),
            ("noise-p0.02-d1", "p=0.02, depth 1", {"p": 0.02, "depth": 1, "n": 2}),
            ("noise-p0.05-d1", "p=0.05, depth 1", {"p": 0.05, "depth": 1, "n": 2}),
            ("noise-p0.01-d3", "p=0.01, depth 3", {"p": 0.01, "depth": 3, "n": 2}),
            ("noise-p0.03-d3", "p=0.03, depth 3", {"p": 0.03, "depth": 3, "n": 2}),
            ("noise-p0.05-d3", "p=0.05, depth 3", {"p": 0.05, "depth": 3, "n": 2}),
        ]
        out = []
        for iid, label, params in defs:
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"2-qubit depolarizing p={params['p']}, depth {params['depth']}, ideal ⟨Z₀Z₁⟩=1; "
                       "see noisy vs ZNE-mitigated.",
                 "es": f"despolarizante de 2 qubits p={params['p']}, profundidad {params['depth']}, ideal "
                       "⟨Z₀Z₁⟩=1; ve ruidoso vs mitigado por ZNE."},
            ))
        return out
