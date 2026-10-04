# 03 · Registry and extension

`qversus/registry.py` holds two dictionaries filled by decorators:

- `@register_problem` keys a `Problem` subclass by `id`; `@register_solver` keys a `Solver` subclass by `name`.
- `get_problem(id)` instantiates one problem; `all_problems()` and `all_solvers()` return the classes.
- `solvers_for(problem, only=None)` instantiates every solver whose `applicable(problem)` is true.

The first call imports `qversus.problems` and `qversus.solvers`, whose `__init__` modules import every
formulation and every adapter. Registration is therefore automatic and order-independent.

## Guarded adapter imports

`qversus/solvers/__init__.py` imports each adapter module inside its own `try`. If a framework is missing
(PennyLane not installed, say), only that module fails; a warning names it; every other adapter registers.
`qversus.solvers.LOADED` maps each framework's display name to whether it loaded. This is what lets the
extras stay optional.

## The opt-in rule

A solver with `requires_opt_in = True` is never returned by `solvers_for(problem)`; it is returned only by
`solvers_for(problem, only="<its name>")`. The IBM hardware adapter additionally reports itself applicable
only when `QISKIT_IBM_TOKEN` is set. Running "every solver" therefore never queues a job on a QPU or spends
budget.

## Extension contract

| To add | You write | You change elsewhere |
|---|---|---|
| a framework or a method | one `Solver` subclass + `@register_solver`, and one line in `_ADAPTER_MODULES` if it is a new module | nothing |
| a problem | one `Problem` subclass + `@register_problem`, one import line in `problems/__init__.py` | nothing: applicable solvers attach themselves; add a classical baseline if the family is new |
| a hardware backend | one `Solver` with `paradigm = QUANTUM_HARDWARE` and `requires_opt_in = True` | nothing: same result and trace shape |

Recipes with code: [../guides/02_add-a-solver.md](../guides/02_add-a-solver.md),
[../guides/03_add-a-problem.md](../guides/03_add-a-problem.md).

Read next: [04 · Trace schema](04_trace-schema.md).
