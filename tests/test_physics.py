"""Physics tests: every problem, solved through the registry by the real frameworks, against its closed form.

Skipped automatically when Qiskit is not installed (a core-only install), so `pytest` stays green there;
CI installs the `dev` extra and runs them for real.
"""

from __future__ import annotations

import pytest

qiskit = pytest.importorskip("qiskit")


def test_state_prep_bell_runs_and_traces():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("state-prep")
    inst = problem.instance("bell-phi-plus")
    solver = next(s for s in solvers_for(problem) if s.name == "state-qiskit")
    res = solver.run(problem, inst, seed=42, shots=512)
    # Bell Φ+ → only |00> and |11> populated, each ~0.5.
    final = res.trace.steps[-1].probabilities
    assert abs(final[0] - 0.5) < 1e-6 and abs(final[-1] - 0.5) < 1e-6
    assert set(res.trace.measurements["counts"]) <= {"00", "11"}


def test_bernstein_vazirani_recovers_secret_in_one_query():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("bernstein-vazirani")
    inst = problem.instance("bv-11010")
    res = {s.name: s.run(problem, inst, seed=42, shots=256) for s in solvers_for(problem)}
    assert res["bv-qiskit"].value["recovered"] == "11010"
    assert res["bv-qiskit"].value["quantum_queries"] == 1
    assert res["bv-classical"].value["recovered"] == "11010"
    assert res["bv-classical"].value["classical_queries"] == 5  # n bits → n classical queries


def test_deutsch_jozsa_constant_and_balanced():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("deutsch-jozsa")
    for iid, exp in [("dj-const0-3", "constant"), ("dj-bal-101", "balanced")]:
        inst = problem.instance(iid)
        res = {s.name: s.run(problem, inst, seed=42, shots=256) for s in solvers_for(problem)}
        assert res["dj-qiskit"].value["verdict"] == exp
        assert res["dj-qiskit"].value["quantum_queries"] == 1
        assert res["dj-classical"].value["verdict"] == exp


def test_simon_recovers_period():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("simon")
    inst = problem.instance("simon-3-101")
    res = {s.name: s.run(problem, inst, seed=42, shots=512) for s in solvers_for(problem)}
    assert res["simon-qiskit"].value["recovered"] == "101"
    assert res["simon-qiskit"].value["correct"] is True
    assert res["simon-classical"].value["recovered"] == "101"


def test_grover_finds_marked():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("grover")
    inst = problem.instance("grover-3-5")
    res = {s.name: s.run(problem, inst, seed=42, shots=512) for s in solvers_for(problem)}
    assert res["grover-qiskit"].value["found"] == "101"
    assert res["grover-qiskit"].value["correct"] is True
    assert res["grover-qiskit"].value["success_prob"] > 0.9
    assert res["grover-classical"].value["correct"] is True


@pytest.mark.parametrize("instance_id", ["grover-2-3", "grover-3-5", "grover-3-2", "grover-3-2marked",
                                         "grover-4-10", "grover-4-0"])
def test_grover_item_labels_are_the_counts_keys(instance_id):
    import re

    from qversus.registry import get_problem, solvers_for

    problem = get_problem("grover")
    inst = problem.instance(instance_id)
    n, marked = inst.params["n"], inst.params["marked"]
    res = {s.name: s.run(problem, inst, seed=42, shots=2048) for s in solvers_for(problem)}
    q = res["grover-qiskit"]
    labels = q.trace.extra["marked"]
    counts = q.trace.measurements["counts"]

    assert labels == [format(w, f"0{n}b") for w in marked]           # the item's index, in binary
    assert labels == re.findall(r"\|([01]+)⟩", inst.title["en"])      # ... which is the ket in the title
    assert all(lab in counts for lab in labels)                       # ... and a key of the histogram
    share = sum(counts[lab] for lab in labels) / q.trace.measurements["shots"]
    assert abs(share - q.value["success_prob"]) < 0.05                # the marked keys hold the success mass
    assert q.value["found"] in labels and q.value["correct"] is True
    assert res["grover-classical"].value["found"] in labels


