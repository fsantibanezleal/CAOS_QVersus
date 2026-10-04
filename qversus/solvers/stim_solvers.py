"""Stim adapter (Phase-B framework), the stabilizer/QEC engine.

Stim simulates Clifford circuits with thousands of qubits (Gottesman-Knill), which is exactly what error
correction needs: sample the noisy syndrome history of a code, then decode. qversus pairs Stim with PyMatching
(minimum-weight perfect matching) to run the real QEC decoding pipeline for the repetition code. This is
the standard toolchain that scales up to surface codes, a genuinely new simulation paradigm beside the
state-vector solvers (Qiskit/PennyLane/Cirq), added as one more adapter.
"""

from __future__ import annotations

import time

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult

try:
    import stim

    STIM_VERSION = stim.__version__
except Exception:  # pragma: no cover
    stim = None
    STIM_VERSION = "unknown"


@register_solver
class StimQEC(Solver):
    name = "qec-stim"
    label = {"en": "QEC code (Stim + MWPM)", "es": "Código QEC (Stim + MWPM)"}
    framework = "stim"
    paradigm = QUANTUM_SIM
    SHOTS = 30_000

    def applicable(self, problem: Problem) -> bool:
        return problem.id in ("qec-repetition", "qec-surface") and stim is not None

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import pymatching

        d, p, rounds = instance.params["distance"], instance.params["p"], instance.params["rounds"]
        code_task = instance.params.get("code_task", "repetition_code:memory")
        is_surface = code_task.startswith("surface")
        t0 = time.perf_counter()
        noise = ({"after_clifford_depolarization": p, "before_measure_flip_probability": p}
                 if is_surface
                 else {"before_round_data_depolarization": p, "before_measure_flip_probability": p / 2})
        circuit = stim.Circuit.generated(code_task, rounds=rounds, distance=d, **noise)
        nqubits = circuit.num_qubits
        sampler = circuit.compile_detector_sampler(seed=seed)
        det, obs = sampler.sample(self.SHOTS, separate_observables=True)
        matcher = pymatching.Matching.from_detector_error_model(
            circuit.detector_error_model(decompose_errors=True))
        pred = matcher.decode_batch(det)
        logical_err = float((pred != obs).any(axis=1).mean())
        wall = (time.perf_counter() - t0) * 1e3
        kind = "rotated surface code" if is_surface else "repetition code"
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"logical_error_rate": round(logical_err, 5), "distance": d, "rounds": rounds,
                   "physical_p": p, "physical_qubits": nqubits},
            cost={"wall_ms": round(wall, 1), "shots": self.SHOTS, "physical_qubits": nqubits},
            notes={"en": f"Stim+PyMatching: distance-{d} {kind} at p={p} → logical error {logical_err:.4f} "
                         f"over {rounds} rounds ({nqubits} physical qubits).",
                   "es": f"Stim+PyMatching: {kind} distancia-{d} a p={p} → error lógico {logical_err:.4f} "
                         f"en {rounds} rondas ({nqubits} qubits físicos)."},
            extra={"shots": self.SHOTS, "code": code_task},
        )
