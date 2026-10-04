"""Core tests: pure NumPy, no quantum SDK, so they run on a core-only install."""

from __future__ import annotations

import json

import numpy as np

from qversus.core.rng import make_rng, sample_counts
from qversus.core.trace import SCHEMA_VERSION, Step, Trace, amp


def test_amp_rounds_complex():
    a = amp(0.7071067811 + 0j)
    assert a == {"re": 0.707107, "im": 0.0}


def test_sample_counts_is_seed_deterministic():
    probs = np.array([0.5, 0.0, 0.0, 0.5])  # Bell Phi+: only 00 and 11
    c1 = sample_counts(probs, shots=1000, seed=42)
    c2 = sample_counts(probs, shots=1000, seed=42)
    assert c1 == c2
    assert set(c1) <= {"00", "11"}
    assert sum(c1.values()) == 1000


def test_sample_counts_key_is_the_basis_index_in_binary():
    # All weight on basis index 1 of two qubits: qubit 0 is |1>, qubit 1 is |0>. The key is the index in
    # binary, highest qubit leftmost, so it reads "01".
    probs = np.array([0.0, 1.0, 0.0, 0.0])
    assert sample_counts(probs, shots=10, seed=1) == {"01": 10}


def test_make_rng_is_reproducible():
    assert make_rng(7).integers(0, 1000, 5).tolist() == make_rng(7).integers(0, 1000, 5).tolist()


def test_trace_roundtrip_and_bytes():
    step = Step(0, "init", [], {"en": "x", "es": "x"}, [amp(1 + 0j)], [[0.0, 0.0, 1.0]], [1.0])
    tr = Trace(case_id="t", title={"en": "T", "es": "T"}, concept={"en": "", "es": ""}, qubits=1,
               steps=[step], measurements={"counts": {"0": 10}, "shots": 10}, circuit_ops=[],
               provenance={"engine": "x", "engine_version": "0", "seed": 42, "lane": "live", "ran_on": "sim"})
    d = tr.to_dict()
    assert d["schema_version"] == SCHEMA_VERSION == "qversus-trace/1"
    assert tr.nbytes() == len(json.dumps(d, ensure_ascii=False).encode("utf-8"))


def test_import_core_does_not_import_a_quantum_sdk():
    import sys

    import qversus.core  # noqa: F401

    assert "qiskit" not in sys.modules or "qversus.core.circuit_trace" in sys.modules
