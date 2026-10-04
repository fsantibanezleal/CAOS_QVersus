# 05 · Classical baselines

Every problem has a classical solver, and it is the most important comparison in the package: on these
instances it is the more practical method. Where a classical method is provably exact, its result carries
`optimal = True`.

| Problem | Solver | Method |
|---|---|---|
| `single-qubit` | `bit-classical` | a classical bit: two states, one retrievable bit (the Holevo bound caps a qubit's readout at one bit too) |
| `qrng` | `qrng-classical` | a seeded pseudo-random generator: high entropy, fully deterministic |
| `interference` | `interference-classical` | a classical wave through two paths: intensity cos²(φ/2) |
| `state-prep` | `state-classical` | the target amplitudes written down directly (uses Qiskit's `Statevector` to build them) |
| `chsh` | `chsh-classical` | local hidden variables: max S = 2 |
| `teleportation` | `teleport-classical` | measure and resend: average fidelity 2/3 |
| `superdense` | `superdense-classical` | one bit per carrier |
| `deutsch-jozsa` | `dj-classical` | deterministic query algorithm |
| `bernstein-vazirani` | `bv-classical` | query each unit vector: n queries |
| `simon` | `simon-classical` | query until a collision |
| `grover` | `grover-classical` | a seeded random scan until a marked item is found |
| `qft` | `qft-classical` | the FFT: every amplitude, readable, O(N log N) |
| `qpe` | `qpe-classical` | the phase is known exactly |
| `shor` | `shor-classical` | trial division |
| `maxcut` | `maxcut-bruteforce` (optimal), `maxcut-greedy` | all 2ⁿ partitions; single-flip local search |
| `vqe` | `vqe-classical` (optimal) | exact diagonalisation of the 16 × 16 Hamiltonian (uses PennyLane to build it) |
| `qml` | `qml-classical` | scikit-learn RBF-kernel SVC on the same split |
| `noise` | `noise-classical` | the exact noiseless value |
| `qec-repetition`, `qec-surface` | `qec-baseline` | one unprotected qubit under the same noise for the same number of rounds |

Reading a comparison: the classical baseline is not a straw man. When it wins, that is the result; the quantum
methods' value at this scale is the phenomenon they demonstrate (nonlocality, interference, a query
separation, a threshold) and the scaling argument, stated as such.
