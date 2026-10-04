"""VQE, variational ground-state energy of H₂ (the first learned/trained method).

The Variational Quantum Eigensolver is a hybrid loop: a parametrized circuit prepares a trial state, the
quantum computer measures ⟨H⟩, and a classical optimizer tunes the parameters to minimize the energy
(variational principle: ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀). qversus runs it on the real H₂ molecular Hamiltonian (built by
PennyLane's differentiable Hartree-Fock, STO-3G, 4 qubits) along a dissociation curve, against the exact
ground state by diagonalization. Honest framing: H₂ in a minimal basis is a 4×4 problem, trivial
classically, so VQE here is pedagogical, not advantageous; scaling it hits barren plateaus and deep
ansätze. It is, though, a genuine *learned* method: the energy is found by training θ.
"""

from __future__ import annotations

from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

ANGSTROM_TO_BOHR = 1.8897259886


@register_problem
class VQE(Problem):
    id = "vqe"
    category = "variational"
    live_capable = False  # 4 qubits + a classical optimization loop + chemistry → precompute
    title = {"en": "VQE, H₂ ground state", "es": "VQE, estado fundamental de H₂"}
    concept = {
        "en": (
            "VQE finds a molecule's ground-state energy with a hybrid quantum-classical loop. A "
            "parametrized circuit (here: the Hartree-Fock state plus one double-excitation rotation) "
            "prepares a trial state |ψ(θ)⟩; the device measures the energy ⟨ψ(θ)|H|ψ(θ)⟩; a classical "
            "optimizer lowers it toward the true ground energy (the variational principle guarantees it "
            "never goes below). We sweep the H–H bond length to trace the dissociation curve, using the "
            "real H₂ Hamiltonian (PennyLane differentiable Hartree-Fock, STO-3G, 4 qubits). It is a genuine "
            "learned method, but H₂ minimal-basis is a 4×4 matrix a laptop diagonalizes instantly, so the "
            "honest verdict is pedagogy, not advantage."
        ),
        "es": (
            "VQE halla la energía del estado fundamental de una molécula con un bucle híbrido "
            "cuántico-clásico. Un circuito parametrizado (aquí: el estado de Hartree-Fock más una rotación "
            "de doble excitación) prepara un estado de prueba |ψ(θ)⟩; el dispositivo mide la energía "
            "⟨ψ(θ)|H|ψ(θ)⟩; un optimizador clásico la baja hacia la energía fundamental real (el principio "
            "variacional garantiza que nunca baja de ella). Barremos la distancia de enlace H–H para trazar "
            "la curva de disociación, usando el Hamiltoniano real de H₂ (Hartree-Fock diferenciable de "
            "PennyLane, STO-3G, 4 qubits). Es un método aprendido genuino, pero H₂ en base mínima es una "
            "matriz 4×4 que un laptop diagonaliza al instante, así que el veredicto honesto es pedagogía, no "
            "ventaja."
        ),
    }
    metric = {"en": "ground-state energy (Hartree)", "es": "energía del estado fundamental (Hartree)"}
    references = [
        {"label": "Peruzzo et al., A variational eigenvalue solver on a photonic quantum processor (2014)",
         "doi": "10.1038/ncomms5213"},
        {"label": "McArdle et al., Quantum computational chemistry, Rev. Mod. Phys. 92, 015003 (2020)",
         "doi": "10.1103/RevModPhys.92.015003"},
    ]

    def instances(self) -> list[Instance]:
        bond_lengths = [0.5, 0.74, 1.0, 1.5, 2.0, 2.5]   # Å; 0.74 ≈ equilibrium
        out = []
        for r in bond_lengths:
            tag = " (≈ equilibrium)" if abs(r - 0.74) < 1e-9 else ""
            out.append(Instance(
                f"vqe-h2-{str(r).replace('.', '_')}",
                {"en": f"H₂ at R={r} Å{tag}", "es": f"H₂ a R={r} Å{tag}"},
                {"R_angstrom": r, "R_bohr": r * ANGSTROM_TO_BOHR, "n": 4},
                {"en": f"Bond length {r} Å, VQE vs exact diagonalization on the same H₂ Hamiltonian.",
                 "es": f"Distancia de enlace {r} Å, VQE vs diagonalización exacta del mismo Hamiltoniano."},
            ))
        return out
