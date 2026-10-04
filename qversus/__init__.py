"""qversus: canonical quantum-computing problems, solved by real frameworks next to classical baselines.

A `Problem` is a formulation (Grover search, MaxCut, H2 ground state, a surface-code memory, ...) with a
set of `Instance`s. A `Solver` is a thin adapter that attacks a problem with ONE real framework (Qiskit +
Aer, PennyLane, Cirq, Stim + PyMatching) or with a classical method, and returns the same `SolverResult`
shape whatever the framework. The registry pairs them, so putting a quantum method next to the classical
baseline that is usually still more practical is one loop, not a per-framework script.

Circuit-model solvers also return a `Trace`: a replayable, JSON-first recording of the run (the state after
every gate, per-qubit Bloch vectors, probabilities, a seeded shot histogram). A run is a pure function of
`(params, seed)`.

The core needs NumPy only. Each framework is an optional extra; a missing framework disables only its own
adapters. See the README and docs/ for the contracts.
"""

__version__ = "0.01.000"  # display form X.XX.XXX; pyproject.toml carries the PEP 440 form 0.1.0
