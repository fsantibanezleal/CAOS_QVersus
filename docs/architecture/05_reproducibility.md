# 05 · Reproducibility and bit order

## A run is a pure function of `(params, seed)`

State evolution is exact (`Statevector`, exact expectation values, exact diagonalisation). The only
stochastic steps are measurement sampling and the seeded draws of a few classical methods, and both go
through NumPy's PCG64 generator seeded explicitly (`qversus.core.rng.make_rng`, `sample_counts`). The same
inputs, with the same framework versions, give the same values and the same counts.

Verified at extraction: the 119 instances were run through this package with the seed and shot count of the
records the original implementation had committed. 113 reproduced every value, count, amplitude, Bloch vector
and circuit exactly; the other 6 (the repetition code) had been recorded by an earlier version of the Stim
adapter, and this package reproduces the original implementation's current output for them exactly.

What can move a result:

| Source | Effect | How to hold it still |
|---|---|---|
| framework versions | a transpiler or simulator change can alter an optimised circuit or the last digits of a value | pin exact versions in the consumer (e.g. `qiskit==2.4.2`, `qiskit-aer==0.17.2`, `pennylane==0.45.0`, `cirq-core==1.6.1`, `stim==1.16.0`) |
| Stim sampling | Stim's own documentation: a seeded sampler gives the same results only "on the exact same machine with the exact same version of Stim", and results are deliberately NOT consistent across Stim versions (the loaded build, e.g. `stim._stim_sse2` or an AVX2 variant, is part of "the same machine") | pin Stim exactly; record the machine when the bytes matter |
| wall-clock fields | `cost.wall_ms` is measured, so it differs run to run | never compare it; it is the one field that is not a function of the inputs |

## Bit order

The single convention, used everywhere:

- **Arrays** (`statevector`, `probabilities`): index `i` is the basis state whose binary expansion has qubit 0
  as its least significant bit (Qiskit's little-endian order).
- **Count keys**: the basis index written in binary, most significant bit first, so the HIGHEST qubit is the
  leftmost character and qubit 0 the rightmost: `format(i, f"0{n}b")`. Index 10 on four qubits is `"1010"`
  (qubits 3 and 1 are `|1>`).
- **Problem answers that are bit strings indexed by position** (a Bernstein-Vazirani secret, a MaxCut
  partition) state their own order in the adapter: position `u` is qubit `u`, the reverse of the count keys.
  Grover's `found` and `extra.marked` currently use this position order too, although a marked item is an
  item, not a position string; aligning them with the count keys is tracked as a defect.

Read next: [../problems.md](../problems.md).
