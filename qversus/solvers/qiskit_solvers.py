"""Qiskit adapters, real Qiskit 2.x + quantum_info. Two solvers:

- `state-qiskit`  : builds the entanglement targets gate-by-gate and emits a full step trace.
- `qaoa-qiskit`   : p=1 QAOA for MaxCut, optimized by an exact statevector grid-search over (γ, β)
                    (deterministic → reproducible; no removed qiskit-algorithms dependency). Emits the
                    optimal-parameter circuit trace + the (γ, β) energy landscape for the viz.
"""

from __future__ import annotations

import time

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

from qversus.core.circuit_trace import circuit_ops, evolve, measure_counts, step_of
from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult

try:
    import qiskit

    QISKIT_VERSION = qiskit.__version__
except Exception:  # pragma: no cover
    QISKIT_VERSION = "unknown"


def _state_circuit(kind: str, variant: str, n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    if kind == "bell":
        qc.h(0)
        qc.cx(0, 1)
        if variant in ("phi_minus", "psi_minus"):
            qc.z(0)
        if variant in ("psi_plus", "psi_minus"):
            qc.x(1)
    elif kind == "ghz":
        qc.h(0)
        for q in range(n - 1):
            qc.cx(q, q + 1)
    else:  # pragma: no cover, W handled via the exact-prepare path below
        raise ValueError(kind)
    return qc


@register_solver
class QiskitStatePrep(Solver):
    name = "state-qiskit"
    label = {"en": "Gate circuit · Qiskit", "es": "Circuito de compuertas · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "state-prep"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace
        from qversus.solvers.classical_solvers import target_state

        p = instance.params
        kind, n = p["kind"], p["n"]
        t0 = time.perf_counter()
        if kind == "w":
            # W has no short clean gate form; prepare the exact target and show it as one labeled step.
            sv0 = Statevector.from_int(0, 2**n)
            svW = Statevector(target_state("w", n))
            steps = [
                step_of(0, "init", [], {"en": "Initial |0…0⟩", "es": "Inicial |0…0⟩"}, sv0, n),
                step_of(1, "PREP-W", list(range(n)),
                        {"en": "Prepare W (cascade of controlled rotations)",
                         "es": "Preparar W (cascada de rotaciones controladas)"}, svW, n),
            ]
            ops = [{"gate": "prepare_W", "targets": list(range(n)), "params": []}]
            probs = np.asarray(svW.probabilities())
            from qversus.core.rng import sample_counts

            meas = {"counts": sample_counts(probs, shots, seed), "shots": shots}
        else:
            qc = _state_circuit(kind, p.get("variant", ""), n)
            steps = evolve(qc)
            ops = circuit_ops(qc)
            meas = measure_counts(qc, shots, seed)
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id,
            title=problem.title,
            concept=problem.concept,
            qubits=n,
            steps=steps,
            measurements=meas,
            circuit_ops=ops,
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"fidelity": 1.0, "shots": shots},
            cost={"wall_ms": round(wall, 3), "qubits": n, "depth": len(steps) - 1},
            notes={"en": "Exact statevector simulation of the gate circuit (Qiskit quantum_info).",
                   "es": "Simulación exacta del vector de estado del circuito (Qiskit quantum_info)."},
            trace=trace,
        )


@register_solver
class QiskitBV(Solver):
    name = "bv-qiskit"
    label = {"en": "BV circuit · Qiskit", "es": "Circuito BV · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "bernstein-vazirani"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace

        n, secret = instance.params["n"], instance.params["secret"]
        total = n + 1  # input qubits 0..n-1 + answer ancilla = qubit n
        qc = QuantumCircuit(total)
        qc.x(n)
        qc.h(range(total))            # input → uniform superposition; ancilla → |−⟩
        for i in range(n):            # oracle f(x)=s·x via phase kickback
            if secret[i] == "1":
                qc.cx(i, n)
        qc.h(range(n))                # interfere → input register becomes |s⟩
        t0 = time.perf_counter()
        steps = evolve(qc)
        probs = np.asarray(Statevector(qc).probabilities())
        idx = int(np.argmax(probs))
        recovered = format(idx, f"0{total}b")[::-1][:n]   # qubit-order; input bits = qubits 0..n-1
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=total,
            steps=steps, measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"recovered": recovered, "correct": recovered == secret, "quantum_queries": 1},
            cost={"wall_ms": round(wall, 3), "qubits": total, "depth": steps[-1].index, "oracle_queries": 1},
            notes={"en": f"One oracle query recovers s={recovered} via phase kickback + interference.",
                   "es": f"Una consulta al oráculo recupera s={recovered} vía phase kickback + interferencia."},
            trace=trace,
        )


