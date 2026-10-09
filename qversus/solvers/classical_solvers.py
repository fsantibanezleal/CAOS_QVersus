"""Classical baselines, the honest "still more practical" foil (pure NumPy, no quantum SDK).

These exist to make the dossier's verdict concrete and on-screen: for MaxCut at lab sizes, exact brute
force returns the provably-optimal cut in microseconds; for state prep, a classical computer writes the
2^n amplitudes directly. Every quantum solver is shown next to one of these.
"""

from __future__ import annotations

import time

import numpy as np

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import CLASSICAL, Solver, SolverResult


def target_state(kind: str, n: int, variant: str = "") -> np.ndarray:
    """The exact target statevector for a state-prep instance (little-endian basis index)."""
    psi = np.zeros(2**n, dtype=complex)
    if kind == "bell":
        s = 1 / np.sqrt(2)
        table = {
            "phi_plus": [(0b00, s), (0b11, s)],
            "phi_minus": [(0b00, s), (0b11, -s)],
            "psi_plus": [(0b01, s), (0b10, s)],
            "psi_minus": [(0b01, s), (0b10, -s)],
        }
        for idx, a in table[variant]:
            psi[idx] = a
    elif kind == "ghz":
        psi[0] = psi[2**n - 1] = 1 / np.sqrt(2)
    elif kind == "w":
        for q in range(n):
            psi[1 << q] = 1 / np.sqrt(n)
    else:  # pragma: no cover
        raise ValueError(f"unknown state kind {kind!r}")
    return psi


@register_solver
class ClassicalStatePrep(Solver):
    name = "state-classical"
    label = {"en": "Direct amplitudes · classical", "es": "Amplitudes directas · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "state-prep"

    def run(self, problem: Problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        p = instance.params
        t0 = time.perf_counter()
        psi = target_state(p["kind"], p["n"], p.get("variant", ""))
        wall = (time.perf_counter() - t0) * 1e3
        nz = {format(i, f"0{p['n']}b"): round(float(abs(psi[i]) ** 2), 6) for i in np.nonzero(psi)[0]}
        return SolverResult(
            solver=self.name,
            label=self.label,
            framework=self.framework,
            paradigm=self.paradigm,
            value={"nonzero_probabilities": nz},
            cost={"wall_ms": round(wall, 4), "qubits": p["n"]},
            notes={
                "en": "A classical computer stores all 2^n amplitudes directly, instant at this scale. "
                      "The entanglement is the concept; there is no advantage here.",
                "es": "Un computador clásico guarda las 2^n amplitudes directamente, instantáneo a esta "
                      "escala. El entrelazamiento es el concepto; aquí no hay ventaja.",
            },
            optimal=True,
        )


@register_solver
class BruteForceMaxCut(Solver):
    name = "maxcut-bruteforce"
    label = {"en": "Brute force (optimal) · classical", "es": "Fuerza bruta (óptimo) · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "maxcut"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        n, edges = instance.params["n"], instance.params["edges"]
        t0 = time.perf_counter()
        best_cut, best_bits = -1, None
        for x in range(2**n):
            bits = format(x, f"0{n}b")
            c = sum(1 for (u, v) in edges if bits[u] != bits[v])
            if c > best_cut:
                best_cut, best_bits = c, bits
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name,
            label=self.label,
            framework=self.framework,
            paradigm=self.paradigm,
            value={"cut": best_cut, "bitstring": best_bits},
            cost={"wall_ms": round(wall, 4), "evaluated": 2**n},
            notes={
                "en": f"Enumerated all {2**n} partitions; the optimum ({best_cut}) is exact and found in "
                      f"{wall:.3f} ms. This is the bar QAOA must beat, and does not, at this scale.",
                "es": f"Enumeró las {2**n} particiones; el óptimo ({best_cut}) es exacto y se encontró en "
                      f"{wall:.3f} ms. Este es el listón que QAOA debe superar, y no lo hace, a esta escala.",
            },
            optimal=True,
        )


@register_solver
class ClassicalBV(Solver):
    name = "bv-classical"
    label = {"en": "Oracle queries · classical", "es": "Consultas al oráculo · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "bernstein-vazirani"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.problems.bernstein_vazirani import BernsteinVazirani

        n, secret = instance.params["n"], instance.params["secret"]
        t0 = time.perf_counter()
        # Query the oracle on each basis vector e_i (only bit i set): f(e_i) = s_i. n queries.
        recovered = "".join(str(BernsteinVazirani.oracle(secret, 1 << i)) for i in range(n))
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"recovered": recovered, "correct": recovered == secret, "classical_queries": n},
            cost={"wall_ms": round(wall, 4), "oracle_queries": n},
            notes={"en": f"Recovered s={recovered} bit-by-bit in {n} oracle queries (one per bit), instant "
                         "at this scale; the quantum win is in query count, not wall-time.",
                   "es": f"Recuperó s={recovered} bit a bit en {n} consultas al oráculo (una por bit), "
                         "instantáneo a esta escala; la ventaja cuántica es en número de consultas, no en tiempo."},
            optimal=True,
        )


@register_solver
class ClassicalDJ(Solver):
    name = "dj-classical"
    label = {"en": "Oracle queries · classical", "es": "Consultas al oráculo · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "deutsch-jozsa"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.problems.deutsch_jozsa import DeutschJozsa

        n = instance.params["n"]
        expected = "constant" if instance.params["kind"] == "constant" else "balanced"
        half = 2 ** (n - 1)
        t0 = time.perf_counter()
        seen: set[int] = set()
        verdict, queries = None, 0
        for x in range(2**n):
            queries += 1
            seen.add(DeutschJozsa.evaluate(instance.params, x))
            if len(seen) > 1:                 # two different outputs ⇒ balanced (stop early)
                verdict = "balanced"
                break
            if queries > half:                # queried just over half, all equal ⇒ must be constant
                verdict = "constant"
                break
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"verdict": verdict, "correct": verdict == expected, "classical_queries": queries},
            cost={"wall_ms": round(wall, 4), "oracle_queries": queries},
            notes={"en": f"Decided f is {verdict} after {queries} oracle queries (worst case "
                         f"{half + 1}); the quantum win is in query count, not wall-time.",
                   "es": f"Decidió que f es {verdict} tras {queries} consultas (peor caso {half + 1}); "
                         "la ventaja cuántica es en número de consultas, no en tiempo."},
            optimal=True,
        )


