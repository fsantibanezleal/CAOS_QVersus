"""Quantum teleportation, move an unknown qubit with entanglement + 2 classical bits.

Alice holds an unknown state |ψ⟩ and shares a Bell pair with Bob. She entangles |ψ⟩ with her half, does a
Bell measurement, and sends Bob 2 classical bits; Bob applies a Pauli correction and recovers |ψ⟩ exactly.
The original is destroyed (no-cloning) and nothing travels faster than light (the classical bits are
needed). qversus runs the coherent (deferred-measurement) form so the statevector trace shows |ψ⟩'s Bloch
vector hop from Alice's qubit to Bob's with fidelity 1. The honest comparison: with only classical
resources (measure-and-resend) you cannot do better than average fidelity 2/3, so teleportation is a
genuine quantum protocol with no classical equivalent, but it is not faster-than-light communication and it
*requires* pre-shared entanglement and a classical channel.
"""

from __future__ import annotations

import math

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

PI = math.pi


@register_problem
class Teleportation(Problem):
    id = "teleportation"
    category = "entanglement"
    live_capable = True   # committed as a coherent 3-qubit unitary (deferred-measurement form)
    title = {"en": "Quantum teleportation", "es": "Teletransportación cuántica"}
    concept = {
        "en": (
            "Teleportation moves an unknown qubit state |ψ⟩ from Alice to Bob using one shared Bell pair and "
            "two classical bits. Alice entangles |ψ⟩ with her half of the pair, measures both in the Bell "
            "basis, and sends the 2-bit outcome; Bob applies the matching Pauli (I/X/Z/XZ) and ends up with "
            "|ψ⟩ exactly. Alice's copy is gone (no-cloning), and the classical bits are essential, so this "
            "is not faster-than-light. We run the coherent (deferred-measurement) version: watch |ψ⟩'s "
            "Bloch vector leave Alice's qubit and reappear on Bob's, fidelity 1. Classically you can't "
            "transmit an unknown qubit better than fidelity 2/3 (measure-and-resend), so this is a real "
            "quantum protocol, though it needs entanglement and a classical channel."
        ),
        "es": (
            "La teletransportación mueve un estado de qubit desconocido |ψ⟩ de Alice a Bob usando un par de "
            "Bell compartido y dos bits clásicos. Alice entrelaza |ψ⟩ con su mitad del par, mide ambos en la "
            "base de Bell y envía el resultado de 2 bits; Bob aplica el Pauli correspondiente (I/X/Z/XZ) y "
            "obtiene |ψ⟩ exacto. La copia de Alice desaparece (no-clonación), y los bits clásicos son "
            "esenciales, así que no es más rápido que la luz. Ejecutamos la versión coherente (medición "
            "diferida): observa el vector de Bloch de |ψ⟩ salir del qubit de Alice y reaparecer en el de "
            "Bob, fidelidad 1. Clásicamente no puedes transmitir un qubit desconocido con fidelidad mayor a "
            "2/3 (medir y reenviar), así que es un protocolo cuántico real, aunque necesita entrelazamiento "
            "y un canal clásico."
        ),
    }
    metric = {"en": "teleportation fidelity (ideal = 1)", "es": "fidelidad de teletransportación (ideal = 1)"}
    references = [
        {"label": "Bennett et al., Teleporting an unknown quantum state via dual classical and EPR channels (1993)",
         "doi": "10.1103/PhysRevLett.70.1895"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("tele-0", "|0⟩", (0.0, 0.0)),
            ("tele-1", "|1⟩", (PI, 0.0)),
            ("tele-plus", "|+⟩", (PI / 2, 0.0)),
            ("tele-minus", "|−⟩", (PI / 2, PI)),
            ("tele-i", "|i⟩ = (|0⟩+i|1⟩)/√2", (PI / 2, PI / 2)),
            ("tele-generic", "generic (θ=π/3, φ=π/4)", (PI / 3, PI / 4)),
        ]
        out = []
        for iid, label, (theta, phi) in defs:
            out.append(Instance(
                iid, {"en": f"teleport {label}", "es": f"teletransportar {label}"},
                {"n": 3, "theta": theta, "phi": phi},
                {"en": f"Teleport the unknown state {label}, fidelity should be 1.",
                 "es": f"Teletransportar el estado desconocido {label}, la fidelidad debe ser 1."},
            ))
        return out
