# 02 · Solver and SolverResult

A `Solver` (`qversus/solvers/base.py`) wraps **one** framework or one classical method. Concrete solvers set
four class attributes and implement two methods.

| Member | Meaning |
|---|---|
| `name` | unique registry key, e.g. `"qaoa-cirq"` |
| `label` | bilingual display label |
| `framework` | `"qiskit"`, `"qiskit-aer"`, `"pennylane"`, `"cirq"`, `"stim"`, `"classical:numpy"`, `"classical:sklearn"`, `"ibm-quantum"` |
| `paradigm` | `quantum-sim`, `quantum-hardware` or `classical` |
| `requires_opt_in` | `True` for adapters that cost money or queue time; see [03](03_registry-and-extension.md) |
| `applicable(problem) -> bool` | which problems the adapter handles (usually by `id`) |
| `run(problem, instance, seed, shots) -> SolverResult` | the **only** method that touches the framework |

## SolverResult, the uniform output

| Field | Content |
|---|---|
| `solver`, `label`, `framework`, `paradigm` | copied from the adapter |
| `value` | the answer, problem-specific: `{"cut": 4, "bitstring": "0101"}`, `{"energy": -1.137}`, `{"logical_error_rate": 0.002}` |
| `cost` | what it took: `wall_ms` always; `qubits`, `shots`, `depth`, `gates`, `oracle_queries`, `evaluations` when meaningful |
| `notes` | bilingual one-line reading of the result |
| `trace` | a `Trace` for circuit-model solvers, else `None` |
| `optimal` | `True` when the classical method is provably exact (brute force, exact diagonalisation) |
| `extra` | larger auxiliary data: an optimisation landscape, a ZNE curve, kernel sizes, the Stim task name |

Because the shape is uniform, a consumer compares Qiskit, PennyLane, Cirq, Stim and the classical baselines
with one code path, and a new adapter is picked up with no change anywhere else.

## The three paradigms

- **`quantum-sim`**: a quantum method simulated on a classical computer (exactly, or with a noise model).
- **`quantum-hardware`**: the same method run on a real QPU; the trace provenance names the backend.
- **`classical`**: the baseline. Every problem has one, and it is the comparison that keeps the catalogue
  honest: at these sizes it is the more practical method, and the quantum value lies in the phenomenon or the
  scaling argument, not in the wall time.

Two framework adapters on the same problem are also a correctness check: MaxCut runs QAOA on Qiskit,
PennyLane and Cirq with different Hamiltonian conventions and code paths; they must agree on the cut.

Read next: [03 · Registry and extension](03_registry-and-extension.md).