@register_solver
class ClassicalSimon(Solver):
    name = "simon-classical"
    label = {"en": "Collision search · classical", "es": "Búsqueda de colisión · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "simon"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qversus.problems.simon import Simon

        n, secret = instance.params["n"], instance.params["secret"]
        t0 = time.perf_counter()
        # Query f on inputs until two inputs collide (f 2-to-1) ⇒ s = x1 ⊕ x2. Expected ~2^{n/2} (birthday).
        seen: dict[int, int] = {}
        recovered_val, queries = None, 0
        for x in range(2**n):
            queries += 1
            fx = Simon.evaluate(instance.params, x)
            if fx in seen:
                recovered_val = x ^ seen[fx]
                break
            seen[fx] = x
        recovered = "".join(str((recovered_val >> i) & 1) for i in range(n)) if recovered_val else "0" * n
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"recovered": recovered, "correct": recovered == secret, "classical_queries": queries},
            cost={"wall_ms": round(wall, 4), "oracle_queries": queries},
            notes={"en": f"Found a collision after {queries} queries ⇒ s={recovered} (expected ~2^(n/2) = "
                         f"{round(2 ** (n / 2), 1)}); the quantum advantage is exponential in query count.",
                   "es": f"Halló una colisión tras {queries} consultas ⇒ s={recovered} (esperado ~2^(n/2) = "
                         f"{round(2 ** (n / 2), 1)}); la ventaja cuántica es exponencial en consultas."},
            optimal=True,
        )


