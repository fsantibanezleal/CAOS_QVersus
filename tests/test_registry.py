"""Registry tests: the catalogue, the pairing of problems with solvers, and the opt-in guard."""

from __future__ import annotations

import subprocess
import sys

import pytest

from qversus.registry import all_problems, all_solvers, get_problem, solvers_for
from qversus.solvers.base import CLASSICAL, PARADIGMS, QUANTUM_HARDWARE

EXPECTED_PROBLEMS = {
    "state-prep", "maxcut", "bernstein-vazirani", "deutsch-jozsa", "simon", "grover", "qft", "qpe", "shor",
    "vqe", "qml", "noise", "qec-repetition", "qec-surface", "chsh", "teleportation", "superdense",
    "single-qubit", "qrng", "interference",
}


def test_catalogue_has_the_twenty_problems():
    assert set(all_problems()) == EXPECTED_PROBLEMS


def test_unknown_problem_names_the_known_ones():
    with pytest.raises(KeyError, match="known"):
        get_problem("no-such-problem")


@pytest.mark.parametrize("problem_id", sorted(EXPECTED_PROBLEMS))
def test_every_problem_has_instances_with_bilingual_text(problem_id):
    problem = get_problem(problem_id)
    insts = problem.instances()
    assert insts, problem_id
    assert len({i.id for i in insts}) == len(insts), "instance ids must be unique"
    for text in (problem.title, problem.concept, problem.metric):
        assert set(text) == {"en", "es"} and all(text.values()), problem_id
    for inst in insts:
        assert set(inst.title) == {"en", "es"}


def test_every_solver_declares_a_known_paradigm():
    for name, cls in all_solvers().items():
        assert cls.paradigm in PARADIGMS, name


@pytest.mark.parametrize("problem_id", sorted(EXPECTED_PROBLEMS))
def test_every_problem_is_attacked_by_a_quantum_method_and_a_classical_baseline(problem_id):
    pytest.importorskip("qiskit")
    pytest.importorskip("pennylane")
    pytest.importorskip("stim")
    problem = get_problem(problem_id)
    paradigms = {s.paradigm for s in solvers_for(problem)}
    assert CLASSICAL in paradigms, f"{problem_id} has no classical baseline"
    assert paradigms - {CLASSICAL}, f"{problem_id} has no quantum method"


@pytest.mark.parametrize(
    "module, framework, solvers",
    [
        ("pennylane", "PennyLane", ["vqe-pennylane", "qml-pennylane", "qaoa-pennylane"]),
        ("cirq", "Cirq", ["qaoa-cirq"]),
        ("stim", "Stim (QEC)", ["qec-stim"]),
        ("qulacs", "Qulacs", ["statevector-qulacs"]),
        ("qiskit", "Qiskit + Aer", ["grover-qiskit", "qaoa-qiskit"]),
    ],
)
def test_a_missing_framework_disables_only_its_own_adapters(module, framework, solvers):
    # A fresh interpreter, because the registry is filled once per process. `sys.modules[name] = None` makes
    # `import name` raise ImportError, which is exactly what an absent framework does.
    code = f"""
import sys, warnings
sys.modules[{module!r}] = None
warnings.simplefilter("ignore")
import qversus.solvers as s
from qversus.registry import all_solvers, get_problem, solvers_for
assert s.LOADED[{framework!r}] is False, s.LOADED
registered = set(all_solvers())
assert not registered & set({solvers!r}), registered & set({solvers!r})
assert "grover-classical" in registered
assert [x.name for x in solvers_for(get_problem("grover")) if x.paradigm == "classical"] == ["grover-classical"]
print("ok")
"""
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip() == "ok", out.stderr[-2000:]


def test_hardware_adapters_are_never_in_the_default_set():
    for problem_id in EXPECTED_PROBLEMS:
        problem = get_problem(problem_id)
        assert all(s.paradigm != QUANTUM_HARDWARE for s in solvers_for(problem)), problem_id


def test_hardware_adapter_is_offered_only_when_named_and_a_token_is_set(monkeypatch):
    pytest.importorskip("qiskit")
    hw = [n for n, c in all_solvers().items() if c.paradigm == QUANTUM_HARDWARE]
    if not hw:
        pytest.skip("no hardware adapter registered in this install")
    problem = get_problem("state-prep")
    monkeypatch.delenv("QISKIT_IBM_TOKEN", raising=False)
    assert solvers_for(problem, only=hw[0]) == []          # no token: not even when named
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "not-a-real-token")   # applicability only; nothing is submitted
    assert [s.name for s in solvers_for(problem, only=hw[0])] == [hw[0]]
    assert all(s.name != hw[0] for s in solvers_for(problem))  # still never in the default set