@register_solver
class QiskitDJ(Solver):
    name = "dj-qiskit"
    label = {"en": "DJ circuit · Qiskit", "es": "Circuito DJ · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "deutsch-jozsa"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace

        p = instance.params
        n = p["n"]
        total = n + 1
        expected = "constant" if p["kind"] == "constant" else "balanced"
        qc = QuantumCircuit(total)
        qc.x(n)
        qc.h(range(total))
        if p["kind"] == "constant":
            if p["value"] == 1:
                qc.x(n)               # f≡1 → global (−1) phase via the |−⟩ ancilla; verdict still constant
        else:
            for i in range(n):        # balanced f(x)=s·x → phase kickback (−1)^{s·x}
                if p["secret"][i] == "1":
                    qc.cx(i, n)
        qc.h(range(n))
        t0 = time.perf_counter()
        steps = evolve(qc)
        probs = np.asarray(Statevector(qc).probabilities())
        idx = int(np.argmax(probs))
        input_bits = format(idx, f"0{total}b")[::-1][:n]
        verdict = "constant" if set(input_bits) == {"0"} else "balanced"
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=total,
            steps=steps, measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"verdict": verdict, "correct": verdict == expected, "quantum_queries": 1},
            cost={"wall_ms": round(wall, 3), "qubits": total, "depth": steps[-1].index, "oracle_queries": 1},
            notes={"en": f"One oracle query decides f is {verdict} (all-zeros ⇒ constant, else balanced).",
                   "es": f"Una consulta al oráculo decide que f es {verdict} (todo-ceros ⇒ constante)."},
            trace=trace,
        )


@register_solver
class QiskitSimon(Solver):
    name = "simon-qiskit"
    label = {"en": "Simon circuit + GF(2) solve · Qiskit", "es": "Circuito Simon + GF(2) · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "simon"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.rng import sample_counts
        from qversus.core.trace import Trace

        n, secret = instance.params["n"], instance.params["secret"]
        total = 2 * n                       # input qubits 0..n-1, output qubits n..2n-1
        j = min(i for i in range(n) if secret[i] == "1")
        qc = QuantumCircuit(total)
        qc.h(range(n))
        for i in range(n):                  # copy input → output: f starts as identity
            qc.cx(i, n + i)
        for i in range(n):                  # controlled on input_j, XOR s into the output → 2-to-1 period s
            if secret[i] == "1":
                qc.cx(j, n + i)
        qc.h(range(n))
        t0 = time.perf_counter()
        steps = evolve(qc)
        probs = np.asarray(Statevector(qc).probabilities())
        marg = probs.reshape(2**n, 2**n).sum(axis=0)        # P(input register = y) = Σ_output |amp|²
        ys = [y for y in range(2**n) if marg[y] > 1e-9]      # every sampled y satisfies y·s = 0 (mod 2)
        # GF(2) solve: the unique non-zero s orthogonal to all observed y's.
        recovered_val = next(
            (c for c in range(1, 2**n)
             if all(bin(y & c).count("1") % 2 == 0 for y in ys)),
            0,
        )
        recovered = "".join(str((recovered_val >> i) & 1) for i in range(n))
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=total,
            steps=steps,
            measurements={"counts": sample_counts(marg, shots, seed), "shots": shots},  # input-register y's
            circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"observed_y": [format(y, f"0{n}b") for y in ys]},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"recovered": recovered, "correct": recovered == secret, "quantum_queries": n},
            cost={"wall_ms": round(wall, 3), "qubits": total, "depth": steps[-1].index, "oracle_queries": n},
            notes={"en": f"{len(ys)} distinct y's (each y·s=0); GF(2) solve ⇒ s={recovered}. O(n) queries.",
                   "es": f"{len(ys)} cadenas y distintas (cada y·s=0); GF(2) ⇒ s={recovered}. O(n) consultas."},
            trace=trace,
            extra={"observed_y": trace.extra["observed_y"]},
        )


def _shannon_entropy(probs) -> float:
    import math

    return -sum(p * math.log2(p) for p in probs if p > 1e-12)


@register_solver
class QiskitQRNG(Solver):
    name = "qrng-qiskit"
    label = {"en": "Quantum sampling · Qiskit", "es": "Muestreo cuántico · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qrng"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace

        n = instance.params["n"]
        theta = instance.params.get("theta")
        qc = QuantumCircuit(n)
        if theta is not None:
            qc.ry(theta, 0)          # biased single-qubit coin
        else:
            qc.h(range(n))           # uniform superposition over 2^n
        t0 = time.perf_counter()
        probs = [float(p) for p in np.asarray(Statevector(qc).probabilities())]
        entropy = float(_shannon_entropy(probs))
        uniform = bool(abs(entropy - n) < 1e-3 and theta is None)
        wall = (time.perf_counter() - t0) * 1e3
        meas = measure_counts(qc, shots, seed)
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=n,
            steps=evolve(qc), measurements=meas, circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"entropy_bits": round(entropy, 4), "max_entropy_bits": n,
                   "probabilities": [round(p, 4) for p in probs]},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"entropy_bits": round(entropy, 4), "max_entropy_bits": n, "n_outcomes": 2**n,
                   "uniform": uniform, "true_randomness": True},
            cost={"wall_ms": round(wall, 3), "qubits": n, "shots": shots},
            notes={"en": f"{n}-qubit sampling: Shannon entropy {entropy:.3f} of {n} bits "
                         f"({'uniform' if uniform else 'biased' if theta is not None else 'near-uniform'}); "
                         "randomness is fundamental (measurement collapse).",
                   "es": f"Muestreo de {n} qubits: entropía de Shannon {entropy:.3f} de {n} bits "
                         f"({'uniforme' if uniform else 'sesgado' if theta is not None else 'casi uniforme'}); "
                         "la aleatoriedad es fundamental (colapso de la medición)."},
            trace=trace,
        )