def test_qft_matches_analytic_dft():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("qft")
    inst = problem.instance("qft-3-k5")
    res = {s.name: s.run(problem, inst, seed=42, shots=256) for s in solvers_for(problem)}
    assert res["qft-qiskit"].value["matches_dft"] is True
    assert res["qft-qiskit"].value["fidelity_vs_dft"] > 0.999
    assert res["qft-classical"].value["readable"] is True


def test_qpe_estimates_phase():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("qpe")
    inst = problem.instance("qpe-t3-1_4")  # φ = 1/4 is exactly representable in 3 bits
    res = {s.name: s.run(problem, inst, seed=42, shots=256) for s in solvers_for(problem)}
    assert abs(res["qpe-qiskit"].value["phi_estimate"] - 0.25) < 1e-9
    assert res["qpe-qiskit"].value["error"] == 0.0
    assert res["qpe-qiskit"].value["p_top"] > 0.99
    assert abs(res["qpe-classical"].value["phi_exact"] - 0.25) < 1e-9


def test_shor_factors_15():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("shor")
    inst = problem.instance("shor-15-a7")  # base 7 has order 4 mod 15
    res = {s.name: s.run(problem, inst, seed=42, shots=512) for s in solvers_for(problem)}
    assert res["shor-qiskit"].value["factors"] == [3, 5]
    assert res["shor-qiskit"].value["order"] == 4
    assert res["shor-qiskit"].value["correct"] is True
    assert res["shor-classical"].value["factors"] == [3, 5]


def test_vqe_h2_matches_fci():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("vqe")
    inst = problem.instance("vqe-h2-0_74")  # ≈ equilibrium
    res = {s.name: s.run(problem, inst, seed=42, shots=1) for s in solvers_for(problem)}
    e_vqe = res["vqe-pennylane"].value["energy"]
    e_fci = res["vqe-classical"].value["energy"]
    assert abs(e_vqe - e_fci) < 1.6e-3       # within chemical accuracy
    assert e_fci < -1.13                     # known H₂ equilibrium energy ≈ -1.137 Ha


def test_qml_quantum_kernel_classifies():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("qml")
    inst = problem.instance("qml-circles")  # nonlinear but cleanly separable
    res = {s.name: s.run(problem, inst, seed=42, shots=1) for s in solvers_for(problem)}
    assert res["qml-pennylane"].value["test_acc"] >= 0.8     # quantum kernel works…
    assert res["qml-classical"].value["test_acc"] >= 0.8     # …and so does classical (no advantage)


def test_noise_zne_reduces_error():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("noise")
    inst = problem.instance("noise-p0.02-d1")
    res = {s.name: s.run(problem, inst, seed=42, shots=1) for s in solvers_for(problem)}
    q = res["noise-qiskit"].value
    assert q["ideal"] == 1.0 and q["noisy"] < 1.0           # noise pulls the parity below 1
    assert q["residual_mitigated"] < q["residual_noisy"]    # ZNE reduces the bias
    assert res["noise-classical"].value["value"] == 1.0     # classical is exact + free


def test_qec_repetition_below_threshold():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("qec-repetition")
    r3 = {s.name: s.run(problem, problem.instance("rep-d3-p0.05"), seed=42, shots=1)
          for s in solvers_for(problem)}
    r5 = {s.name: s.run(problem, problem.instance("rep-d5-p0.05"), seed=42, shots=1)
          for s in solvers_for(problem)}
    l3 = r3["qec-stim"].value["logical_error_rate"]
    l5 = r5["qec-stim"].value["logical_error_rate"]
    assert l5 < l3                                                  # distance helps below threshold
    assert l3 < r3["qec-baseline"].value["physical_error_rate"]    # encoding beats the unprotected qubit


def test_qec_surface_below_threshold():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("qec-surface")
    stim_solver = next(s for s in solvers_for(problem) if s.name == "qec-stim")
    l3 = stim_solver.run(problem, problem.instance("surf-d3-p0.005"), seed=42, shots=1).value["logical_error_rate"]
    l5 = stim_solver.run(problem, problem.instance("surf-d5-p0.005"), seed=42, shots=1).value["logical_error_rate"]
    assert l5 < l3                                  # below threshold, distance-5 beats distance-3


