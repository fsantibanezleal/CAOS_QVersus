# Changelog

All notable changes to `qversus`. Format: newest first, grouped Added / Changed / Fixed / Removed. Versions follow
`X.XX.XXX` (major.minor.patch, zero-padded); `pyproject.toml` carries the PEP 440 form. Tags `vX.XX.XXX`.

## [0.01.001], 2026-10-07

### Fixed

- The Grover texts state the classical expectation (N+1)/(M+1), not "~N/2" (#15): the concept, the module
  docstring and every instance note, which now gives its own numbers (Grover's iteration count against the
  expected queries of a random scan). `Grover.optimal_iterations` is the formula the Qiskit solver runs; a test
  ties every note to the solvers' values. No value or cost changed.

## [0.01.000], 2026-10-04

### Added

- The engine, moved out of the QLab product repository (where it was an internal package, `qlab`) into its own
  repository and PyPI project, imports renamed `qlab.` to `qversus.`, with the fixes listed below.
  - `qversus.core`: seeded RNG and shot sampling, the `Trace` / `Step` schema (now `qversus-trace/1`, same
    shape as before), and the Qiskit step tracer.
  - `qversus.problems`: twenty formulations in six families, 119 instances.
  - `qversus.solvers`: adapters over Qiskit + Aer, PennyLane, Cirq, Stim + PyMatching, the classical baselines,
    and the opt-in IBM Quantum hardware adapter.
  - `qversus.registry`: self-registration, guarded adapter imports, the opt-in rule.
- Optional extras per framework (`qiskit`, `pennylane`, `cirq`, `stim`, `learn`, `hardware`, `all`, `dev`); the
  core depends on NumPy only.
- Tests: core (RNG, trace, bit order), registry (catalogue, a classical baseline and a quantum method per
  problem, the opt-in guard, a missing framework per adapter), and the physics checks of every problem against
  its closed form. 88 pass.
- Documentation wiki: architecture, the problem catalogue with per-problem parameters and result fields, one page
  per framework adapter, guides (quick start, adding a solver or a problem, releasing).
- CI (lint, tests, a core-only install check, repository guards, version coherence) and trusted publishing to
  PyPI.

### Fixed (against the code as it was in QLab)

- A missing framework registers none of its adapters: the PennyLane, Cirq and Stim modules caught their own
  `ImportError` and registered anyway; each now imports its framework at module top, like Qiskit (#2).
- Grover labels the marked item in counts-key order (highest qubit leftmost), so `found` and the trace's
  `extra.marked` are the key that holds the item's shots; they were reversed for every item whose bit string is
  not a palindrome (#3).
- The Grover classical baseline reports the expected queries of a random scan, (N+1)/(M+1), instead of one
  seeded draw (kept as `sampled_queries`), and the worst case N - M + 1 (#4).
- The Shor texts state Gidney (2025) as the paper does: fewer than a million noisy physical qubits running an
  error-corrected computation, not "fault-tolerant qubits" (#5).
- `Trace.write_json` writes the same LF bytes on every operating system (#6).

### Verified

- At extraction, before the fixes, the 119 instances run through this package with the seed and shot count of
  QLab's committed records: 113 reproduced every value, count, amplitude, Bloch vector and circuit exactly; the
  other 6 (the repetition code) had been recorded by an earlier version of the Stim adapter, and the package
  reproduced the original implementation's current output for them exactly.
- Re-run after the fixes: 107 of 119 identical. The six Grover instances differ only in the fixed fields (the
  classical queries on all six; the labels on `grover-3-2marked` and `grover-4-10`, the two whose item bit
  strings are not palindromes), and the six repetition-code records as above. Text fields, which include the
  Shor notes, are not compared.
