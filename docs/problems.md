# Problems

Twenty-two formulations in seven families, 131 instances. Each page lists, per problem, the instance parameters,
the result fields of each solver, the closed-form facts the test suite asserts, and the primary references.

| Problem | Family | Metric | Instances | Quantum solvers | Classical baseline |
|---|---|---|---|---|---|
| `single-qubit` | fundamentals | Bloch vector of the prepared state | 6 | `gates-qiskit` | `bit-classical` |
| `qrng` | fundamentals | Shannon entropy (bits) | 6 | `qrng-qiskit` | `qrng-classical` |
| `interference` | fundamentals | P(0) = cos²(φ/2) | 6 | `interference-qiskit` | `interference-classical` |
| `bb84` | fundamentals | QBER of the sifted key | 6 | `bb84-qiskit` | `bb84-classical` |
| `state-prep` | entanglement | prepared state fidelity | 7 | `state-qiskit` | `state-classical` |
| `chsh` | entanglement | CHSH value S | 6 | `chsh-qiskit` | `chsh-classical` |
| `teleportation` | entanglement | teleportation fidelity | 6 | `teleport-qiskit` | `teleport-classical` |
| `superdense` | entanglement | bits decoded per qubit sent | 4 | `superdense-qiskit` | `superdense-classical` |
| `deutsch-jozsa` | oracle algorithms | constant-or-balanced verdict | 6 | `dj-qiskit` | `dj-classical` |
| `bernstein-vazirani` | oracle algorithms | recovered hidden string | 6 | `bv-qiskit` | `bv-classical` |
| `simon` | oracle algorithms | recovered period s | 6 | `simon-qiskit` | `simon-classical` |
| `grover` | flagship algorithms | marked item found | 6 | `grover-qiskit` | `grover-classical` |
| `qft` | flagship algorithms | Fourier transform of the input | 6 | `qft-qiskit` | `qft-classical` |
| `qpe` | flagship algorithms | estimated eigenphase φ | 6 | `qpe-qiskit` | `qpe-classical` |
| `shor` | flagship algorithms | factors of N | 6 | `shor-qiskit` | `shor-classical` |
| `maxcut` | variational | cut value | 6 | `qaoa-qiskit`, `qaoa-pennylane`, `qaoa-cirq` | `maxcut-bruteforce`, `maxcut-greedy` |
| `vqe` | variational | ground-state energy (Hartree) | 6 | `vqe-pennylane` | `vqe-classical` |
| `qml` | variational | classification accuracy | 6 | `qml-pennylane` | `qml-classical` |
| `noise` | noise and QEC | ⟨Z₀Z₁⟩ (ideal 1) | 6 | `noise-qiskit` (Aer) | `noise-classical` |
| `qec-repetition` | noise and QEC | logical error rate | 6 | `qec-stim` | `qec-baseline` |
| `qec-surface` | noise and QEC | logical error rate | 6 | `qec-stim` | `qec-baseline` |
| `compilation` | compilation | two-qubit gates after compiling to {CX, RZ, SX, X} | 6 | `compile-qiskit`, `compile-pytket` | `compile-rebase` |

## Families

1. [Fundamentals](problems/01_fundamentals.md): single-qubit gates, quantum randomness, interference, BB84 key distribution.
2. [Entanglement](problems/02_entanglement.md): Bell, GHZ and W states, the CHSH inequality, teleportation, superdense coding.
3. [Oracle algorithms](problems/03_oracle-algorithms.md): Deutsch-Jozsa, Bernstein-Vazirani, Simon.
4. [Flagship algorithms](problems/04_flagship-algorithms.md): Grover, the QFT, phase estimation, Shor (N = 15).
5. [Variational](problems/05_variational.md): QAOA on MaxCut, VQE on H2, a quantum-kernel classifier.
6. [Noise and error correction](problems/06_noise-and-qec.md): depolarising noise with zero-noise extrapolation, repetition and surface codes.
7. [Compilation](problems/07_compilation.md): QFT, a Grover iteration, a redundant GHZ chain, a full adder and a random circuit compiled to a native gate set by Qiskit and pytket.

Every solver result also carries `cost.wall_ms` and bilingual `notes`; they are not repeated in the tables.