def test_chsh_violates_classical_bound():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("chsh")
    solvers = solvers_for(problem)
    q = next(s for s in solvers if s.name == "chsh-qiskit")
    opt = q.run(problem, problem.instance("chsh-optimal"), seed=42, shots=1)
    prod = q.run(problem, problem.instance("chsh-product"), seed=42, shots=1)
    assert abs(opt.value["S"] - 2 * 2 ** 0.5) < 1e-3        # reaches the Tsirelson bound 2√2
    assert opt.value["exceeds_classical"] is True           # violates the classical bound
    assert prod.value["exceeds_classical"] is False         # a separable state cannot violate it
    base = next(s for s in solvers if s.name == "chsh-classical")
    assert base.run(problem, problem.instance("chsh-optimal"), seed=42, shots=1).value["max_S"] == 2.0


def test_teleportation_perfect_fidelity():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("teleportation")
    res = {s.name: s.run(problem, problem.instance("tele-generic"), seed=42, shots=1)
           for s in solvers_for(problem)}
    tq = res["teleport-qiskit"].value
    assert tq["fidelity"] > 0.999                              # perfect transfer
    assert tq["input_bloch"] == tq["output_bloch"]             # the Bloch vector hops Alice → Bob
    assert res["teleport-classical"].value["best_fidelity"] < 0.7   # classical measure-resend bound 2/3


def test_superdense_decodes_all_messages():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("superdense")
    q = next(s for s in solvers_for(problem) if s.name == "superdense-qiskit")
    for msg in ("00", "01", "10", "11"):
        res = q.run(problem, problem.instance(f"sd-{msg}"), seed=42, shots=1)
        assert res.value["decoded"] == msg and res.value["correct"] is True   # 2 bits from 1 qubit
    base = next(s for s in solvers_for(problem) if s.name == "superdense-classical")
    assert base.run(problem, problem.instance("sd-00"), seed=42, shots=1).value["bits_per_qubit"] == 1


def test_single_qubit_bloch_vectors():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("single-qubit")
    q = next(s for s in solvers_for(problem) if s.name == "gates-qiskit")
    assert q.run(problem, problem.instance("sq-x"), seed=42, shots=1).value["bloch"] == [0.0, 0.0, -1.0]
    assert q.run(problem, problem.instance("sq-h"), seed=42, shots=1).value["bloch"] == [1.0, 0.0, 0.0]
    assert q.run(problem, problem.instance("sq-hs"), seed=42, shots=1).value["bloch"] == [0.0, 1.0, 0.0]
    base = next(s for s in solvers_for(problem) if s.name == "bit-classical")
    assert base.run(problem, problem.instance("sq-x"), seed=42, shots=1).value["states"] == 2


def test_qrng_entropy():
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("qrng")
    q = next(s for s in solvers_for(problem) if s.name == "qrng-qiskit")
    assert q.run(problem, problem.instance("qrng-3"), seed=42, shots=64).value["entropy_bits"] == 3.0
    biased = q.run(problem, problem.instance("qrng-bias30"), seed=42, shots=64).value
    assert biased["uniform"] is False and biased["entropy_bits"] < 1.0    # RY(π/3) → biased coin
    cls = next(s for s in solvers_for(problem) if s.name == "qrng-classical")
    assert cls.run(problem, problem.instance("qrng-3"), seed=42, shots=64).value["deterministic"] is True