@register_solver
class ClassicalFactor(Solver):
    name = "shor-classical"
    label = {"en": "Trial division · classical", "es": "División de prueba · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "shor"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        N = instance.params["N"]
        t0 = time.perf_counter()
        factors, d = None, 2
        while d * d <= N:
            if N % d == 0:
                factors = sorted([d, N // d])
                break
            d += 1
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"factors": factors, "method": "trial division", "ops": int(N**0.5)},
            cost={"wall_ms": round(wall, 4), "ops": int(N**0.5)},
            notes={"en": f"Trial division factors {N} = {factors[0]}×{factors[1]} in microseconds. "
                         "Factoring is easy at this size. For RSA-2048, Gidney (2025) estimates fewer than a "
                         "million noisy physical qubits running an error-corrected computation for under a week.",
                   "es": f"La división de prueba factoriza {N} = {factors[0]}×{factors[1]} en microsegundos. "
                         "Factorizar es fácil a este tamaño. Para RSA-2048, Gidney (2025) estima menos de un "
                         "millón de qubits físicos ruidosos ejecutando un cómputo con corrección de errores "
                         "durante menos de una semana."},
            optimal=True,
        )


@register_solver
class ClassicalSVM(Solver):
    name = "qml-classical"
    label = {"en": "RBF-SVM · classical", "es": "SVM-RBF · clásico"}
    framework = "classical:sklearn"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qml"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from sklearn.svm import SVC

        from qversus.problems.qml_classifier import QMLClassifier

        Xtr, ytr, Xte, yte = QMLClassifier.dataset(instance.params["kind"], seed=seed)
        t0 = time.perf_counter()
        clf = SVC(kernel="rbf", gamma="scale").fit(Xtr, ytr)
        train_acc = float(clf.score(Xtr, ytr))
        test_acc = float(clf.score(Xte, yte))
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"train_acc": round(train_acc, 3), "test_acc": round(test_acc, 3)},
            cost={"wall_ms": round(wall, 3), "support_vectors": int(clf.n_support_.sum())},
            notes={"en": f"Classical RBF-SVM: train {train_acc:.2f}, test {test_acc:.2f}. A standard kernel "
                         "machine on the same data, the bar the quantum kernel has to beat (and doesn't).",
                   "es": f"SVM-RBF clásico: train {train_acc:.2f}, test {test_acc:.2f}. Una máquina de kernel "
                         "estándar sobre los mismos datos, el listón que el kernel cuántico debe superar (y no)."},
            optimal=True,
        )


@register_solver
class ClassicalPRNG(Solver):
    name = "qrng-classical"
    label = {"en": "Pseudo-random generator · classical", "es": "Generador pseudoaleatorio · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qrng"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        n = instance.params["n"]
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, 2**n, size=shots)
        counts = np.bincount(draws, minlength=2**n)
        p = counts / counts.sum()
        entropy = float(-np.sum([pi * np.log2(pi) for pi in p if pi > 1e-12]))
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"entropy_bits": round(entropy, 4), "max_entropy_bits": n, "deterministic": True,
                   "true_randomness": False},
            cost={"wall_ms": 0.0, "shots": shots},
            notes={"en": f"A classical PRNG produces the same flat statistics (entropy {entropy:.3f}/{n} bits) "
                         ", but it is fully deterministic given its seed. Statistically indistinguishable here; "
                         "the quantum edge is certifiable true randomness, not better numbers.",
                   "es": f"Un PRNG clásico produce las mismas estadísticas planas (entropía {entropy:.3f}/{n} "
                         "bits), pero es totalmente determinista dada su semilla. Estadísticamente "
                         "indistinguible aquí; la ventaja cuántica es aleatoriedad verdadera certificable."},
            optimal=True,
        )


@register_solver
class ClassicalBit(Solver):
    name = "bit-classical"
    label = {"en": "Classical bit · classical", "es": "Bit clásico · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "single-qubit"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # The classical counterpart of a qubit is a bit: exactly two states (the poles of the sphere), one
        # bit of retrievable information. A qubit roams the whole sphere, but a measurement returns one bit.
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"states": 2, "retrievable_bits": 1, "poles": ["|0⟩ (z=+1)", "|1⟩ (z=−1)"]},
            cost={"wall_ms": 0.0},
            notes={"en": "A classical bit is just two points, the poles |0⟩ and |1⟩. A qubit occupies the "
                         "whole Bloch sphere, but measurement collapses it to one bit (Holevo): one qubit "
                         "stores no more classical information than one bit. The sphere matters via interference.",
                   "es": "Un bit clásico son solo dos puntos, los polos |0⟩ y |1⟩. Un qubit ocupa toda la "
                         "esfera de Bloch, pero la medición lo colapsa a un bit (Holevo): un qubit no guarda "
                         "más información clásica que un bit. La esfera importa por interferencia."},
            optimal=True,
        )


