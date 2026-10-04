# 01 · Problem and Instance

A `Problem` (`qversus/problems/base.py`) is a solver-agnostic formulation. It imports no quantum framework,
so the whole catalogue loads on a NumPy-only install.

| Member | Type | Meaning |
|---|---|---|
| `id` | `str` | registry key, e.g. `"maxcut"` |
| `title`, `concept` | `{"en","es"}` | name and a one-paragraph statement of what the problem teaches |
| `category` | `str` | family: `fundamentals`, `entanglement`, `oracle-algorithms`, `flagship-algorithms`, `variational`, `noise-and-qec` |
| `metric` | `{"en","es"}` | the quantity the solvers report (energy, cut value, logical error rate, ...) |
| `references` | `list[{"label", "doi" or "url"}]` | primary sources for the formulation |
| `live_capable` | `bool` | honest hint: the circuit is small and noise-free, with no optimisation loop and no mid-circuit feed-forward, so a consumer could re-simulate it interactively |
| `instances()` | `list[Instance]` | the parameter regimes; six where a meaningful parametric family exists |
| `instance(id)` | `Instance` | look one up (`None` returns the first); unknown ids raise `KeyError` naming the known ones |

An `Instance` is `{id, title, params, note}`: `params` is the full, problem-specific parameter vector (graph
edges, marked items, bond length, code distance and physical error rate, ...); `note` says in one bilingual
line what the regime shows. The parameter schema of every problem is listed in [../problems.md](../problems.md).

A problem may expose formulation helpers that solvers share, for example `MaxCut.cut_value(edges,
bitstring)`, so the scoring of an answer lives with the formulation and not in each adapter.

```python
from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem


@register_problem
class Parity(Problem):
    id = "parity"
    category = "fundamentals"
    title = {"en": "Parity of a bit string", "es": "Paridad de una cadena de bits"}
    concept = {"en": "...", "es": "..."}
    metric = {"en": "parity bit", "es": "bit de paridad"}

    def instances(self) -> list[Instance]:
        return [Instance("p-101", {"en": "101", "es": "101"}, {"n": 3, "bits": "101"})]
```

Read next: [02 · Solver and SolverResult](02_solver-and-result.md).