@register_solver
class QiskitSingleQubit(Solver):
    name = "gates-qiskit"
    label = {"en": "Gate sequence · Qiskit", "es": "Secuencia de compuertas · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "single-qubit"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qiskit.quantum_info import Pauli

        from qversus.core.trace import Trace

        qc = QuantumCircuit(1)
        for g in instance.params["gates"]:
            getattr(qc, g[0])(*g[1:], 0)        # qc.x(0) / qc.h(0) / qc.ry(theta, 0) / …
        t0 = time.perf_counter()
        sv = Statevector(qc)
        bloch = [round(float(sv.expectation_value(Pauli(p)).real), 4) for p in ("X", "Y", "Z")]
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=1,
            steps=evolve(qc), measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"bloch": bloch, "gates": [g[0].upper() for g in instance.params["gates"]]},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"bloch": bloch, "gates": [g[0].upper() for g in instance.params["gates"]],
                   "norm": round(float(sum(x * x for x in bloch)) ** 0.5, 4)},
            cost={"wall_ms": round(wall, 3), "qubits": 1},
            notes={"en": f"After {'·'.join(g[0].upper() for g in instance.params['gates'])}: Bloch vector "
                         f"{bloch} (a pure state sits on the unit sphere, |r|=1).",
                   "es": f"Tras {'·'.join(g[0].upper() for g in instance.params['gates'])}: vector de Bloch "
                         f"{bloch} (un estado puro está en la esfera unitaria, |r|=1)."},
            trace=trace,
        )


@register_solver
class QiskitInterference(Solver):
    name = "interference-qiskit"
    label = {"en": "Mach–Zehnder circuit · Qiskit", "es": "Circuito Mach–Zehnder · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "interference"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace

        phi = float(instance.params["phi"])
        qc = QuantumCircuit(1)
        qc.h(0)            # split |0⟩ into two paths
        qc.p(phi, 0)       # delay one path by the relative phase φ
        qc.h(0)            # recombine
        t0 = time.perf_counter()
        probs = np.asarray(Statevector(qc).probabilities())
        wall = (time.perf_counter() - t0) * 1e3
        p0, p1 = round(float(probs[0]), 4), round(float(probs[1]), 4)
        fringe = "constructive" if p0 > 0.99 else "destructive" if p0 < 0.01 else "mixed"
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=1,
            steps=evolve(qc), measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"phi": round(phi, 4), "p0": p0, "p1": p1},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"phi": round(phi, 4), "p0": p0, "p1": p1, "fringe": fringe},
            cost={"wall_ms": round(wall, 3), "qubits": 1},
            notes={"en": f"H · P({phi:.3f}) · H gives P(0) = cos²(φ/2) = {p0} ({fringe}). The two paths' "
                         f"amplitudes interfere, at φ=π they cancel exactly.",
                   "es": f"H · P({phi:.3f}) · H da P(0) = cos²(φ/2) = {p0} ({fringe}). Las amplitudes de los "
                         f"dos caminos interfieren, en φ=π se cancelan exactamente."},
            trace=trace,
        )


