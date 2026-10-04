"""Quantum Phase Estimation, read an eigenphase into a register (the QFT's first payoff).

Given a unitary U and one of its eigenstates |ψ⟩ with U|ψ⟩ = e^{2πiφ}|ψ⟩, QPE writes a t-bit estimate of φ
into a counting register using controlled-U^{2^j} powers and an inverse QFT. Here U = P(2πφ) (a phase
gate) with eigenstate |1⟩, so φ is exactly known, which lets qversus *verify* the estimate. The honest
framing: for a tiny unitary you can just diagonalize it classically and read φ exactly and instantly; QPE
earns its keep only when U acts on an exponentially large space you cannot diagonalize (e.g. e^{iHt} for a
molecular Hamiltonian, the heart of VQE-free chemistry and of Shor's order-finding). It is the QFT's first
real application, and it is *finite-precision*: t counting qubits resolve φ to 2^{-t}.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class QPE(Problem):
    id = "qpe"
    category = "flagship-algorithms"
    live_capable = True
    title = {"en": "Quantum Phase Estimation", "es": "Estimación cuántica de fase"}
    concept = {
        "en": (
            "QPE estimates the phase φ of an eigenvalue e^{2πiφ} of a unitary U. A counting register of t "
            "qubits is put in superposition; controlled-U^{2^j} kicks the phase back onto it; an inverse "
            "QFT turns that phase ramp into a binary number, the t-bit estimate of φ. It is the first real "
            "use of the QFT and the engine inside Shor's order-finding. Two honest caveats: it is "
            "finite-precision (t bits resolve φ to 2^{-t}), and at this toy scale a classical "
            "eigendecomposition of U gives φ exactly and instantly, QPE only wins when U is too large to "
            "diagonalize."
        ),
        "es": (
            "QPE estima la fase φ de un autovalor e^{2πiφ} de un unitario U. Un registro de conteo de t "
            "qubits se pone en superposición; controlled-U^{2^j} le devuelve la fase (phase kickback); una "
            "QFT inversa convierte esa rampa de fase en un número binario, la estimación de φ a t bits. Es "
            "el primer uso real de la QFT y el motor del order-finding de Shor. Dos salvedades honestas: es "
            "de precisión finita (t bits resuelven φ a 2^{-t}), y a esta escala de juguete una "
            "diagonalización clásica de U da φ exacto e instantáneo, QPE solo gana cuando U es demasiado "
            "grande para diagonalizar."
        ),
    }
    metric = {"en": "estimated eigenphase φ", "es": "fase propia estimada φ"}
    references = [
        {"label": "Kitaev, Quantum measurements and the Abelian Stabilizer Problem (1995)",
         "url": "https://arxiv.org/abs/quant-ph/9511026"},
        {"label": "Nielsen & Chuang, Quantum Computation and Quantum Information (2010)",
         "url": "https://doi.org/10.1017/CBO9780511976667"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("qpe-t3-1_4", "t=3, φ=1/4 (exact)", {"t": 3, "phi": 0.25, "exact": True}),
            ("qpe-t3-5_8", "t=3, φ=5/8 (exact)", {"t": 3, "phi": 0.625, "exact": True}),
            ("qpe-t4-3_16", "t=4, φ=3/16 (exact)", {"t": 4, "phi": 0.1875, "exact": True}),
            ("qpe-t3-0.3", "t=3, φ=0.3 (finite precision)", {"t": 3, "phi": 0.3, "exact": False}),
            ("qpe-t4-0.8", "t=4, φ=0.8 (finite precision)", {"t": 4, "phi": 0.8, "exact": False}),
            ("qpe-t5-0.1", "t=5, φ=0.1 (finite precision)", {"t": 5, "phi": 0.1, "exact": False}),
        ]
        out = []
        for iid, label, params in defs:
            t = params["t"]
            kind = "exact (φ = m/2ᵗ)" if params["exact"] else f"nearest of 2^{t} bins"
            out.append(Instance(
                iid, {"en": label, "es": label}, params,
                {"en": f"U=P(2πφ), eigenstate |1⟩, t={t} counting qubits → {kind}; resolution 2^-{t}.",
                 "es": f"U=P(2πφ), autoestado |1⟩, t={t} qubits de conteo → {kind}; resolución 2^-{t}."},
            ))
        return out