@register_solver
class ClassicalInterference(Solver):
    name = "interference-classical"
    label = {"en": "Wave interference · classical", "es": "Interferencia de ondas · clásica"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "interference"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # A classical optical Mach–Zehnder: two paths with a relative phase φ recombine, and the output
        # intensity is I(φ) = cos²(φ/2): the same fringe as the qubit. Interference is not, by itself,
        # quantum; what is quantum is that it occurs for a single particle's probability amplitude.
        phi = float(instance.params["phi"])
        intensity = round(float(np.cos(phi / 2) ** 2), 4)
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"phi": round(phi, 4), "intensity": intensity, "law": "I = cos²(φ/2)"},
            cost={"wall_ms": 0.0},
            notes={"en": f"A classical wave (optical Mach–Zehnder) gives the identical fringe I = cos²(φ/2) = "
                         f"{intensity}. Interference itself is classical; the quantum twist is that it happens "
                         f"for one particle's amplitude, the resource the algorithms steer.",
                   "es": f"Una onda clásica (Mach–Zehnder óptico) da la franja idéntica I = cos²(φ/2) = "
                         f"{intensity}. La interferencia en sí es clásica; lo cuántico es que ocurre para la "
                         f"amplitud de una partícula, el recurso que dirigen los algoritmos."},
            optimal=True,
        )


@register_solver
class ClassicalHolevo(Solver):
    name = "superdense-classical"
    label = {"en": "Holevo limit · classical", "es": "Límite de Holevo · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "superdense"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # Without pre-shared entanglement, one qubit (or one classical symbol) carries at most ONE classical
        # bit (Holevo's bound). To send 2 bits you must transmit 2. Superdense doubles this: using a Bell pair.
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"bits_per_qubit": 1, "qubits_needed_for_2_bits": 2},
            cost={"wall_ms": 0.0},
            notes={"en": "Without entanglement, one qubit conveys at most 1 classical bit (Holevo), sending "
                         "2 bits needs 2 transmissions. Superdense gets 2 bits per qubit, but only via a "
                         "pre-shared Bell pair (an honest resource trade, not free bandwidth).",
                   "es": "Sin entrelazamiento, un qubit transmite a lo más 1 bit clásico (Holevo), enviar 2 "
                         "bits necesita 2 transmisiones. La superdensa logra 2 bits por qubit, pero solo vía "
                         "un par de Bell compartido (un intercambio honesto de recursos, no ancho de banda gratis)."},
            optimal=True,
        )


@register_solver
class ClassicalResend(Solver):
    name = "teleport-classical"
    label = {"en": "Measure & re-prepare · classical", "es": "Medir y re-preparar · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "teleportation"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # The best ANY classical strategy can do for an unknown qubit is measure-and-re-prepare, whose
        # optimal average fidelity is exactly 2/3 (Massar-Popescu). This is the bound teleportation beats.
        f = 2.0 / 3.0
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"best_fidelity": round(f, 4), "strategy": "measure & re-prepare"},
            cost={"wall_ms": 0.0},
            notes={"en": "Without entanglement, the best classical 'measure-and-resend' of an unknown qubit "
                         "reaches only average fidelity 2/3, the bound teleportation's fidelity-1 transfer beats.",
                   "es": "Sin entrelazamiento, el mejor 'medir y reenviar' clásico de un qubit desconocido "
                         "alcanza solo fidelidad media 2/3, la cota que la fidelidad-1 de la teletransportación supera."},
            optimal=True,
        )


@register_solver
class ClassicalLHV(Solver):
    name = "chsh-classical"
    label = {"en": "Local hidden variables (bound) · classical", "es": "Variables ocultas locales (cota) · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "chsh"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # No computation needed: the CHSH theorem proves S ≤ 2 for ANY local-hidden-variable strategy
        # (deterministic ±1 assignments give the extreme value 2). This is the bound quantum must beat.
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"max_S": 2.0, "model": "local hidden variables"},
            cost={"wall_ms": 0.0},
            notes={"en": "Any classical (local-hidden-variable) strategy obeys |S| ≤ 2, the CHSH bound. "
                         "A quantum S above 2 cannot be explained by local realism (this is what Bell tests prove).",
                   "es": "Cualquier estrategia clásica (de variables ocultas locales) cumple |S| ≤ 2, la cota "
                         "CHSH. Un S cuántico mayor que 2 no se explica con realismo local (eso prueban los tests de Bell)."},
            optimal=True,
        )