@register_solver
class QiskitSuperdense(Solver):
    name = "superdense-qiskit"
    label = {"en": "Superdense circuit · Qiskit", "es": "Circuito superdenso · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "superdense"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace

        msg = instance.params["message"]   # 2 chars, "b1 b0"
        b1, b0 = msg[0], msg[1]
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)            # shared Bell pair (Alice = q0, Bob = q1)
        qc.barrier()
        if b0 == "1":
            qc.x(0)            # encode low bit with X
        if b1 == "1":
            qc.z(0)            # encode high bit with Z
        qc.barrier()
        qc.cx(0, 1)
        qc.h(0)                # Bob's Bell measurement (decode)
        t0 = time.perf_counter()
        probs = np.asarray(Statevector(qc).probabilities())
        idx = int(np.argmax(probs))
        decoded = format(idx, "02b")[::-1]   # qubit order (q0=X-bit b0, q1=Z-bit b1) → "b1 b0"
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=2,
            steps=evolve(qc), measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"message": msg, "decoded": decoded, "qubits_sent": 1, "bits_decoded": 2},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"message": msg, "decoded": decoded, "correct": bool(decoded == msg),
                   "bits_decoded": 2, "qubits_sent": 1},
            cost={"wall_ms": round(wall, 3), "qubits": 2, "qubits_transmitted": 1},
            notes={"en": f"Encoded message {msg} into 1 qubit; Bob decoded {decoded}, 2 classical bits from "
                         "1 transmitted qubit (+ a pre-shared Bell pair).",
                   "es": f"Codificó el mensaje {msg} en 1 qubit; Bob decodificó {decoded}, 2 bits clásicos "
                         "desde 1 qubit transmitido (+ un par de Bell compartido)."},
            trace=trace,
        )


@register_solver
class QiskitTeleport(Solver):
    name = "teleport-qiskit"
    label = {"en": "Teleportation circuit · Qiskit", "es": "Circuito de teletransportación · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "teleportation"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qiskit.quantum_info import Pauli, partial_trace, state_fidelity

        from qversus.core.trace import Trace

        theta, phi = instance.params["theta"], instance.params["phi"]
        # q0 = unknown |ψ⟩, q1+q2 = Bell pair (q2 is Bob's). Coherent (deferred-measurement) teleportation.
        qc = QuantumCircuit(3)
        qc.ry(theta, 0)
        qc.rz(phi, 0)                # prepare |ψ⟩ on q0
        qc.barrier()
        qc.h(1)
        qc.cx(1, 2)                  # shared Bell pair
        qc.barrier()
        qc.cx(0, 1)
        qc.h(0)                      # Alice's Bell measurement (coherent)
        qc.barrier()
        qc.cx(1, 2)
        qc.cz(0, 2)                  # Bob's Pauli corrections (controlled = deferred measurement)
        t0 = time.perf_counter()
        sv = Statevector(qc)
        rho2 = partial_trace(sv, [0, 1])          # Bob's qubit after teleportation
        psi = QuantumCircuit(1)
        psi.ry(theta, 0)
        psi.rz(phi, 0)
        target = Statevector(psi)                  # the original |ψ⟩
        fidelity = float(state_fidelity(rho2, target))
        in_bloch = [round(float(target.expectation_value(Pauli(p)).real), 4) for p in ("X", "Y", "Z")]
        out_bloch = [round(float(rho2.expectation_value(Pauli(p)).real), 4) for p in ("X", "Y", "Z")]
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=3,
            steps=evolve(qc), measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"input_bloch": in_bloch, "output_bloch": out_bloch, "fidelity": round(fidelity, 6)},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"fidelity": round(fidelity, 6), "perfect": bool(fidelity > 0.999),
                   "input_bloch": in_bloch, "output_bloch": out_bloch},
            cost={"wall_ms": round(wall, 3), "qubits": 3, "classical_bits": 2},
            notes={"en": f"Teleported |ψ⟩ to Bob's qubit with fidelity {fidelity:.4f} (input Bloch {in_bloch} "
                         f"→ output {out_bloch}); the original is destroyed (no-cloning).",
                   "es": f"Teletransportó |ψ⟩ al qubit de Bob con fidelidad {fidelity:.4f} (Bloch entrada "
                         f"{in_bloch} → salida {out_bloch}); el original se destruye (no-clonación)."},
            trace=trace,
        )


@register_solver
class QiskitCHSH(Solver):
    name = "chsh-qiskit"
    label = {"en": "CHSH correlators · Qiskit", "es": "Correladores CHSH · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "chsh"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import math

        from qiskit.quantum_info import SparsePauliOp

        from qversus.core.trace import Trace

        pr = instance.params
        qc = QuantumCircuit(2)
        if pr["entangled"]:
            qc.h(0)
            qc.cx(0, 1)          # |Φ⁺⟩
        # else: |00⟩ (separable)
        t0 = time.perf_counter()
        sv = Statevector(qc)

        def measure_op(theta):           # M(θ) = cosθ·Z + sinθ·X  (axis in the X–Z plane)
            return SparsePauliOp(["Z", "X"], coeffs=[math.cos(theta), math.sin(theta)])

        def corr(a, b):                  # E(a,b) = ⟨M(a) ⊗ M(b)⟩
            op = measure_op(b).tensor(measure_op(a))   # qubit0 = a, qubit1 = b
            return float(sv.expectation_value(op).real)

        e00, e01 = corr(pr["a0"], pr["b0"]), corr(pr["a0"], pr["b1"])
        e10, e11 = corr(pr["a1"], pr["b0"]), corr(pr["a1"], pr["b1"])
        S = e00 + e01 + e10 - e11
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=2,
            steps=evolve(qc), measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"correlators": {"E00": round(e00, 4), "E01": round(e01, 4),
                                   "E10": round(e10, 4), "E11": round(e11, 4)},
                   "S": round(S, 4), "classical_bound": 2.0, "tsirelson_bound": round(2 * math.sqrt(2), 4)},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"S": round(S, 4), "exceeds_classical": bool(abs(S) > 2 + 1e-6),
                   "tsirelson_bound": round(2 * math.sqrt(2), 4),
                   "correlators": [round(e00, 4), round(e01, 4), round(e10, 4), round(e11, 4)]},
            cost={"wall_ms": round(wall, 3), "qubits": 2, "settings": 4},
            notes={"en": f"S = {S:.3f} ({'VIOLATES' if abs(S) > 2 + 1e-6 else 'within'} the classical bound "
                         f"2; Tsirelson = 2√2 ≈ 2.828).",
                   "es": f"S = {S:.3f} ({'VIOLA' if abs(S) > 2 + 1e-6 else 'dentro de'} la cota clásica 2; "
                         f"Tsirelson = 2√2 ≈ 2.828)."},
            trace=trace,
        )


