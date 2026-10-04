# Changelog

All notable changes to `qversus`. Format: newest first, grouped Added / Changed / Fixed / Removed. Versions follow
`X.XX.XXX` (major.minor.patch, zero-padded); `pyproject.toml` carries the PEP 440 form. Tags `vX.XX.XXX`.

## [0.01.000], 2026-10-04

### Added

- The engine, moved out of the QLab product repository (where it was an internal package, `qlab`) into its own
  repository and PyPI project. Logic unchanged; imports renamed `qlab.` to `qversus.`.
  - `qversus.core`: seeded RNG and shot sampling, the `Trace` / `Step` schema (now `qversus-trace/1`, same
    shape as before), and the Qiskit step tracer.
  - `qversus.problems`: twenty formulations in six families, 119 instances.
  - `qversus.solvers`: adapters over Qiskit + Aer, PennyLane, Cirq, Stim + PyMatching, the classical baselines,
    and the opt-in IBM Quantum hardware adapter.
  - `qversus.registry`: self-registration, guarded adapter imports, the opt-in rule.
- Optional extras per framework (`qiskit`, `pennylane`, `cirq`, `stim`, `learn`, `hardware`, `all`, `dev`); the
  core depends on NumPy only.
- Tests: core (RNG, trace, bit order), registry (catalogue, a classical baseline and a quantum method per
  problem, the opt-in guard), and the physics checks of every problem against its closed form. 71 pass.
- Documentation wiki: architecture, the problem catalogue with per-problem parameters and result fields, one page
  per framework adapter, guides (quick start, adding a solver or a problem, releasing).
- CI (lint, tests, a core-only install check, repository guards, version coherence) and trusted publishing to
  PyPI.

### Verified

- The 119 instances run through this package with the seed and shot count of QLab's committed records: 113
  reproduce every value, count, amplitude, Bloch vector and circuit exactly; the other 6 (the repetition code)
  had been recorded by an earlier version of the Stim adapter, and this package reproduces the original
  implementation's current output for them exactly.
