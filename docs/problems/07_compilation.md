# 07 · Compilation

## `compilation`: the same unitary in fewer two-qubit gates

A circuit written in convenient gates (H, controlled phases, Toffolis, swaps) is compiled to the IBM-like native
set {CX, RZ, SX, X}. Translating gate by gate is always correct but wasteful; an optimising compiler resynthesises
the circuit, cancels redundant gates and folds trailing swaps into a relabelling of the output wires. Two-qubit
gates dominate the error of today's devices, so their count is the metric; depth and total gates are reported
beside it. Every result is checked to be the source unitary up to a global phase. This is classical software for
quantum hardware: no quantum advantage is claimed.

The circuits are framework-free op lists (`{"gate", "targets", "params"}`, little-endian), built by
`source_circuit(params)`. The module simulates op lists with NumPy (`unitary`), so the equivalence check depends
on none of the compilers it checks; the simulator equals Qiskit's `Operator` to 1e-12 on every gate it knows.
Depth is the longest chain of gates on any wire, the same definition for every solver.

| Parameter | Meaning |
|---|---|
| `kind` | `qft`, `grover` (one iteration), `ghz-redundant`, `adder` (full adder) or `random` |
| `n` | qubits |
| `marked` | the item a Grover iteration marks |
| `gates`, `seed` | length and seed of a random circuit (gates from H, X, S, T, S†, RZ, RX, CX, CZ, CP) |

Instances: `comp-qft3`, `comp-qft4`, `comp-grover3` (marks 5), `comp-ghz5` (a GHZ chain with gates that cancel),
`comp-adder` (two Toffolis), `comp-random4` (30 gates, seed 7).

| Solver | Method |
|---|---|
| `compile-qiskit` | Qiskit's preset pass manager at `optimization_level=3`, `basis_gates` {CX, RZ, SX, X}, no coupling map; emits the trace of the compiled circuit |
| `compile-pytket` | pytket `FullPeepholeOptimise`, then `AutoRebase` to the same set and `RemoveRedundancies` |
| `compile-rebase` | every source gate replaced by its textbook decomposition, nothing merged (the classical baseline) |

Every solver reports `two_qubit`, `depth`, `gates`, `equivalent`, `output_wires` (the wire logical qubit i is
read on at the end), `relabels_wires`, the `source` and `rebased` counts, and `two_qubit_saved` against the
rebase. The Qiskit trace's `extra` holds the source op list and the three sets of counts.

Results (seed 42, CX / depth / gates):

| Instance | Source | Gate by gate | Qiskit level 3 | pytket |
|---|---|---|---|---|
| `comp-qft3` | 4 / 6 / 7 | 9 / 20 / 27 | 6 / 15 / 21 | 6 / 16 / 24 |
| `comp-qft4` | 8 / 8 / 12 | 18 / 28 / 48 | 12 / 22 / 36 | 12 / 25 / 39 |
| `comp-grover3` | 2 / 11 / 23 | 12 / 51 / 85 | 12 / 28 / 47 | 12 / 33 / 50 |
| `comp-ghz5` | 8 / 19 / 21 | 8 / 37 / 39 | 4 / 7 / 7 | 4 / 7 / 7 |
| `comp-adder` | 5 / 6 / 8 | 15 / 29 / 48 | 11 / 21 / 33 | 11 / 21 / 33 |
| `comp-random4` | 11 / 16 / 30 | 14 / 37 / 80 | 14 / 31 / 56 | 14 / 30 / 53 |

The source column counts its own gates (a Toffoli is one gate on three wires), so it is not comparable with the
compiled columns. Both optimisers remove the QFT's swaps (the outputs are relabelled, `output_wires` [3, 2, 1, 0]
on four qubits) and every redundant pair of the GHZ chain; on the Grover iteration and the random circuit they
save depth and single-qubit gates but no CX.

Checked: every compiled circuit is the source unitary up to a global phase, uses only {CX, RZ, SX, X}, and is no
worse than the gate-by-gate translation in CX count or depth; both optimisers reduce the redundant GHZ to its 4
CX and fold the QFT-4 swaps into the wiring; each decomposition rule equals its gate; the NumPy simulator equals
Qiskit's. References: Sivarajah et al., Quantum Sci. Technol. 6, 014003 (2021), doi:10.1088/2058-9565/ab8e92;
Javadi-Abhari et al., Quantum computing with Qiskit (2024), arxiv.org/abs/2405.08810; Nielsen and Chuang (2010),
§4.3 and Fig. 4.9.
