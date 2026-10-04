# 04 · Flagship algorithms

## `grover`: unstructured search

Among N = 2ⁿ items, M are marked. Each Grover iteration (oracle phase flip, then inversion about the mean)
rotates the state by 2θ in the plane of the marked and unmarked superpositions, with sin θ = √(M/N); after k
iterations the success probability is sin²((2k+1)θ). The optimal k is ⌊(π/4)√(N/M)⌋; more iterations
over-rotate.

| Parameter | Meaning |
|---|---|
| `n` | qubits (N = 2ⁿ) |
| `marked` | list of marked item indices |

Instances: `grover-2-3`, `grover-3-5`, `grover-3-2`, `grover-3-2marked` (items 3 and 5), `grover-4-10`,
`grover-4-0`.

| Solver | `value` fields (and `extra`) |
|---|---|
| `grover-qiskit` | `found`, `correct`, `success_prob` (total probability on the marked items), `quantum_queries`; `extra.iterations`, `extra.success_prob`; trace `extra.marked` |
| `grover-classical` | `found`, `correct`, `classical_queries` (a seeded random scan) |

Checked: on `grover-3-5` the item is found with success probability above 0.9. References: Grover, STOC '96,
doi:10.1145/237814.237866; Nielsen and Chuang (2010).

## `qft`: the quantum Fourier transform

The QFT applies the discrete Fourier transform to the amplitudes in O(n²) gates, against the FFT's
O(n·2ⁿ) operations, but its output cannot be read out: a measurement returns one sample, not the spectrum.

| Parameter | Meaning |
|---|---|
| `n` | qubits |
| `k` | the basis input |k⟩ |

Instances: n = 3 with k = 0, 1, 4, 5; n = 4 with k = 1, 6.

| Solver | `value` fields |
|---|---|
| `qft-qiskit` | `fidelity_vs_dft`, `matches_dft`, `gate_count`, `readable` (= false) |
| `qft-classical` | `spectrum_uniform_prob`, `amp0_phase_deg`, `ops`, `readable` (= true) |

Checked: on k = 5 the circuit matches the analytic DFT with fidelity above 0.999. References: Coppersmith,
arXiv:quant-ph/0201067; Nielsen and Chuang (2010).

## `qpe`: quantum phase estimation

Estimate the eigenphase φ of U|ψ⟩ = e^{2πiφ}|ψ⟩ (here a phase gate with eigenstate |1⟩, so φ is known
exactly) with t counting qubits. Exact when φ has a t-bit binary expansion; otherwise the nearest t-bit value
is returned with high probability.

| Parameter | Meaning |
|---|---|
| `t` | counting qubits |
| `phi` | the true phase |
| `exact` | whether φ is representable in t bits |

Instances: φ = 1/4, 5/8, 3/16 (exact); 0.3, 0.8, 0.1 (finite precision).

| Solver | `value` fields |
|---|---|
| `qpe-qiskit` | `phi_estimate`, `phi_true`, `error`, `p_top`, `counting_qubits` |
| `qpe-classical` | `phi_exact`, `exact`, `ops` |

Checked: φ = 1/4 with 3 counting qubits is recovered with zero error and top probability above 0.99.
References: Kitaev, arXiv:quant-ph/9511026; Nielsen and Chuang (2010).

## `shor`: order finding for N = 15

Order finding by QPE over the modular-multiplication unitary, then classical continued fractions and gcds.
At N = 15 the factors are immediate classically; the case shows the mechanism, not a capability (Gidney
2025 estimates RSA-2048 at fewer than a million noisy physical qubits, error-corrected, running for under a
week).

| Parameter | Meaning |
|---|---|
| `N` | 15 |
| `a` | base, coprime to N |
| `t` | counting qubits |

Instances: a = 2, 4, 7, 8, 11, 13.

| Solver | `value` fields |
|---|---|
| `shor-qiskit` | `factors`, `order`, `base`, `correct` (cost: `counting_qubits`, `work_qubits`, `depth`) |
| `shor-classical` | `factors`, `method` (trial division), `ops` |

Checked: a = 7 has order 4 and gives factors [3, 5] in both. References: Shor, SIAM J. Comput. 26, 1484
(1997), doi:10.1137/S0097539795293172; Gidney, arXiv:2505.15917 (2025).