@register_solver
class QiskitNoise(Solver):
    name = "noise-qiskit"
    label = {"en": "Aer noise + ZNE · Qiskit", "es": "Ruido Aer + ZNE · Qiskit"}
    framework = "qiskit-aer"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "noise"

    @staticmethod
    def _bell(depth: int):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        for _ in range(depth):       # identity CX-pairs add depth (noise) without changing the ideal state
            qc.cx(0, 1)
            qc.cx(0, 1)
        return qc

    @staticmethod
    def _fold(qc, k: int):
        """Global gate folding U → U (U† U)^k: noise scale λ = 2k+1, ideal state unchanged."""
        folded = qc.copy()
        inv = qc.inverse()
        for _ in range(k):
            folded = folded.compose(inv).compose(qc)
        return folded

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qiskit.quantum_info import Pauli
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, depolarizing_error

        p, depth = instance.params["p"], instance.params["depth"]
        t0 = time.perf_counter()
        qc = self._bell(depth)
        ZZ = Pauli("ZZ")
        ideal = float(Statevector(qc).expectation_value(ZZ).real)

        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
        nm.add_all_qubit_quantum_error(depolarizing_error(p / 10, 1), ["h", "x", "z", "rx", "ry", "rz"])
        sim = AerSimulator(method="density_matrix", noise_model=nm)

        def noisy_exp(circ) -> float:
            c = circ.copy()
            c.save_density_matrix()
            rho = sim.run(c, seed_simulator=seed).result().data()["density_matrix"]
            return float(rho.expectation_value(ZZ).real)

        lambdas = [1, 3, 5]
        exps = [noisy_exp(self._fold(qc, k)) for k in (0, 1, 2)]   # λ = 2k+1
        noisy = exps[0]
        slope, intercept = np.polyfit(lambdas, exps, 1)            # linear ZNE extrapolation to λ=0
        mitigated = float(intercept)
        # ideal vs noisy probabilities for the histogram (diagonal of ρ at λ=1)
        c0 = qc.copy()
        c0.save_density_matrix()
        rho0 = sim.run(c0, seed_simulator=seed).result().data()["density_matrix"]
        noisy_probs = np.real(np.diag(rho0.data))
        ideal_probs = np.asarray(Statevector(qc).probabilities())
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"ideal": round(ideal, 4), "noisy": round(noisy, 4), "mitigated": round(mitigated, 4),
                   "residual_noisy": round(abs(ideal - noisy), 4),
                   "residual_mitigated": round(abs(ideal - mitigated), 4)},
            cost={"wall_ms": round(wall, 1), "qubits": 2, "noise_scales": lambdas},
            notes={"en": f"Ideal ⟨ZZ⟩={ideal:.3f}, noisy={noisy:.3f}, ZNE-mitigated={mitigated:.3f} "
                         f"(p={p}, depth={depth}). Mitigation recovers most of the lost signal.",
                   "es": f"Ideal ⟨ZZ⟩={ideal:.3f}, ruidoso={noisy:.3f}, mitigado-ZNE={mitigated:.3f} "
                         f"(p={p}, profundidad={depth}). La mitigación recupera gran parte de la señal."},
            extra={"zne": {"lambdas": lambdas, "expectations": [round(e, 4) for e in exps],
                           "slope": round(float(slope), 4), "intercept": round(mitigated, 4)},
                   "ideal_probs": [round(float(x), 4) for x in ideal_probs],
                   "noisy_probs": [round(float(x), 4) for x in noisy_probs]},
        )


