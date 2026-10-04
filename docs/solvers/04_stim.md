# 04 · Stim and PyMatching

**Stim** (Gidney, Apache-2.0) is a Clifford (stabiliser) circuit simulator. By the Gottesman-Knill theorem a
Clifford circuit is simulable in polynomial time, and Stim samples circuits with thousands of qubits and
millions of shots per second, which is what error-correction studies need. **PyMatching** decodes them by
minimum-weight perfect matching. Install with the `stim` extra.

## The adapter

**`qec-stim`** serves both `qec-repetition` and `qec-surface`:

1. `stim.Circuit.generated(task, rounds=d, distance=d, **noise)` builds the memory experiment
   (`repetition_code:memory` or `surface_code:rotated_memory_z`) with its noise parameters.
2. `circuit.compile_detector_sampler(seed=seed)` samples detection events and the logical observable flips
   (30,000 shots).
3. `pymatching.Matching.from_detector_error_model(circuit.detector_error_model(decompose_errors=True))` builds
   the decoder from Stim's own error model; `decode_batch` predicts the observable flips.
4. The logical error rate is the fraction of shots where the prediction disagrees with the true flip.

This is the standard Stim, detector error model, PyMatching toolchain used in surface-code threshold studies.

Reproducibility: Stim documents that a seeded sampler gives identical results only for the exact same Stim
version on the exact same machine, and deliberately changes its seeding between versions. Pin it.

## When it is the right tool

Clifford circuits, stabiliser codes, thresholds and decoders, at sizes no state-vector simulator reaches. Not a
general simulator: any non-Clifford gate (T, Toffoli, arbitrary rotations) needs a state-vector or
tensor-network engine.

References: Gidney, "Stim: a fast stabilizer circuit simulator", Quantum 5, 497 (2021),
doi:10.22331/q-2021-07-06-497; Higgott and Gidney, "Sparse Blossom", arXiv:2303.15933 (PyMatching 2).
