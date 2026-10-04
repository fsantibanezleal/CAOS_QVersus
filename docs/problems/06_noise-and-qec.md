# 06 · Noise and error correction

## `noise`: depolarising noise and zero-noise extrapolation

A Bell pair's parity ⟨Z₀Z₁⟩ (ideal 1) under a depolarising noise model: two-qubit depolarising error p on
every CX and p/10 on every single-qubit gate, simulated with Qiskit Aer's `density_matrix` method, so the noisy
value is exact (no shot noise). Depth adds identity CX pairs (CX · CX = I), more noise with the same ideal
state. Zero-noise extrapolation (ZNE) folds the whole circuit, U → U(U†U)^k, to run at noise scales
λ = 2k + 1, fits the values and extrapolates to λ = 0. The core of ZNE is implemented directly; Mitiq, the
standard library, is GPL-3.0.

| Parameter | Meaning |
|---|---|
| `p` | depolarising probability per gate |
| `depth` | number of identity CX pairs appended |
| `n` | 2 |

Instances: p = 0.01, 0.02, 0.05 at depth 1; p = 0.01, 0.03, 0.05 at depth 3.

| Solver | `value` fields (and `extra`) |
|---|---|
| `noise-qiskit` (framework `qiskit-aer`) | `ideal`, `noisy`, `mitigated`, `residual_noisy`, `residual_mitigated`; `extra.zne` (scales and values), `extra.ideal_probs`, `extra.noisy_probs` (cost: `noise_scales`) |
| `noise-classical` | `value` (= 1, exact), `exact` |

Checked: at p = 0.02 the noisy parity is below 1 and ZNE reduces the residual; the classical value is exactly 1.
References: Temme, Bravyi and Gambetta, Phys. Rev. Lett. 119, 180509 (2017), doi:10.1103/PhysRevLett.119.180509;
Giurgica-Tiron et al., Digital zero-noise extrapolation for quantum error mitigation, arXiv:2005.10921 (2020).

## `qec-repetition`: the bit-flip repetition code

A distance-d repetition-code memory (Stim's `repetition_code:memory`) with d rounds of stabiliser measurement.
Noise: depolarising error p on the data qubits before each round and measurement flips with probability p/2.
Stim samples detection events (30,000 shots, seeded); PyMatching decodes them by minimum-weight perfect
matching built from Stim's own detector error model. Below threshold, a larger distance lowers the logical
error rate.

| Parameter | Meaning |
|---|---|
| `distance` | code distance (3 or 5) |
| `rounds` | stabiliser rounds (= distance) |
| `p` | physical error rate |

Instances: d = 3 and 5 at p = 0.05, 0.1, 0.2.

| Solver | `value` fields (and `extra`) |
|---|---|
| `qec-stim` | `logical_error_rate`, `distance`, `rounds`, `physical_p`, `physical_qubits`; `extra.shots`, `extra.code` (the Stim task) |
| `qec-baseline` | `physical_error_rate`, `physical_qubits` (= 1) |

The baseline is one unprotected qubit under the same depolarising model for the same number of rounds: per
round its Z value flips with probability q = 2p/3 (an X or a Y error), so after r rounds it is wrong with
probability (1 − (1 − 2q)^r) / 2. The code is worth having only when its logical error rate is below this.

Checked: at p = 0.05, distance 5 beats distance 3, and distance 3 beats the unprotected qubit. References:
Google Quantum AI, arXiv:2408.13687 (below-threshold surface-code memory); Gidney, Quantum 5, 497 (2021),
doi:10.22331/q-2021-07-06-497.

## `qec-surface`: the rotated surface code

The same pipeline on Stim's `surface_code:rotated_memory_z`, which corrects both X and Z errors, under
circuit-level noise: depolarising error p after every Clifford gate and measurement flips with probability p.
The instances span the threshold of about 1%: below it a larger code is better, above it worse.

| Parameter | Meaning |
|---|---|
| `distance` | 3 or 5 |
| `rounds` | = distance |
| `p` | physical error rate |
| `code_task` | `surface_code:rotated_memory_z` |

Instances: d = 3 and 5 at p = 0.005, 0.01, 0.02.

| Solver | `value` fields (and `extra`) |
|---|---|
| `qec-stim` | as for the repetition code |
| `qec-baseline` | as for the repetition code |

Checked: at p = 0.005, distance 5 beats distance 3. References: Fowler et al., Phys. Rev. A 86, 032324 (2012),
doi:10.1103/PhysRevA.86.032324; Google Quantum AI, arXiv:2408.13687.
