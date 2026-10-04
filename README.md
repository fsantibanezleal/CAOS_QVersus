# qversus

[![CI](https://github.com/fsantibanezleal/CAOS_QVersus/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/fsantibanezleal/CAOS_QVersus/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/qversus)](https://pypi.org/project/qversus/)
[![License](https://img.shields.io/github/license/fsantibanezleal/CAOS_QVersus)](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/LICENSE)

**Canonical quantum-computing problems, solved by the real frameworks next to the classical baseline that is
usually still more practical, with every run recorded as a replayable, seeded trace.**

`qversus` separates *what* to compute from *how*. A `Problem` is a formulation (Grover search, MaxCut, the H2
ground state, a surface-code memory, ...) with a set of parameter regimes (`Instance`s). A `Solver` is a thin
adapter that attacks a problem with **one** real framework (Qiskit + Aer, PennyLane, Cirq, Stim + PyMatching)
or with a classical method, and returns the same `SolverResult` shape whatever the framework. A registry pairs
them, so running a quantum method and the classical baseline side by side is one loop, not one script per
framework.

Circuit-model solvers also return a `Trace`: the state after every gate (amplitudes, per-qubit Bloch vectors,
probabilities), the circuit as a flat op list, and a seeded shot histogram. A run is a pure function of
`(params, seed)`: with the same framework versions, the same inputs give the same bytes.

The package makes no claim of quantum advantage. Every problem ships a classical baseline, and on these
textbook-scale instances the classical method wins on wall time; what the quantum methods show are real
phenomena (interference, entanglement, query separations, error-correction thresholds) at a scale a laptop
simulates exactly.

## Install

```bash
pip install qversus                 # core: NumPy only (formulations, registry, trace schema, RNG)
pip install "qversus[all]"          # every simulator-based adapter
```

| Extra | Brings | Enables |
|---|---|---|
| `qiskit` | `qiskit>=2.4,<3`, `qiskit-aer>=0.17` | the circuit adapters (16 problems), the step tracer, the Aer noise model |
| `pennylane` | `pennylane>=0.45`, `networkx` | QAOA cross-check, VQE on H2, the quantum-kernel classifier, the H2 Hamiltonian for the exact baseline |
| `cirq` | `cirq-core>=1.6` | the third QAOA implementation |
| `stim` | `stim>=1.16`, `pymatching>=2.0` | repetition and surface-code memories decoded by minimum-weight matching |
| `learn` | `scikit-learn>=1.5` | the classical RBF-SVM baseline and the precomputed-kernel SVM |
| `hardware` | `qiskit-ibm-runtime>=0.30` | the opt-in IBM Quantum adapter (real QPU, needs a token) |
| `all` | every extra except `hardware` | |

A missing framework disables only its own adapters (a warning names it); the rest of the registry works.

## Quick start

```python
from qversus.registry import get_problem, solvers_for

problem = get_problem("maxcut")
instance = problem.instance("square")            # the 4-cycle; optimum cut = 4

for solver in solvers_for(problem):              # QAOA on Qiskit, PennyLane and Cirq + two classical methods
    result = solver.run(problem, instance, seed=42, shots=2048)
    print(f"{result.paradigm:12} {result.solver:18} cut={result.value['cut']}  cost={result.cost}")
```

```python
from qversus.registry import get_problem, solvers_for

problem = get_problem("grover")
instance = problem.instance("grover-4-10")       # N = 16 items, item 10 marked
qiskit = next(s for s in solvers_for(problem) if s.framework == "qiskit")
result = qiskit.run(problem, instance, seed=42, shots=2048)

trace = result.trace.to_dict()                   # JSON-ready: steps, circuit_ops, measurements, provenance
print(result.value, trace["measurements"]["counts"])
```

More: [quick start guide](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/docs/guides/01_quickstart.md).

## The catalogue

Twenty problems in six families, 119 instances. Each has at least one quantum method and one classical baseline.

| Problem | Family | Quantum solvers | Classical baseline |
|---|---|---|---|
| `single-qubit`, `qrng`, `interference` | fundamentals | Qiskit | Bloch/bit model, PRNG, wave optics |
| `state-prep`, `chsh`, `teleportation`, `superdense` | entanglement | Qiskit | the amplitudes written down directly, local hidden variables, measure-and-resend, one bit per carrier |
| `deutsch-jozsa`, `bernstein-vazirani`, `simon` | oracle algorithms | Qiskit | query-counting classical algorithms |
| `grover`, `qft`, `qpe`, `shor` | flagship algorithms | Qiskit | linear scan, FFT, exact phase, trial division |
| `maxcut`, `vqe`, `qml` | variational | Qiskit, PennyLane, Cirq | brute force + greedy, exact diagonalisation, RBF-SVM |
| `noise`, `qec-repetition`, `qec-surface` | noise and QEC | Qiskit-Aer, Stim + PyMatching | the exact answer, the unprotected qubit |

Per-problem parameters, result fields and the closed-form checks the tests enforce:
[docs/problems](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/docs/problems.md).

## Contracts

- **`Problem` / `Instance`**: identity (id, bilingual EN/ES title and concept, category, metric, references),
  the instances, and a `live_capable` hint (small and noise-free enough to re-simulate interactively).
- **`Solver` / `SolverResult`**: `run(problem, instance, seed, shots) -> SolverResult` with `value`, `cost`,
  bilingual `notes`, an optional `trace`, `optimal` (an exact classical baseline) and `extra` (landscapes,
  curves, kernel matrices). Paradigm is one of `quantum-sim`, `quantum-hardware`, `classical`.
- **`Trace`** (schema `qversus-trace/1`): JSON-first and free of framework types, so a reader needs neither
  Python nor a quantum SDK.
- **Bit order**: amplitude and probability arrays use Qiskit's little-endian index (qubit 0 is the least
  significant bit); count keys are that index in binary, highest qubit leftmost.

Details: [docs/architecture](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/docs/architecture.md).

## Real hardware (opt-in)

The `ibm-hardware` adapter submits small circuits to IBM Quantum (Open Plan, free tier) and returns the counts
with the backend named in the provenance. It is never part of the default solver set: it is offered only when
named explicitly **and** `QISKIT_IBM_TOKEN` is set. See
[docs/solvers/06_ibm-hardware.md](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/docs/solvers/06_ibm-hardware.md).

## Development

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev]"   # bash: .venv/bin/python
python -m pytest                     # core, registry and physics tests
python -m ruff check qversus tests
python scripts/check_content_standards.py
```

CI runs lint, the tests, a core-only install check, and the repository guards on `develop` and `main`.
Releases are tagged `vX.XX.XXX` and published to PyPI by trusted publishing
([docs/guides/04_releasing.md](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/docs/guides/04_releasing.md)).

## Used by

- **QLab** ([qlab.fasl-work.com](https://qlab.fasl-work.com)): a public, didactic quantum-computing lab whose
  committed traces are produced by this engine.

## License

MIT. See [LICENSE](https://github.com/fsantibanezleal/CAOS_QVersus/blob/main/LICENSE).
