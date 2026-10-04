"""Real-hardware adapters: submit a problem instance to a REAL quantum computer and return its result.

Currently: IBM Quantum (Open Plan, free). The adapter is **opt-in** (`requires_opt_in = True`): the registry
never returns it from `solvers_for(problem)` unless it is named explicitly (`solvers_for(problem,
only="ibm-hardware")`), so running "every solver" never touches a QPU or spends budget.

It reads `QISKIT_IBM_TOKEN` (and optionally `QISKIT_IBM_INSTANCE`) from the environment; the operator supplies
the token, typically through a local, untracked `.env`. The returned counts form a trace whose provenance
names the backend (`ran_on`), so a consumer can show the noisy real-hardware histogram next to the ideal
simulator.

This module builds the same `Trace`/`SolverResult` shape as every other adapter, so it is a pure add-on
(the extensibility contract). It is dormant until a token exists; importing it never requires the token.
"""

from __future__ import annotations

import os
import time

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_HARDWARE, Solver, SolverResult

# Cases whose circuits are small enough for the free Open Plan budget (built by the Qiskit adapters).
_HARDWARE_CASES = {"state-prep", "bernstein-vazirani", "deutsch-jozsa"}


def _ibm_token() -> str | None:
    return os.environ.get("QISKIT_IBM_TOKEN") or None


@register_solver
class IBMHardware(Solver):
    name = "ibm-hardware"
    label = {"en": "Real QPU · IBM Quantum", "es": "QPU real · IBM Quantum"}
    framework = "ibm-quantum"
    paradigm = QUANTUM_HARDWARE
    requires_opt_in = True            # never auto-runs; cost/queue is explicit

    def applicable(self, problem: Problem) -> bool:
        # Only offer it for the small circuit cases AND only when a token is configured.
        return problem.id in _HARDWARE_CASES and _ibm_token() is not None

    def _circuit(self, problem: Problem, instance: Instance):
        """Reuse the Qiskit adapter's circuit for this case (single source of truth for the physics)."""
        from qiskit import QuantumCircuit

        from qversus.solvers import qiskit_solvers as q

        p = instance.params
        if problem.id == "state-prep":
            if p["kind"] == "w":
                raise ValueError("W-state hardware run not wired (no short gate form); use a sim solver.")
            qc = q._state_circuit(p["kind"], p.get("variant", ""), p["n"])
            qc.measure_all()
            return qc
        if problem.id == "bernstein-vazirani":
            n = p["n"]
            qc = QuantumCircuit(n + 1, n)
            qc.x(n)
            qc.h(range(n + 1))
            for i in range(n):
                if p["secret"][i] == "1":
                    qc.cx(i, n)
            qc.h(range(n))
            qc.measure(range(n), range(n))
            return qc
        if problem.id == "deutsch-jozsa":
            n = p["n"]
            qc = QuantumCircuit(n + 1, n)
            qc.x(n)
            qc.h(range(n + 1))
            if p["kind"] == "constant":
                if p["value"] == 1:
                    qc.x(n)
            else:
                for i in range(n):
                    if p["secret"][i] == "1":
                        qc.cx(i, n)
            qc.h(range(n))
            qc.measure(range(n), range(n))
            return qc
        raise ValueError(f"no hardware circuit for {problem.id}")

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        token = _ibm_token()
        if token is None:
            raise SystemExit(
                "ibm-hardware needs QISKIT_IBM_TOKEN. Create a free IBM Quantum Open account "
                "(https://quantum.cloud.ibm.com), copy its API token, export it as QISKIT_IBM_TOKEN "
                "(for example through a local, untracked .env), then select the ibm-hardware solver again."
            )
        # Imported lazily so the module loads without the SDK / token.
        from qiskit import transpile
        from qiskit_ibm_runtime import QiskitRuntimeService
        from qiskit_ibm_runtime import SamplerV2 as Sampler

        qc = self._circuit(problem, instance)
        t0 = time.perf_counter()
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token,
                                       instance=os.environ.get("QISKIT_IBM_INSTANCE") or None)
        backend = service.least_busy(operational=True, simulator=False)
        isa = transpile(qc, backend=backend, optimization_level=3)
        job = Sampler(mode=backend).run([(isa,)], shots=shots)
        result = job.result()[0]
        counts = {k: int(v) for k, v in result.data.meas.get_counts().items()}
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"counts_top": dict(sorted(counts.items(), key=lambda kv: -kv[1])[:5]), "shots": shots},
            cost={"wall_ms": round(wall, 1), "qubits": qc.num_qubits, "shots": shots,
                  "backend": backend.name, "job_id": job.job_id()},
            notes={"en": f"Ran on real IBM hardware ({backend.name}); compare this noisy histogram to the "
                         "ideal simulator trace for the same case.",
                   "es": f"Ejecutado en hardware real de IBM ({backend.name}); compara este histograma "
                         "ruidoso con la traza del simulador ideal del mismo caso."},
            extra={"counts": counts, "ran_on": f"IBM Quantum · {backend.name}"},
        )
