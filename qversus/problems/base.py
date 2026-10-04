"""Problem formulations, what to compute, independent of the method that computes it.

A `Problem` declares its didactic identity (bilingual title/concept, category) and its set of
`Instance`s (the variant regimes a consumer can select between; aim for ≥6 where a meaningful
parametric family exists). It is solver-agnostic: the same problem is attacked by many `Solver`s
(quantum + classical), each a thin adapter over a real framework. Adding a problem never touches a solver.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Instance:
    """One variant regime of a problem (a full parameter vector a consumer can select)."""

    id: str
    title: dict[str, str]            # bilingual short label for the variant chip
    params: dict                     # problem-specific (graph edges, geometry, marked item, N, …)
    note: dict[str, str] = field(default_factory=dict)   # bilingual "what this regime shows"


class Problem(ABC):
    """A formulation. Concrete problems set the class attributes and implement `instances`."""

    id: str = "problem"
    title: dict[str, str] = {"en": "Problem", "es": "Problema"}
    concept: dict[str, str] = {"en": "", "es": ""}
    category: str = "fundamentals"
    # The bilingual name of the quantity the solvers compute (energy, max cut, found item, …).
    metric: dict[str, str] = {"en": "result", "es": "resultado"}
    references: list[dict] = []      # [{label, doi|url}] shared by the case
    # Is the circuit small and clean enough to re-simulate interactively (e.g. in a browser)? False when the case needs an offline-only
    # feature (optimization loop, realistic noise, mid-circuit feed-forward, >12 qubits). The gate still
    # re-checks the measured numbers; this is the case author's honest hint.
    live_capable: bool = True

    @abstractmethod
    def instances(self) -> list[Instance]:
        """The variant regimes (≥6 where a parametric family exists; a single honest benchmark otherwise)."""

    def instance(self, instance_id: str | None) -> Instance:
        items = self.instances()
        if instance_id is None:
            return items[0]
        for it in items:
            if it.id == instance_id:
                return it
        raise KeyError(f"{self.id}: no instance {instance_id!r} (have {[i.id for i in items]})")
