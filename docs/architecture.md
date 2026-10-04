# Architecture

The design goal, stated plainly: **adding a framework or a method is one adapter, never a rewrite and never
duplicated plumbing.** A formulation knows *what* to compute; an adapter knows *how*, through one framework;
neither knows the other's internals; a registry pairs them; every result has one shape.

```
qversus/
  core/rng.py            seeded generator + shot sampling (the only stochastic step)
  core/trace.py          Trace / Step dataclasses, schema qversus-trace/1
  core/circuit_trace.py  Qiskit step tracer (every circuit adapter funnels through it)
  problems/base.py       Problem ABC + Instance
  problems/<name>.py     one formulation each, @register_problem
  solvers/base.py        Solver ABC + SolverResult + the three paradigms
  solvers/<fw>_solvers.py  the adapters, @register_solver, imported under a guard
  registry.py            register_* decorators, get_problem, all_problems, solvers_for
```

## Read in order

1. [Problem and Instance](architecture/01_problem-and-instance.md): the formulation contract.
2. [Solver and SolverResult](architecture/02_solver-and-result.md): the adapter contract and the three paradigms.
3. [Registry and extension](architecture/03_registry-and-extension.md): self-registration, guarded imports, the opt-in rule.
4. [Trace schema](architecture/04_trace-schema.md): `qversus-trace/1`, field by field.
5. [Reproducibility and bit order](architecture/05_reproducibility.md): what makes a run a pure function of `(params, seed)`.
