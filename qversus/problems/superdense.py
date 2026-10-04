"""Superdense coding, send 2 classical bits by transmitting 1 qubit (teleportation's dual).

Alice and Bob share a Bell pair. To send Bob two classical bits, Alice applies one of {I, X, Z, ZX} to her
half (encoding the 2 bits), then sends Bob that single qubit; Bob does a Bell measurement on both qubits and
reads off both bits perfectly. So one transmitted qubit carries two classical bits, double the Holevo
limit of one bit per qubit, at the cost of a pre-shared entangled pair. It is the exact dual of
teleportation (which spends entanglement + 2 classical bits to move 1 qubit). The honest framing: it's a
real communication resource trade, not free bandwidth, the Bell pair had to be distributed beforehand, and
without entanglement one qubit conveys at most one classical bit.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class Superdense(Problem):
    id = "superdense"
    category = "entanglement"
    live_capable = True
    title = {"en": "Superdense coding", "es": "Codificación superdensa"}
    concept = {
        "en": (
            "Superdense coding sends two classical bits while physically transmitting only one qubit, using "
            "a pre-shared Bell pair. Alice encodes the 2-bit message into her half with a Pauli "
            "(00→I, 01→X, 10→Z, 11→ZX), turning the shared state into one of the four Bell states; she sends "
            "that one qubit to Bob, who undoes the entanglement (CX, H) and measures both bits exactly. One "
            "qubit, two bits, double the Holevo limit, but only because an entangled pair was distributed "
            "in advance. It is the dual of teleportation, and an honest resource trade rather than free "
            "bandwidth."
        ),
        "es": (
            "La codificación superdensa envía dos bits clásicos transmitiendo físicamente un solo qubit, "
            "usando un par de Bell compartido. Alice codifica el mensaje de 2 bits en su mitad con un Pauli "
            "(00→I, 01→X, 10→Z, 11→ZX), convirtiendo el estado compartido en uno de los cuatro estados de "
            "Bell; envía ese qubit a Bob, quien deshace el entrelazamiento (CX, H) y mide ambos bits exacto. "
            "Un qubit, dos bits, el doble del límite de Holevo, pero solo porque se distribuyó un par "
            "entrelazado de antemano. Es el dual de la teletransportación, y un intercambio honesto de "
            "recursos, no ancho de banda gratis."
        ),
    }
    metric = {"en": "classical bits decoded per qubit sent", "es": "bits clásicos decodificados por qubit enviado"}
    references = [
        {"label": "Bennett & Wiesner, Communication via one- and two-particle operators on EPR states (1992)",
         "doi": "10.1103/PhysRevLett.69.2881"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        # The honest complete set is the four 2-bit messages: not padded to a larger count.
        msgs = [("00", "message 00 → I"), ("01", "message 01 → X"),
                ("10", "message 10 → Z"), ("11", "message 11 → ZX")]
        out = []
        for bits, label in msgs:
            out.append(Instance(
                f"sd-{bits}", {"en": label, "es": label}, {"n": 2, "message": bits},
                {"en": f"Alice sends bits {bits} via one qubit; Bob decodes both.",
                 "es": f"Alice envía los bits {bits} por un qubit; Bob decodifica ambos."},
            ))
        return out
