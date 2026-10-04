"""The quantum trace schema: the artifact contract between the engine and whatever consumes its runs.

A trace is a *replayable recording* of one circuit run: for every step (one gate / a barrier / a
measurement) we store the full statevector, the per-qubit Bloch vector, and the basis-state
probabilities, plus the final measurement histogram. A consumer (a notebook, a report, a static web app)
only reads or animates it: replay is the truth, nothing is recomputed. The schema is JSON-first, compact,
and free of any framework type, so a reader never needs Python or a quantum SDK to use it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCHEMA_VERSION = "qversus-trace/1"

# Amplitudes/Bloch coords are rounded to keep traces small and gzip-friendly; 6 decimals is well below
# any didactic precision need and keeps |state| ~ 1 to float tolerance.
ROUND = 6


def amp(z: complex) -> dict[str, float]:
    """Serialize a complex amplitude as {"re", "im"} rounded for compactness."""
    return {"re": round(float(z.real), ROUND), "im": round(float(z.imag), ROUND)}


@dataclass
class Step:
    """One animation frame: the state immediately AFTER applying `gate`."""

    index: int
    gate: str                       # e.g. "H", "CX", "RY", "barrier", "measure"
    targets: list[int]              # qubit indices the gate acts on
    label: dict[str, str]           # bilingual short caption {"en":..., "es":...}
    statevector: list[dict[str, float]]   # 2**n amplitudes as {"re","im"}
    bloch: list[list[float]]        # per-qubit reduced Bloch vector [x, y, z]
    probabilities: list[float]      # 2**n basis-state probabilities
    params: list[float] = field(default_factory=list)


@dataclass
class Trace:
    """A complete, replayable case run."""

    case_id: str
    title: dict[str, str]           # bilingual {"en","es"}
    concept: dict[str, str]         # bilingual one-paragraph "what this teaches"
    qubits: int
    steps: list[Step]
    measurements: dict              # {"counts": {bitstring: int}, "shots": int}
    circuit_ops: list[dict]         # flat op list for the diagram renderer
    provenance: dict                # {engine, engine_version, seed, lane, ran_on}
    references: list[dict] = field(default_factory=list)   # [{"label","doi"|"url"}]
    extra: dict = field(default_factory=dict)              # optional noisy/mitigated/curves blocks
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)

    def write_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Bytes, not text: write_text turns "\n" into CRLF on Windows, so a run's bytes would depend on the OS.
        path.write_bytes(json.dumps(self.to_dict(), indent=1, ensure_ascii=False).encode("utf-8"))
        return path

    def nbytes(self) -> int:
        return len(json.dumps(self.to_dict(), ensure_ascii=False).encode("utf-8"))