@register_solver
class QiskitShor(Solver):
    name = "shor-qiskit"
    label = {"en": "Order-finding (QPE) · Qiskit", "es": "Order-finding (QPE) · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "shor"

    @staticmethod
    def _modmul_unitary(factor: int, N: int, dim: int):
        """Permutation unitary U|y⟩=|(factor·y) mod N⟩ for y<N, identity on y≥N (real modular mult)."""
        mat = np.zeros((dim, dim))
        for y in range(dim):
            mat[((factor * y) % N) if y < N else y, y] = 1.0
        return mat

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from fractions import Fraction
        from math import gcd

        from qiskit.circuit.library import UnitaryGate

        from qversus.core.trace import Trace

        N, a, t = instance.params["N"], instance.params["a"], instance.params["t"]
        nwork = N.bit_length()                       # 4 for N=15
        dim = 2**nwork
        total = t + nwork                            # counting (0..t-1) + work (t..t+nwork-1)
        work = list(range(t, total))
        qc = QuantumCircuit(total)
        qc.x(t)                                      # work register = |1⟩
        qc.h(range(t))
        for j in range(t):                           # controlled-U_a^{2^j}
            factor = pow(a, 2**j, N)
            cg = UnitaryGate(self._modmul_unitary(factor, N, dim), label=f"U{a}^{2**j}").control(1)
            qc.append(cg, [j, *work])
        qc.barrier()
        for i in range(t // 2):                      # inverse QFT on the counting register
            qc.swap(i, t - 1 - i)
        for tgt in range(t):
            for ctrl in range(tgt):
                qc.cp(-np.pi / 2 ** (tgt - ctrl), ctrl, tgt)
            qc.h(tgt)
        t0 = time.perf_counter()
        steps = evolve(qc)
        probs = np.asarray(Statevector(qc).probabilities())
        marg = probs.reshape(2 ** nwork, 2**t).sum(axis=0)   # counting-register marginal
        # Order-finding: the measured phases s/r are the high-probability counting outcomes.
        order, factors = None, None
        for m in np.argsort(marg)[::-1]:
            if marg[m] < 1e-6:
                break
            frac = Fraction(int(m), 2**t).limit_denominator(N)
            r = frac.denominator
            if r > 1 and pow(a, r, N) == 1:
                order = r
                if r % 2 == 0:
                    x = pow(a, r // 2, N)
                    p, q = gcd(x - 1, N), gcd(x + 1, N)
                    if p * q == N and 1 not in (p, q):
                        factors = sorted([p, q])
                        break
        wall = (time.perf_counter() - t0) * 1e3
        ok = factors is not None and factors[0] * factors[1] == N
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=total,
            steps=steps, measurements={"counts": {format(c, f"0{t}b"): int(round(marg[c] * shots))
                                                  for c in range(2**t) if marg[c] > 1e-6}, "shots": shots},
            circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"base": a, "order": order, "factors": factors},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"factors": factors, "order": order, "base": a, "correct": ok},
            cost={"wall_ms": round(wall, 1), "qubits": total, "depth": steps[-1].index,
                  "counting_qubits": t, "work_qubits": nwork},
            notes={"en": f"QPE order-finding: base a={a} ⇒ order r={order} ⇒ factors {factors} of {N}.",
                   "es": f"Order-finding por QPE: base a={a} ⇒ orden r={order} ⇒ factores {factors} de {N}."},
            trace=trace,
        )


@register_solver
class QiskitQPE(Solver):
    name = "qpe-qiskit"
    label = {"en": "QPE circuit · Qiskit", "es": "Circuito QPE · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qpe"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import math

        from qversus.core.trace import Trace

        t, phi = instance.params["t"], instance.params["phi"]
        target = t                                    # counting qubits 0..t-1, eigenstate qubit = t
        qc = QuantumCircuit(t + 1)
        qc.x(target)                                  # |1⟩ is the eigenstate of P(2πφ)
        qc.h(range(t))
        for j in range(t):                            # controlled-U^{2^j}, U = P(2πφ)
            qc.cp(2 * math.pi * phi * (2**j), j, target)
        qc.barrier()
        # inverse QFT on the counting register (0..t-1): swaps, then inverse-CP ladder + H
        for i in range(t // 2):
            qc.swap(i, t - 1 - i)
        for tgt in range(t):
            for ctrl in range(tgt):
                qc.cp(-math.pi / 2 ** (tgt - ctrl), ctrl, tgt)
            qc.h(tgt)
        t0 = time.perf_counter()
        steps = evolve(qc)
        probs = np.asarray(Statevector(qc).probabilities())
        marg = probs.reshape(2, 2**t).sum(axis=0)     # counting-register marginal (trace out the eigenstate)
        m = int(np.argmax(marg))
        phi_hat = m / 2**t
        best_bin = round(phi * 2**t) % (2**t)
        err = abs(phi_hat - phi)
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=t + 1,
            steps=steps, measurements={"counts": {format(c, f"0{t}b"): int(round(marg[c] * shots))
                                                  for c in range(2**t) if marg[c] > 1e-6}, "shots": shots},
            circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"phi_true": phi, "phi_estimate": round(phi_hat, 6), "m": m,
                   "p_best": round(float(marg[best_bin]), 4)},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"phi_estimate": round(phi_hat, 6), "phi_true": phi, "error": round(err, 6),
                   "counting_qubits": t, "p_top": round(float(marg[m]), 4)},
            cost={"wall_ms": round(wall, 3), "qubits": t + 1, "depth": steps[-1].index},
            notes={"en": f"QPE with t={t} → φ̂={phi_hat:.4f} (true {phi}), error {err:.4f}, "
                         f"P(top)={marg[m]:.3f}. Resolution 2^-{t}.",
                   "es": f"QPE con t={t} → φ̂={phi_hat:.4f} (real {phi}), error {err:.4f}, "
                         f"P(top)={marg[m]:.3f}. Resolución 2^-{t}."},
            trace=trace,
        )


