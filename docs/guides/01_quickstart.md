# 01 · Quick start

## Install

```bash
python -m venv .venv
.venv/Scripts/python -m pip install "qversus[all]"     # bash: .venv/bin/python
```

For results that must reproduce byte for byte, pin the frameworks exactly in your own requirements (see
[../architecture/05_reproducibility.md](../architecture/05_reproducibility.md)).

## List the catalogue and the solvers

```python
from qversus.registry import all_problems, get_problem, solvers_for

for pid in sorted(all_problems()):
    problem = get_problem(pid)
    names = [s.name for s in solvers_for(problem)]
    print(f"{pid:20} {problem.category:20} {len(problem.instances())} instances  {names}")
```

## Run every solver on one instance and compare

```python
from qversus.registry import get_problem, solvers_for

problem = get_problem("vqe")
instance = problem.instance("vqe-h2-0_74")
results = [s.run(problem, instance, seed=42, shots=2048) for s in solvers_for(problem)]

exact = next(r for r in results if r.optimal)
for r in results:
    error_mha = (r.value["energy"] - exact.value["energy"]) * 1000
    print(f"{r.solver:15} {r.value['energy']:.6f} Ha  error {error_mha:+.3f} mHa  {r.cost['wall_ms']:.1f} ms")
```

## Read a trace

```python
import json
from qversus.registry import get_problem, solvers_for

problem = get_problem("state-prep")
instance = problem.instance("ghz-3")
solver = next(s for s in solvers_for(problem) if s.name == "state-qiskit")
trace = solver.run(problem, instance, seed=42, shots=1024).trace

for step in trace.steps:                         # the state after each gate
    print(step.index, step.gate, step.targets, [round(p, 3) for p in step.probabilities])
print(trace.measurements["counts"])              # keys: basis index in binary, highest qubit leftmost
trace.write_json("ghz-3.json")                   # schema qversus-trace/1
```

## What a missing framework looks like

Without PennyLane installed, importing the registry warns `qversus solver adapter qversus.solvers.pennylane_solvers
unavailable (PennyLane): ...`, and `solvers_for(get_problem("vqe"))` returns only the classical solver. That
baseline also needs PennyLane, to build the H2 Hamiltonian, so running it raises `ImportError`: install the
`pennylane` extra for VQE. `qversus.solvers.LOADED` tells you which framework adapters loaded.

The VQE snippet above prints, with the pinned frameworks: `vqe-classical -1.137284 Ha` (the exact energy,
`optimal = True`) and `vqe-pennylane -1.137279 Ha`, an error of +0.005 mHa, well inside chemical accuracy.
