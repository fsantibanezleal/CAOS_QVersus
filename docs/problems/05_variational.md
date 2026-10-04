# 05 · Variational

Hybrid methods: a parameterised circuit evaluated by a quantum (here, simulated) device inside a classical
optimisation loop. They are the near-term candidates, and the place where claims most need a classical baseline.

## `maxcut`: QAOA against brute force and a greedy heuristic

Partition the vertices to maximise the number of edges crossing the cut. QAOA at depth p = 1 prepares
|γ,β⟩ = e^{−iβB} e^{−iγC} |+⟩ⁿ and maximises ⟨C⟩ over (γ, β); here by grid search on the exact expectation.

| Parameter | Meaning |
|---|---|
| `n` | vertices |
| `edges` | list of `[u, v]` |

Instances: `triangle` (K₃), `square` (C₄), `square-diag`, `bowtie`, `pentagon` (C₅), `petersen-ish`
(6-node 3-regular).

| Solver | `value` fields (and `extra`) |
|---|---|
| `qaoa-qiskit` | `cut`, `bitstring`, `expectation`; `extra.landscape` (the (γ, β) grid of ⟨C⟩) |
| `qaoa-pennylane` | `cut`, `bitstring` (independent implementation: `qml.qaoa.maxcut`, cost minimised) |
| `qaoa-cirq` | `cut`, `bitstring`, `expectation` |
| `maxcut-bruteforce` | `cut`, `bitstring`; `optimal = true` (cost: `evaluated` = 2ⁿ) |
| `maxcut-greedy` | `cut`, `bitstring` (single-flip local search from a seeded start) |

Bit strings: position u is vertex u. `MaxCut.cut_value(edges, bitstring)` scores any partition.

Checked: the square's optimum is 4 and no QAOA cut exceeds the brute-force optimum; the triangle is frustrated
(optimum 2). References: Farhi, Goldstone and Gutmann, arXiv:1411.4028; Goemans and Williamson, J. ACM 42,
1115 (1995), doi:10.1145/227683.227684; Harrigan et al., arXiv:2106.05900.

## `vqe`: the H2 ground-state energy

Minimise ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀ (the variational principle) for the H2 Hamiltonian built by
`qml.qchem.molecular_hamiltonian` (PennyLane's default STO-3G basis, four qubits). The ansatz is the
Hartree-Fock reference |1100⟩ followed by one `DoubleExcitation(θ)`, the single excitation that captures the
H2 ground state in this basis.

| Parameter | Meaning |
|---|---|
| `R_angstrom`, `R_bohr` | bond length |
| `n` | 4 |

Instances: R = 0.5, 0.74 (near equilibrium), 1.0, 1.5, 2.0, 2.5 Å.

| Solver | `value` fields (and `extra`) |
|---|---|
| `vqe-pennylane` | `energy`, `optimal_theta`, `qubits`; `extra.landscape` (energy against θ) |
| `vqe-classical` | `energy`, `method` (exact diagonalisation, FCI in this basis), `dim` |

Checked: at 0.74 Å VQE lies within chemical accuracy (1.6 mHa) of the exact energy, which is below −1.13 Ha.
References: Peruzzo et al., Nat. Commun. 5, 4213 (2014), doi:10.1038/ncomms5213; McArdle et al., Rev. Mod.
Phys. 92, 015003 (2020), doi:10.1103/RevModPhys.92.015003.

## `qml`: a quantum-kernel classifier

An angle-embedding feature map (`qml.AngleEmbedding`, one qubit per feature) prepares |φ(x)⟩; the fidelity
kernel K(x, x') = |⟨φ(x')|φ(x)⟩|² is the probability of |00⟩ after U(x) followed by U(x')†, and the Gram
matrix feeds scikit-learn's SVC with a precomputed kernel. The comparison is an RBF-kernel SVC
(`gamma="scale"`) on the same split.

| Parameter | Meaning |
|---|---|
| `kind` | dataset: `linear`, `linear-hard`, `circles`, `moons`, `xor`, `blobs` |
| `n` | 2 (features and qubits) |

| Solver | `value` fields (and `extra`) |
|---|---|
| `qml-pennylane` | `train_acc`, `test_acc`, `qubits`; `extra.n_train`, `extra.n_test` (cost: `kernel_evals`) |
| `qml-classical` | `train_acc`, `test_acc` (cost: `support_vectors`) |

Checked: on `circles` both reach at least 0.8 test accuracy: the kernel works, and so does the classical one.
References: Havlicek et al., Nature 567, 209 (2019), doi:10.1038/s41586-019-0980-2; Huang et al., Nat.
Commun. 12, 2631 (2021), doi:10.1038/s41467-021-22539-9.
