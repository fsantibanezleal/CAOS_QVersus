# 08 · pytket

**pytket** (Quantinuum, Apache-2.0) is the Python interface to the t|ket⟩ compiler. Install with the `pytket`
extra; the adapter needs nothing else.

## The adapter

**`compile-pytket`** builds a pytket `Circuit` from the instance's op list (angles in half-turns, pytket's unit;
the phase gate P(λ) as `U1`, the controlled phase as `CU1`), then applies three passes:

1. `FullPeepholeOptimise`: two-qubit block resynthesis, Clifford simplification, and trailing swaps folded into an
   implicit wire permutation;
2. `AutoRebase({CX, Rz, SX, X})`: onto the native set;
3. `RemoveRedundancies`: what the rebase leaves (zero rotations, adjacent inverses).

The result is read back as an op list (angles back to radians). The check takes pytket's own unitary of the
compiled circuit, which applies the implicit permutation, converts it from pytket's big-endian order (qubit 0
most significant) to qversus' little-endian order, and compares it with the NumPy unitary of the source. The
implicit permutation is reported as `output_wires`. Fields: see
[the compilation problem](../problems/07_compilation.md); `extra.compiled_ops` holds the compiled circuit.

Checked: on every instance the compiled circuit is the source unitary up to a global phase and uses only the
native set; it reduces the redundant GHZ chain to 4 CX and folds the QFT-4 swaps into the wiring.

## When it is the right tool

Retargeting one circuit to many gate sets and devices, aggressive two-qubit resynthesis, and comparing compilers.
On these small circuits pytket and Qiskit's level-3 pass manager reach the same CX counts; Qiskit's output is
slightly shallower on most, pytket's on the random circuit. Neither result is a claim about larger circuits.
