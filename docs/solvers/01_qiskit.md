# 01 · Qiskit and Aer

**Qiskit** (IBM, Apache-2.0) is the most widely used circuit-model SDK: circuits, operators, primitives and a
Rust-accelerated transpiler. Its high-performance simulator is the separate **qiskit-aer** package
(statevector, density-matrix, MPS, stabiliser and tensor-network methods, plus noise models). Install with the
`qiskit` extra.

## What the adapters use

- **Exact simulation without shots**: `qiskit.quantum_info.Statevector` evolves the state exactly; values
  (fidelities, ⟨C⟩ for QAOA, CHSH correlators, P(0) of the interferometer) are read from it, and the histogram
  is sampled afterwards with the seeded generator. So results do not depend on a simulator's sampling.
- **The step tracer** (`qversus.core.circuit_trace`): replays a `QuantumCircuit` instruction by instruction,
  recording amplitudes, reduced Bloch vectors (`partial_trace`, then `expectation_value` of X, Y, Z) and
  probabilities. Every circuit adapter funnels through it.
- **Observables**: `SparsePauliOp` (the MaxCut cost Hamiltonian), `Pauli` (parities and correlators),
  `state_fidelity` (teleportation).
- **Noise**: `AerSimulator(method="density_matrix")` with a `NoiseModel` of depolarising errors; the noisy
  expectation is exact (no shot noise), which isolates the effect of noise from sampling error.
- **Shor's modular multiplication**: a `UnitaryGate` built from the permutation matrix of x → a·x mod 15.

## The 2.x API

The 1.0 release ended the metapackage era: `qiskit.opflow` and `qiskit.algorithms` were removed, so pre-1.0
VQE and QAOA tutorials do not run. Execution on hardware goes through the V2 primitives (`SamplerV2`,
`EstimatorV2`) and `BackendV2`. The adapters here avoid both removed modules: QAOA is a grid search over the
exact expectation, which needs no optimiser package.

## When it is the right tool

Teaching, the broadest ecosystem, IBM hardware, and noise simulation. Not the best for autodiff-heavy
variational work (PennyLane) or the fastest small-circuit loops.

References: Qiskit documentation, docs.quantum.ibm.com; Javadi-Abhari et al., "Quantum computing with
Qiskit", arXiv:2405.08810 (2024).