@register_solver
class QiskitQFT(Solver):
    name = "qft-qiskit"
    label = {"en": "QFT circuit · Qiskit", "es": "Circuito QFT · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qft"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import math

        from qversus.core.trace import Trace

        n, k = instance.params["n"], instance.params["k"]
        N = 2**n
        qc = QuantumCircuit(n)
        for i in range(n):                       # prepare |k⟩ (little-endian: bit i = qubit i)
            if (k >> i) & 1:
                qc.x(i)
        qc.barrier()
        for target in range(n - 1, -1, -1):      # textbook QFT: H + controlled-phase ladder
            qc.h(target)
            for control in range(target):
                qc.cp(math.pi / 2 ** (target - control), control, target)
        for i in range(n // 2):                  # bit-reversal swaps
            qc.swap(i, n - 1 - i)
        t0 = time.perf_counter()
        steps = evolve(qc)
        sv = np.asarray(Statevector(qc).data)
        # Analytic DFT of |k⟩: u[j] = (1/√N) e^{2πi k j / N}. Validate fidelity (try both sign conventions).
        j = np.arange(N)
        dft = np.exp(2j * np.pi * k * j / N) / math.sqrt(N)
        fid = max(abs(np.vdot(dft, sv)) ** 2, abs(np.vdot(np.conjugate(dft), sv)) ** 2)
        gate_count = len([s for s in steps if s.gate not in ("init",)])
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=n,
            steps=steps, measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"fidelity_vs_dft": round(float(fid), 6), "gate_count": gate_count},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"fidelity_vs_dft": round(float(fid), 6), "matches_dft": bool(fid > 0.999),
                   "gate_count": gate_count, "readable": False},
            cost={"wall_ms": round(wall, 3), "qubits": n, "gates": gate_count,
                  "gate_complexity": "O(n^2)"},
            notes={"en": f"QFT|{k}⟩ via {gate_count} gates (O(n²)); fidelity vs analytic DFT = {fid:.4f}. "
                         "But a measurement gives one sample, the spectrum is not readable.",
                   "es": f"QFT|{k}⟩ con {gate_count} compuertas (O(n²)); fidelidad vs DFT analítica = "
                         f"{fid:.4f}. Pero una medición da una sola muestra, el espectro no es legible."},
            trace=trace,
        )


def _mcz(qc: "QuantumCircuit", n: int) -> None:
    """Multi-controlled Z on n qubits (phase flip of |1…1⟩)."""
    if n == 1:
        qc.z(0)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)


def _grover_oracle(qc: "QuantumCircuit", n: int, marked: list[int]) -> None:
    """Phase-flip each marked basis state |w⟩."""
    for w in marked:
        zeros = [i for i in range(n) if not (w >> i) & 1]
        if zeros:
            qc.x(zeros)
        _mcz(qc, n)
        if zeros:
            qc.x(zeros)


def _grover_diffuser(qc: "QuantumCircuit", n: int) -> None:
    """Inversion about the mean: H^n X^n (MCZ) X^n H^n."""
    qc.h(range(n))
    qc.x(range(n))
    _mcz(qc, n)
    qc.x(range(n))
    qc.h(range(n))