def test_interference_fringe_matches_cos2():
    import math

    from qversus.registry import get_problem, solvers_for

    problem = get_problem("interference")
    q = next(s for s in solvers_for(problem) if s.name == "interference-qiskit")
    cls = next(s for s in solvers_for(problem) if s.name == "interference-classical")
    # the H·P(φ)·H fringe is P(0) = cos²(φ/2); φ=0 → 1 (constructive), φ=π → 0 (destructive)
    assert q.run(problem, problem.instance("itf-0"), seed=42, shots=1).value["p0"] == 1.0
    assert q.run(problem, problem.instance("itf-pi"), seed=42, shots=1).value["p0"] == 0.0
    half = q.run(problem, problem.instance("itf-pi2"), seed=42, shots=1).value
    assert abs(half["p0"] - 0.5) < 1e-6 and half["fringe"] == "mixed"
    # the classical wave reproduces the same fringe (committed values are rounded to 4 decimals)
    for iid in ("itf-0", "itf-pi4", "itf-pi2", "itf-2pi3", "itf-pi"):
        phi = problem.instance(iid).params["phi"]
        assert abs(cls.run(problem, problem.instance(iid), seed=42, shots=1).value["intensity"]
                   - math.cos(phi / 2) ** 2) < 1e-3


def test_maxcut_classical_optimum_beats_or_matches_qaoa():
    from qversus.problems.maxcut import MaxCut
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("maxcut")
    inst = problem.instance("square")  # C4 → optimum cut = 4
    results = {s.name: s.run(problem, inst, seed=42, shots=512) for s in solvers_for(problem)}
    assert results["maxcut-bruteforce"].value["cut"] == 4
    assert results["maxcut-bruteforce"].optimal is True
    # QAOA cut never exceeds the classical optimum.
    assert results["qaoa-qiskit"].value["cut"] <= results["maxcut-bruteforce"].value["cut"]
    # Triangle is frustrated: optimum is 2, not 3.
    assert MaxCut().cut_value([[0, 1], [1, 2], [0, 2]], "010") == 2


@pytest.mark.parametrize("instance_id, expected", [("grover-2-3", 2.5), ("grover-3-5", 4.5), ("grover-3-2", 4.5),
                                                   ("grover-3-2marked", 3.0), ("grover-4-10", 8.5),
                                                   ("grover-4-0", 8.5)])
def test_grover_classical_reports_the_expected_queries(instance_id, expected):
    from qversus.registry import get_problem, solvers_for

    problem = get_problem("grover")
    inst = problem.instance(instance_id)
    scan = next(s for s in solvers_for(problem) if s.name == "grover-classical")
    value = scan.run(problem, inst, seed=42, shots=1).value
    n, m = inst.params["n"], len(inst.params["marked"])
    assert value["classical_queries"] == expected == (2**n + 1) / (m + 1)
    assert value["worst_case_queries"] == 2**n - m + 1
    assert 1 <= value["sampled_queries"] <= value["worst_case_queries"]

    # The seeded draws converge to it. The first marked position is the minimum of a uniform M-subset of
    # {1..N}, with variance M(N+1)(N-M) / ((M+1)^2 (M+2)); allow four standard errors of the mean.
    runs = 2000
    draws = [scan.run(problem, inst, seed=s, shots=1).value["sampled_queries"] for s in range(runs)]
    var = m * (2**n + 1) * (2**n - m) / ((m + 1) ** 2 * (m + 2))
    assert abs(sum(draws) / runs - expected) < 4 * (var / runs) ** 0.5


def test_grover_notes_state_the_numbers_the_solvers_report():
    import re

    from qversus.registry import get_problem, solvers_for

    pytest.importorskip("qiskit")
    problem = get_problem("grover")
    by_name = {s.name: s for s in solvers_for(problem)}
    for inst in problem.instances():
        assert "~N/2" not in inst.note["en"] and "~N/2" not in inst.note["es"]
        k, expected = re.search(r"Grover's (\d+) iterations? against the ([\d.]+) queries", inst.note["en"]).groups()
        quantum = by_name["grover-qiskit"].run(problem, inst, seed=42, shots=64)
        classical = by_name["grover-classical"].run(problem, inst, seed=42, shots=64)
        assert int(k) == quantum.extra["iterations"], inst.id
        assert float(expected) == classical.value["classical_queries"], inst.id
    assert "~N/2" not in problem.concept["en"] and "(N+1)/(M+1)" in problem.concept["en"]
