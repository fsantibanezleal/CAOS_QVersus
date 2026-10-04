# 03 · Add a problem

## 1. Write the formulation

`qversus/problems/my_problem.py`: subclass `Problem`, set the identity attributes (bilingual `title`,
`concept`, `metric`; `category`; `references` with DOIs or URLs of primary sources; an honest `live_capable`),
and implement `instances()`. Aim for six instances where the problem has a meaningful parametric family, so
the regimes show how the answer changes; a single honest benchmark is fine otherwise. Import no quantum
framework here.

```python
@register_problem
class MyProblem(Problem):
    id = "my-problem"
    category = "fundamentals"
    title = {"en": "...", "es": "..."}
    concept = {"en": "...", "es": "..."}
    metric = {"en": "...", "es": "..."}
    references = [{"label": "Author, Title (year)", "doi": "10.xxxx/yyyy"}]
    live_capable = True

    def instances(self) -> list[Instance]:
        return [Instance(f"mp-{k}", {"en": f"k = {k}", "es": f"k = {k}"}, {"n": 2, "k": k},
                         {"en": "what this regime shows", "es": "qué muestra este régimen"}) for k in range(6)]
```

## 2. Register it

Add the module to the import list in `qversus/problems/__init__.py` and to `__all__`.

## 3. Give it solvers, including a classical baseline

Existing adapters attach themselves when their `applicable()` says so. A new family usually needs a new
quantum adapter and always needs a classical one: the catalogue's rule is that every problem is compared with a
classical method, and `tests/test_registry.py` enforces it.

## 4. Test and document

A physics test against the closed form; the problem in `docs/problems.md` and its family page (parameters,
result fields, what the test checks, references).
