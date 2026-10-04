"""Solver adapters, each subclass wraps ONE real framework to attack a problem.

A `Solver` is the plug-in seam of the whole engine: adding a framework = one new subclass + one
`@register_solver` line, with zero edits to the core, the pipeline, the registry mechanism, or the web.
Every adapter returns the same `SolverResult` shape (value + cost + optional replay trace + bilingual
notes), so the comparison panel, the gate and the manifest treat Qiskit, PennyLane, Cirq, Stim and the
classical baselines identically. There is exactly one execution path, "no parches que ejecutan todo por
separado."
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from qversus.core.trace import Trace
from qversus.problems.base import Instance, Problem

# Paradigm of a solver: drives how a consumer labels the result and the honesty framing.
QUANTUM_SIM = "quantum-sim"          # exact/noisy simulation of a quantum method on a classical computer
QUANTUM_HARDWARE = "quantum-hardware"  # ran on a real QPU (committed result + provenance)
CLASSICAL = "classical"              # the honest "still more practical" baseline
PARADIGMS = (QUANTUM_SIM, QUANTUM_HARDWARE, CLASSICAL)


@dataclass
class SolverResult:
    """The uniform adapter output."""

    solver: str                      # unique key, e.g. "qaoa-qiskit"
    label: dict[str, str]            # bilingual tab label, e.g. {"en":"QAOA · Qiskit"}
    framework: str                   # "qiskit" | "pennylane" | "cirq" | "stim" | "classical:numpy" …
    paradigm: str                    # one of PARADIGMS
    value: dict                      # problem-specific answer ({"energy":…} / {"cut":…,"bitstring":…} …)
    cost: dict                       # {wall_ms, qubits?, shots?, gates?, depth?, calls?}
    notes: dict[str, str] = field(default_factory=dict)   # bilingual one-liner on the method/result
    trace: Trace | None = None       # optional step animation (circuit-model solvers)
    optimal: bool = False            # True for an exact classical baseline (provably optimal)
    extra: dict = field(default_factory=dict)             # curves / landscapes / kernel matrices …


class Solver(ABC):
    """Base adapter. Concrete solvers set the class attributes and implement `run`."""

    name: str = "solver"             # unique registry key
    label: dict[str, str] = {"en": "Solver", "es": "Solver"}
    framework: str = "?"
    paradigm: str = QUANTUM_SIM
    # Real-hardware / paid adapters set this True so they never run in a default `--all`; the pipeline
    # only invokes them when explicitly named (`--solver <name>`). Keeps QPU cost/queue strictly opt-in.
    requires_opt_in: bool = False

    def applicable(self, problem: Problem) -> bool:
        """Override to declare which problems this adapter handles (default: by category allow-list)."""
        return True

    @abstractmethod
    def run(self, problem: Problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        """Run the method on one instance and return the uniform result."""
