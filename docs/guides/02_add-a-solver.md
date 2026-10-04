# 02 · Add a solver

A solver wraps one framework (or one classical method) and returns a `SolverResult`. Nothing else changes.

## 1. Write the adapter

`qversus/solvers/myfw_solvers.py`:

```python
"""MyFramework adapters."""

from __future__ import annotations

import time

import myframework  # the framework import sits at module top: if it fails, only this module is skipped

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult


@register_solver
class MyFrameworkGHZ(Solver):
    name = "state-myfw"
    label = {"en": "GHZ circuit · MyFramework", "es": "Circuito GHZ · MyFramework"}
    framework = "myframework"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "state-prep"

    def run(self, problem: Problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        t0 = time.perf_counter()
        fidelity = myframework.simulate_ghz(instance.params["n"], seed=seed)   # your framework call
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"fidelity": round(float(fidelity), 6)},
            cost={"wall_ms": round((time.perf_counter() - t0) * 1e3, 3), "qubits": instance.params["n"]},
            notes={"en": "...", "es": "..."},
        )
```

Rules: the framework is touched only inside the module; `run` is a pure function of its arguments and the
seed; bilingual `notes`; `cost.wall_ms` always present. If the method is a circuit, build it in Qiskit and use
`qversus.core.circuit_trace` to return a `Trace`, so the new solver's trace has the shape of every other.

## 2. Register the module

Add one line to `_ADAPTER_MODULES` in `qversus/solvers/__init__.py`:

```python
("qversus.solvers.myfw_solvers", "MyFramework"),
```

## 3. Declare the dependency

Add an extra in `pyproject.toml` (`myfw = ["myframework>=X.Y"]`) and add it to `all` and `dev`.

## 4. Test it

Add a test in `tests/test_physics.py` that runs the solver through the registry and checks a closed form (a
fidelity of 1, an energy within chemical accuracy, agreement with another adapter on the same instance), and
document the adapter in `docs/solvers/`.

## Hardware or paid backends

Set `paradigm = QUANTUM_HARDWARE` and `requires_opt_in = True`, make `applicable` return `False` when the
credential is absent, and import the provider SDK inside `run`. Name the backend in `trace.provenance["ran_on"]`.
