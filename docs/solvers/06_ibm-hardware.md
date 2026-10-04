# 06 · IBM Quantum hardware (opt-in)

**`ibm-hardware`** (paradigm `quantum-hardware`, framework `ibm-quantum`) runs a small circuit on a real IBM
Quantum backend through `qiskit-ibm-runtime` and returns the counts with the backend in the provenance.
Install with the `hardware` extra.

## Guard rails

- **Opt-in**: `requires_opt_in = True`, so `solvers_for(problem)` never returns it; only
  `solvers_for(problem, only="ibm-hardware")` does.
- **Token**: it reports itself applicable only when `QISKIT_IBM_TOKEN` is set (optionally
  `QISKIT_IBM_INSTANCE`). The operator supplies the token, for example through an untracked `.env`. Importing
  the module never needs the token or the SDK.
- **Scope**: only problems whose circuits fit the free Open Plan budget: `state-prep` (Bell and GHZ; the W
  state has no short gate form here), `bernstein-vazirani`, `deutsch-jozsa`. The circuit is the Qiskit
  adapter's, so the physics has one source.

## What a run does

The circuit is transpiled to the backend's instruction set, sampled with `SamplerV2`, and returned as a trace
whose `provenance.ran_on` names the backend, so a consumer can set the noisy hardware histogram beside the
ideal simulator. Free tier: about ten minutes of QPU time per 28-day window (IBM Quantum Open Plan); use it for
small circuits, not sweeps.

Reference: IBM Quantum Platform documentation, quantum.cloud.ibm.com/docs.
