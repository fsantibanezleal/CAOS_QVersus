# Solvers

Each framework lives in one adapter module, imported under a guard, so a missing framework disables only its
own solvers. The classical module needs NumPy alone; three of its baselines lazily import Qiskit (the exact
target state), PennyLane (the H2 Hamiltonian) or scikit-learn (the RBF-SVM).

| Module | Framework (pin used for committed results) | Solvers | Paradigm |
|---|---|---|---|
| `qiskit_solvers` | Qiskit 2.4.2 + qiskit-aer 0.17.2 | 16: `state-qiskit`, `chsh-qiskit`, `teleport-qiskit`, `superdense-qiskit`, `gates-qiskit`, `qrng-qiskit`, `interference-qiskit`, `dj-qiskit`, `bv-qiskit`, `simon-qiskit`, `grover-qiskit`, `qft-qiskit`, `qpe-qiskit`, `shor-qiskit`, `qaoa-qiskit`, `noise-qiskit` | quantum-sim |
| `pennylane_solvers` | PennyLane 0.45.0 | `qaoa-pennylane`, `vqe-pennylane`, `qml-pennylane` | quantum-sim |
| `cirq_solvers` | cirq-core 1.6.1 | `qaoa-cirq` | quantum-sim |
| `stim_solvers` | Stim 1.16.0 + PyMatching 2 | `qec-stim` | quantum-sim |
| `qulacs_solvers` | Qulacs 0.6 (with Qiskit to build the circuit) | `statevector-qulacs` | quantum-sim |
| `classical_solvers` | NumPy (+ the lazy imports above) | one or two per problem | classical |
| `hardware_solvers` | qiskit-ibm-runtime | `ibm-hardware` (opt-in) | quantum-hardware |

## Read in order

1. [Qiskit and Aer](solvers/01_qiskit.md)
2. [PennyLane](solvers/02_pennylane.md)
3. [Cirq](solvers/03_cirq.md)
4. [Stim and PyMatching](solvers/04_stim.md)
5. [Classical baselines](solvers/05_classical.md)
6. [IBM Quantum hardware (opt-in)](solvers/06_ibm-hardware.md)
7. [Qulacs](solvers/07_qulacs.md)