@register_solver
class ClassicalUnprotected(Solver):
    name = "qec-baseline"
    label = {"en": "Unprotected qubit · classical model", "es": "Qubit sin proteger · modelo clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id in ("qec-repetition", "qec-surface")

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        p, rounds = instance.params["p"], instance.params["rounds"]
        t0 = time.perf_counter()
        # A single unprotected qubit under the same depolarizing model: per round, X or Y flips the Z value
        # with probability 2p/3; over `rounds` rounds the net flip prob (odd number of flips) is
        #   p_phys = (1 - (1 - 2·q)^rounds) / 2,  q = 2p/3.
        q = 2 * p / 3
        p_phys = (1 - (1 - 2 * q) ** rounds) / 2
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"physical_error_rate": round(float(p_phys), 5), "physical_qubits": 1},
            cost={"wall_ms": round(wall, 4)},
            notes={"en": f"An unprotected qubit under the same noise over {rounds} rounds flips with "
                         f"probability {p_phys:.4f}. The encoded code wins when its logical error is below this.",
                   "es": f"Un qubit sin proteger bajo el mismo ruido en {rounds} rondas se voltea con "
                         f"probabilidad {p_phys:.4f}. El código codificado gana cuando su error lógico baja de esto."},
            optimal=True,
        )


@register_solver
class ClassicalNoiseless(Solver):
    name = "noise-classical"
    label = {"en": "Noiseless statevector · classical", "es": "Vector de estado sin ruido · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "noise"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from qiskit.quantum_info import Pauli, Statevector  # build the ideal state; the value is exact

        from qversus.solvers.qiskit_solvers import QiskitNoise

        qc = QiskitNoise._bell(instance.params["depth"])
        t0 = time.perf_counter()
        ideal = float(Statevector(qc).expectation_value(Pauli("ZZ")).real)
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"value": round(ideal, 4), "exact": True},
            cost={"wall_ms": round(wall, 4), "qubits": 2},
            notes={"en": f"A noiseless statevector simulator returns the exact ⟨Z₀Z₁⟩={ideal:.3f} for free. "
                         "At any classically-simulable scale this is the reference mitigation only "
                         "approximates, mitigation matters on hardware beyond classical reach.",
                   "es": f"Un simulador de vector de estado sin ruido devuelve el ⟨Z₀Z₁⟩={ideal:.3f} exacto "
                         "gratis. A cualquier escala simulable clásicamente esta es la referencia que la "
                         "mitigación solo aproxima, la mitigación importa en hardware fuera del alcance clásico."},
            optimal=True,
        )


@register_solver
class ClassicalFCI(Solver):
    name = "vqe-classical"
    label = {"en": "Exact diagonalization (FCI) · classical", "es": "Diagonalización exacta (FCI) · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "vqe"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import pennylane as qml  # only to BUILD the Hamiltonian; the solve is numpy eigvalsh

        from qversus.solvers.pennylane_solvers import build_h2

        H, nq = build_h2(instance.params["R_bohr"])
        t0 = time.perf_counter()
        M = qml.matrix(H, wire_order=range(nq))
        e_exact = float(np.min(np.linalg.eigvalsh(M)))
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"energy": round(e_exact, 6), "method": "exact diagonalization (FCI)", "dim": 2**nq},
            cost={"wall_ms": round(wall, 3), "dim": 2**nq, "gate_complexity": "O(d^3)"},
            notes={"en": f"Exact ground energy {e_exact:.5f} Ha by diagonalizing the {2 ** nq}×{2 ** nq} "
                         "Hamiltonian, instant. H₂ minimal-basis is trivial classically; VQE is pedagogy here.",
                   "es": f"Energía exacta {e_exact:.5f} Ha diagonalizando el Hamiltoniano {2 ** nq}×{2 ** nq} "
                         ", instantáneo. H₂ en base mínima es trivial clásicamente; VQE es pedagogía aquí."},
            optimal=True,
        )


