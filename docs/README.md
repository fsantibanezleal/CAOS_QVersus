# qversus documentation

`qversus` is a small engine with one execution path: formulations (`Problem`) are attacked by adapters over
real frameworks and by classical methods (`Solver`), paired by a registry, and every circuit-model run is
recorded as a replayable `Trace`. This wiki documents the contracts, the twenty-one problems, the adapters and
how to extend or release the package.

| Section | What it answers |
|---|---|
| [Architecture](architecture.md) | The abstractions, the registry, the trace schema, reproducibility and bit order |
| [Problems](problems.md) | The catalogue: per problem, its parameters, the result fields of each solver, and the closed-form checks the tests enforce |
| [Solvers](solvers.md) | Each framework adapter: what it builds, the API it relies on, when it is the right tool |
| [Guides](guides.md) | Quick start, adding a solver, adding a problem, releasing to PyPI |

Conventions used throughout: amplitudes and probabilities are indexed with Qiskit's little-endian
convention (qubit 0 is the least significant bit of the basis index); a count key is that index written in
binary, highest qubit leftmost. Text meant for people (titles, concepts, notes, verdicts) is bilingual
`{"en": ..., "es": ...}`.
