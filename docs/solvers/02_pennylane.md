# 02 · PennyLane

**PennyLane** (Xanadu, Apache-2.0) treats quantum circuits as differentiable functions that plug into
classical automatic differentiation, and ships a quantum-chemistry module. Install with the `pennylane` extra
(it brings NetworkX, which `qml.qaoa.maxcut` requires).

## The three adapters

- **`qaoa-pennylane`**: builds the MaxCut cost Hamiltonian with `qml.qaoa.maxcut(graph)` from a
  `networkx.Graph` (a list of edges is not accepted) and evaluates ⟨H_C⟩ on `default.qubit` over the same
  (γ, β) grid as the Qiskit and Cirq adapters. PennyLane's MaxCut Hamiltonian is **minimised** to maximise the
  cut (a cut edge contributes −1), so the adapter searches for the minimum and reads the cut from the most
  probable bit string. Three implementations with different conventions must agree on the cut, which is the
  cross-check.
- **`vqe-pennylane`**: `qml.qchem.molecular_hamiltonian(["H", "H"], coords)` gives the four-qubit STO-3G
  Hamiltonian; the ansatz is the Hartree-Fock state `qml.qchem.hf_state(2, 4)` followed by one
  `qml.DoubleExcitation(θ)`; θ is scanned and the minimum energy reported with the landscape.
- **`qml-pennylane`**: a fidelity kernel from `qml.AngleEmbedding` and its adjoint, evaluated for every pair of
  points, then scikit-learn's `SVC(kernel="precomputed")`. Needs the `learn` extra for scikit-learn.

## When it is the right tool

Variational algorithms, quantum machine learning, gradients and hybrid training, chemistry Hamiltonians.
Not the place for low-level transpiler control or a broad noise library.

References: PennyLane documentation and demos, pennylane.ai; Bergholm et al., "PennyLane: Automatic
differentiation of hybrid quantum-classical computations", arXiv:1811.04968.