@register_solver
class ClassicalEig(Solver):
    name = "qpe-classical"
    label = {"en": "Eigendecomposition · classical", "es": "Diagonalización · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qpe"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        phi = instance.params["phi"]
        t0 = time.perf_counter()
        # U = P(2πφ) = diag(1, e^{2πiφ}); eigenstate |1⟩ → eigenvalue e^{2πiφ}. Diagonalize exactly.
        U = np.diag([1.0, np.exp(2j * np.pi * phi)])
        eigvals = np.linalg.eigvals(U)
        phi_exact = float(np.angle(eigvals[1]) / (2 * np.pi)) % 1.0
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"phi_exact": round(phi_exact, 6), "ops": 8, "exact": True},
            cost={"wall_ms": round(wall, 4), "ops": 8, "gate_complexity": "O(d^3)"},
            notes={"en": f"Diagonalized the 2×2 U → φ={phi_exact:.4f} exactly in microseconds. For a tiny U "
                         "this is trivial; QPE matters only when U is exponentially large (e^{iHt}).",
                   "es": f"Diagonalizó la U 2×2 → φ={phi_exact:.4f} exacto en microsegundos. Para una U "
                         "minúscula es trivial; QPE importa solo cuando U es exponencialmente grande."},
            optimal=True,
        )


@register_solver
class ClassicalDFT(Solver):
    name = "qft-classical"
    label = {"en": "Discrete Fourier transform · classical", "es": "Transformada discreta de Fourier · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qft"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        n, k = instance.params["n"], instance.params["k"]
        N = 2**n
        t0 = time.perf_counter()
        v = np.zeros(N, dtype=complex)
        v[k] = 1.0
        u = np.fft.fft(v) / np.sqrt(N)            # the full, READABLE Fourier spectrum
        wall = (time.perf_counter() - t0) * 1e3
        ops = int(N * max(1, n))                  # FFT ≈ O(N log N) = O(n·2ⁿ)
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"spectrum_uniform_prob": round(1.0 / N, 6), "ops": ops, "readable": True,
                   "amp0_phase_deg": round(float(np.angle(u[0], deg=True)), 3)},
            cost={"wall_ms": round(wall, 4), "ops": ops, "gate_complexity": "O(N log N)"},
            notes={"en": f"Classical FFT computes all {N} Fourier amplitudes (readable) in ~{ops} ops. The "
                         "QFT is cheaper to apply but its output cannot be read out, that's the trade.",
                   "es": f"La FFT clásica calcula todas las {N} amplitudes (legibles) en ~{ops} ops. La QFT "
                         "es más barata de aplicar pero su salida no se puede leer, ese es el trade-off."},
            optimal=True,
        )


@register_solver
class ClassicalSearch(Solver):
    name = "grover-classical"
    label = {"en": "Linear scan · classical", "es": "Barrido lineal · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "grover"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        n, marked = instance.params["n"], set(instance.params["marked"])
        rng = np.random.default_rng(seed)
        N = 2**n
        order = rng.permutation(N)            # query items in a random order until a marked one is hit
        t0 = time.perf_counter()
        queries, found_idx = 0, None
        for x in order:
            queries += 1
            if int(x) in marked:
                found_idx = int(x)
                break
        found = format(found_idx, f"0{n}b") if found_idx is not None else "?"   # the item, in counts-key order
        wall = (time.perf_counter() - t0) * 1e3
        # The fair comparator is the EXPECTED cost, not one draw: the first of M marked items in a uniformly
        # random order of N sits at position (N+1)/(M+1) on average (the expected minimum of M distinct
        # uniform positions in 1..N). The worst case is N - M + 1.
        M = len(marked)
        expected = (N + 1) / (M + 1)
        worst = N - M + 1
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"found": found, "correct": found_idx in marked, "classical_queries": round(expected, 4),
                   "sampled_queries": queries, "worst_case_queries": worst},
            cost={"wall_ms": round(wall, 4), "oracle_queries": round(expected, 4)},
            notes={"en": f"A random scan needs (N+1)/(M+1) = {expected:.1f} queries on average to hit one of the "
                         f"{M} marked item(s) among {N} (worst case {worst}); this seeded run took {queries}. "
                         "Grover's ~(π/4)√(N/M) is the quadratic separation.",
                   "es": f"Un barrido aleatorio necesita (N+1)/(M+1) = {expected:.1f} consultas en promedio para dar "
                         f"con uno de los {M} ítem(s) marcados entre {N} (peor caso {worst}); esta corrida con "
                         f"semilla tomó {queries}. El ~(π/4)√(N/M) de Grover es la separación cuadrática."},
            optimal=True,
        )


