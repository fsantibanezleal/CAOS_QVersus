"""qversus.core, the framework-free substrate (no quantum SDK imported here).

- rng:   seeded RNG and shot sampling, so a run is a pure function of (params, seed).
- trace: the quantum trace schema (the artifact contract every circuit-model solver emits).

`qversus.core.circuit_trace` (the Qiskit step tracer) is deliberately NOT imported here, so importing the
core never requires Qiskit.
"""

from qversus.core.rng import DEFAULT_SEED, make_rng, sample_counts
from qversus.core.trace import ROUND, SCHEMA_VERSION, Step, Trace, amp

__all__ = [
    "DEFAULT_SEED",
    "make_rng",
    "sample_counts",
    "ROUND",
    "SCHEMA_VERSION",
    "Step",
    "Trace",
    "amp",
]