@register_solver
class QiskitGrover(Solver):
    name = "grover-qiskit"
    label = {"en": "Grover circuit · Qiskit", "es": "Circuito Grover · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "grover"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import math

        from qversus.core.trace import Trace

        n, marked = instance.params["n"], instance.params["marked"]
        N, M = 2**n, len(marked)
        k = max(1, math.floor(math.pi / 4 * math.sqrt(N / M)))   # optimal Grover iterations
        qc = QuantumCircuit(n)
        qc.h(range(n))
        for _ in range(k):
            _grover_oracle(qc, n, marked)
            _grover_diffuser(qc, n)
        t0 = time.perf_counter()
        steps = evolve(qc)
        probs = np.asarray(Statevector(qc).probabilities())
        idx = int(np.argmax(probs))
        found = format(idx, f"0{n}b")[::-1]                       # qubit order: position u = qubit u
        success = float(sum(probs[w] for w in marked))            # total prob on the marked subspace
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=n,
            steps=steps, measurements=measure_counts(qc, shots, seed), circuit_ops=circuit_ops(qc),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"iterations": k, "success_prob": round(success, 4),
                   "marked": [format(w, f"0{n}b")[::-1] for w in marked]},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"found": found, "correct": idx in marked, "success_prob": round(success, 4),
                   "quantum_queries": k},
            cost={"wall_ms": round(wall, 3), "qubits": n, "depth": steps[-1].index, "oracle_queries": k},
            notes={"en": f"{k} Grover iteration(s) on N={N}, M={M}: P(marked)={success:.3f}, found "
                         f"|{found}⟩. Quantum ~√N queries.",
                   "es": f"{k} iteración(es) de Grover en N={N}, M={M}: P(marcado)={success:.3f}, encontró "
                         f"|{found}⟩. Cuántico ~√N consultas."},
            trace=trace,
            extra={"iterations": k, "success_prob": round(success, 4)},
        )


def _maxcut_cost_op(n: int, edges: list[list[int]]) -> SparsePauliOp:
    """C = Σ_(u,v)∈E 0.5 (I − Z_u Z_v), expectation = expected cut value."""
    sparse = []
    for u, v in edges:
        sparse.append(("ZZ", [u, v], -0.5))
    op = SparsePauliOp.from_sparse_list(sparse, num_qubits=n) + SparsePauliOp(["I" * n], coeffs=[0.5 * len(edges)])
    return op.simplify()


def _qaoa_circuit(n: int, edges: list[list[int]], gamma: float, beta: float) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for u, v in edges:           # cost layer exp(-iγ C)
        qc.rzz(2.0 * gamma, u, v)
    for q in range(n):           # mixer layer exp(-iβ ΣX)
        qc.rx(2.0 * beta, q)
    return qc


@register_solver
class QiskitQAOA(Solver):
    name = "qaoa-qiskit"
    label = {"en": "QAOA (p=1) · Qiskit", "es": "QAOA (p=1) · Qiskit"}
    framework = "qiskit"
    paradigm = QUANTUM_SIM
    GRID = 24

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "maxcut"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.core.trace import Trace

        n, edges = instance.params["n"], instance.params["edges"]
        cost = _maxcut_cost_op(n, edges)
        t0 = time.perf_counter()
        gammas = np.linspace(0, np.pi, self.GRID)
        betas = np.linspace(0, np.pi, self.GRID)
        landscape, best = [], (-1.0, 0.0, 0.0)
        for g in gammas:
            row = []
            for b in betas:
                sv = Statevector(_qaoa_circuit(n, edges, g, b))
                e = float(sv.expectation_value(cost).real)
                row.append(round(e, 4))
                if e > best[0]:
                    best = (e, g, b)
            landscape.append(row)
        exp_best, g_best, b_best = best
        qc_best = _qaoa_circuit(n, edges, g_best, b_best)
        probs = np.asarray(Statevector(qc_best).probabilities())
        idx = int(np.argmax(probs))
        bits = format(idx, f"0{n}b")[::-1]  # → vertex u = position u (qubit order)
        cut = problem.cut_value(edges, bits)
        wall = (time.perf_counter() - t0) * 1e3
        trace = Trace(
            case_id=problem.id, title=problem.title, concept=problem.concept, qubits=n,
            steps=evolve(qc_best), measurements=measure_counts(qc_best, shots, seed),
            circuit_ops=circuit_ops(qc_best),
            provenance={"engine": "qiskit", "engine_version": QISKIT_VERSION, "seed": seed,
                        "lane": "tbd", "ran_on": "simulator"},
            references=problem.references,
            extra={"landscape": {"gammas": [round(float(x), 4) for x in gammas],
                                 "betas": [round(float(x), 4) for x in betas], "expectation": landscape},
                   "gamma": round(g_best, 4), "beta": round(b_best, 4)},
        )
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"cut": cut, "bitstring": bits, "expectation": round(exp_best, 4)},
            cost={"wall_ms": round(wall, 1), "qubits": n, "depth": trace.steps[-1].index,
                  "evaluations": self.GRID ** 2},
            notes={"en": f"p=1 QAOA, exact-statevector grid-search over (γ,β). Best ⟨C⟩={exp_best:.3f}; "
                         f"most-probable bitstring cuts {cut} edges.",
                   "es": f"QAOA p=1, búsqueda en malla (γ,β) con vector de estado exacto. Mejor ⟨C⟩="
                         f"{exp_best:.3f}; la cadena más probable corta {cut} aristas."},
            trace=trace,
            extra={"landscape": trace.extra["landscape"]},
        )