@register_solver
class GreedyMaxCut(Solver):
    name = "maxcut-greedy"
    label = {"en": "Greedy local search · classical", "es": "Búsqueda voraz local · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "maxcut"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        n, edges = instance.params["n"], instance.params["edges"]
        rng = np.random.default_rng(seed)
        t0 = time.perf_counter()
        bits = list(rng.integers(0, 2, size=n).astype(str))

        def cut(b):
            return sum(1 for (u, v) in edges if b[u] != b[v])

        improved = True
        while improved:
            improved = False
            for q in range(n):
                flipped = bits.copy()
                flipped[q] = "1" if bits[q] == "0" else "0"
                if cut(flipped) > cut(bits):
                    bits, improved = flipped, True
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name,
            label=self.label,
            framework=self.framework,
            paradigm=self.paradigm,
            value={"cut": cut(bits), "bitstring": "".join(bits)},
            cost={"wall_ms": round(wall, 4)},
            notes={
                "en": "Single-flip local search from a random start, a trivial classical heuristic that "
                      "already reaches (or nearly reaches) the optimum on these graphs.",
                "es": "Búsqueda local de un solo flip desde un inicio aleatorio, una heurística clásica "
                      "trivial que ya alcanza (o casi) el óptimo en estos grafos.",
            },
        )


@register_solver
class ClassicalTappedChannel(Solver):
    name = "bb84-classical"
    label = {"en": "Tapped classical channel · classical", "es": "Canal clásico intervenido · clásico"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "bb84"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # The same key exchange over a classical wire, with the same random draws as the quantum run. Eve copies
        # every bit she taps perfectly and resends it untouched, so Bob's error rate is the channel's alone:
        # nothing in the data depends on whether she listened. There are no bases, so no bit is sifted away.
        from qversus.problems.bb84 import ABORT_QBER, draw_rounds

        n, f, p = instance.params["n"], float(instance.params["f"]), float(instance.params["p"])
        t0 = time.perf_counter()
        rounds = draw_rounds(n, f, p, seed)
        bob = rounds["alice_bit"] ^ rounds["flip"].astype(int)
        errors = int((bob != rounds["alice_bit"]).sum())
        q = errors / n
        known = float(rounds["eve"].mean())
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"qber": round(q, 6), "errors": errors, "key_length": n, "eve_known_fraction": round(known, 6),
                   "abort": bool(q > ABORT_QBER), "eve_present": f > 0, "detectable": False},
            cost={"wall_ms": round(wall, 3), "rounds": n},
            notes={"en": f"Over a classical wire Eve copies {known:.0%} of the {n} bits without a trace: Bob's error "
                         f"rate is {q:.4f}, the channel's alone, whether or not she listened. Copying a classical "
                         "bit disturbs nothing; that is the gap BB84 closes.",
                   "es": f"Por un cable clásico Eve copia el {known:.0%} de los {n} bits sin dejar rastro: la tasa de "
                         f"error de Bob es {q:.4f}, solo la del canal, haya escuchado o no. Copiar un bit clásico no "
                         "perturba nada; esa es la brecha que BB84 cierra."},
            optimal=True,
        )


@register_solver
class RebaseOnly(Solver):
    name = "compile-rebase"
    label = {"en": "Gate-by-gate translation · classical", "es": "Traducción compuerta a compuerta · clásica"}
    framework = "classical:numpy"
    paradigm = CLASSICAL

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "compilation"

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        # Every source gate replaced by its textbook decomposition into {CX, RZ, SX, X}, nothing merged or
        # cancelled: always correct, never clever. The optimising compilers are measured against it.
        from qversus.problems.compilation import compiled_value, rebase, source_circuit, unitary
        from qversus.problems.compilation import equivalent as same_unitary

        n = instance.params["n"]
        src = source_circuit(instance.params)
        t0 = time.perf_counter()
        out = rebase(src)
        wall = (time.perf_counter() - t0) * 1e3
        value = compiled_value(src, out, n, same_unitary(unitary(out, n), unitary(src, n)), list(range(n)))
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value=value,
            cost={"wall_ms": round(wall, 3), "qubits": n},
            notes={"en": f"Each of the {value['source']['gates']} source gates replaced by its textbook decomposition: "
                         f"{value['two_qubit']} CX, depth {value['depth']}, {value['gates']} gates. Correct (same "
                         "unitary), but nothing is merged or cancelled.",
                   "es": f"Cada una de las {value['source']['gates']} compuertas fuente reemplazada por su "
                         f"descomposición de libro: {value['two_qubit']} CX, profundidad {value['depth']}, "
                         f"{value['gates']} compuertas. Correcto (mismo unitario), pero nada se fusiona ni cancela."},
        )
