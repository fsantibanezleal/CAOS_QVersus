"""PennyLane adapter, real PennyLane, an independent second implementation of QAOA for MaxCut.

This is the SimLab "two engines on one problem" discipline (SimPy live + Ciw analytic cross-check), here
as QAOA-Qiskit vs QAOA-PennyLane: two real frameworks must agree on ⟨C⟩ and the cut, which validates
both. PennyLane builds the cost Hamiltonian with `qml.qaoa`, evaluates ⟨C⟩ on `default.qubit`, and uses
the same deterministic (γ, β) grid as the Qiskit adapter so the head-to-head is apples-to-apples.
"""

from __future__ import annotations

import time

import numpy as np

from qversus.problems.base import Instance, Problem
from qversus.registry import register_solver
from qversus.solvers.base import QUANTUM_SIM, Solver, SolverResult

try:
    import pennylane as qml

    PENNYLANE_VERSION = qml.__version__
except Exception:  # pragma: no cover
    qml = None
    PENNYLANE_VERSION = "unknown"


def build_h2(r_bohr: float):
    """Real H₂ molecular Hamiltonian (STO-3G, 4 qubits) via PennyLane's differentiable Hartree-Fock, 
    no external chemistry backend. Shared by the VQE quantum solver and the exact-diagonalization baseline."""
    from pennylane import numpy as pnp

    coords = pnp.array([[0.0, 0.0, 0.0], [0.0, 0.0, r_bohr]])
    return qml.qchem.molecular_hamiltonian(["H", "H"], coords)


@register_solver
class PennyLaneVQE(Solver):
    name = "vqe-pennylane"
    label = {"en": "VQE (UCC double) · PennyLane", "es": "VQE (doble UCC) · PennyLane"}
    framework = "pennylane"
    paradigm = QUANTUM_SIM
    GRID = 100

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "vqe" and qml is not None

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        H, nq = build_h2(instance.params["R_bohr"])
        hf = qml.qchem.hf_state(2, nq)                 # [1,1,0,0], the Hartree-Fock reference
        dev = qml.device("default.qubit", wires=nq)

        @qml.qnode(dev)
        def energy(theta):
            qml.BasisState(hf, wires=range(nq))
            qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])  # the single excitation that captures H₂'s GS
            return qml.expval(H)

        t0 = time.perf_counter()
        thetas = np.linspace(-np.pi, np.pi, self.GRID)
        energies = [float(energy(th)) for th in thetas]
        i = int(np.argmin(energies))
        e_min, th_best = energies[i], float(thetas[i])
        wall = (time.perf_counter() - t0) * 1e3
        step = max(1, self.GRID // 40)
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"energy": round(e_min, 6), "optimal_theta": round(th_best, 4), "qubits": nq},
            cost={"wall_ms": round(wall, 1), "qubits": nq, "evaluations": self.GRID},
            notes={"en": f"VQE ground energy {e_min:.5f} Ha at θ={th_best:.3f} (HF + one double excitation, "
                         f"{nq} qubits).",
                   "es": f"Energía VQE {e_min:.5f} Ha en θ={th_best:.3f} (HF + una doble excitación, "
                         f"{nq} qubits)."},
            extra={"landscape": {"theta": [round(float(t), 4) for t in thetas[::step]],
                                 "energy": [round(e, 6) for e in energies[::step]]}},
        )


@register_solver
class PennyLaneQML(Solver):
    name = "qml-pennylane"
    label = {"en": "Quantum-kernel SVM · PennyLane", "es": "SVM de kernel cuántico · PennyLane"}
    framework = "pennylane"
    paradigm = QUANTUM_SIM

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "qml" and qml is not None

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        from sklearn.svm import SVC

        from qversus.problems.qml_classifier import QMLClassifier

        Xtr, ytr, Xte, yte = QMLClassifier.dataset(instance.params["kind"], seed=seed)
        nq = 2
        dev = qml.device("default.qubit", wires=nq)

        def feature_map(x):
            qml.AngleEmbedding(x, wires=range(nq))
            qml.IsingZZ(x[0] * x[1], wires=[0, 1])      # a 2nd-order term for expressivity

        @qml.qnode(dev)
        def overlap(x1, x2):
            feature_map(x1)
            qml.adjoint(feature_map)(x2)
            return qml.probs(wires=range(nq))

        def kernel(A, B):
            return np.array([[overlap(a, b)[0] for b in B] for a in A])  # K=|⟨φ(a)|φ(b)⟩|²

        t0 = time.perf_counter()
        K_tr = kernel(Xtr, Xtr)
        K_te = kernel(Xte, Xtr)
        clf = SVC(kernel="precomputed").fit(K_tr, ytr)
        train_acc = float(clf.score(K_tr, ytr))
        test_acc = float(clf.score(K_te, yte))
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"train_acc": round(train_acc, 3), "test_acc": round(test_acc, 3), "qubits": nq},
            cost={"wall_ms": round(wall, 1), "qubits": nq, "kernel_evals": len(Xtr) ** 2 + len(Xte) * len(Xtr)},
            notes={"en": f"Quantum fidelity-kernel SVM: train {train_acc:.2f}, test {test_acc:.2f} "
                         f"({nq} qubits, {len(Xtr)} train pts).",
                   "es": f"SVM de kernel de fidelidad cuántico: train {train_acc:.2f}, test {test_acc:.2f} "
                         f"({nq} qubits, {len(Xtr)} ptos train)."},
            extra={"n_train": len(Xtr), "n_test": len(Xte)},
        )


@register_solver
class PennyLaneQAOA(Solver):
    name = "qaoa-pennylane"
    label = {"en": "QAOA (p=1) · PennyLane", "es": "QAOA (p=1) · PennyLane"}
    framework = "pennylane"
    paradigm = QUANTUM_SIM
    GRID = 24

    def applicable(self, problem: Problem) -> bool:
        return problem.id == "maxcut" and qml is not None

    def run(self, problem, instance: Instance, seed: int, shots: int) -> SolverResult:
        import networkx as nx

        n, edges = instance.params["n"], instance.params["edges"]
        graph = nx.Graph()
        graph.add_nodes_from(range(n))
        graph.add_edges_from((int(u), int(v)) for u, v in edges)
        cost_h, mixer_h = qml.qaoa.maxcut(graph)
        dev = qml.device("default.qubit", wires=n)

        def layer(gamma, beta):
            qml.qaoa.cost_layer(gamma, cost_h)
            qml.qaoa.mixer_layer(beta, mixer_h)

        @qml.qnode(dev)
        def expval(gamma, beta):
            for w in range(n):
                qml.Hadamard(wires=w)
            layer(gamma, beta)
            return qml.expval(cost_h)

        @qml.qnode(dev)
        def probs(gamma, beta):
            for w in range(n):
                qml.Hadamard(wires=w)
            layer(gamma, beta)
            return qml.probs(wires=range(n))

        t0 = time.perf_counter()
        gammas = np.linspace(0, np.pi, self.GRID)
        betas = np.linspace(0, np.pi, self.GRID)
        # PennyLane's qaoa.maxcut cost Hamiltonian H_C = 0.5 Σ_(i,j)∈E (Z_iZ_j − I) is MINIMIZED to
        # maximize the cut (a cut edge contributes −1). So we grid-search for the MINIMUM ⟨H_C⟩, then read
        # the cut off the most-probable bitstring (exact): which is why this cross-checks the Qiskit adapter.
        best = (gammas[0], betas[0], np.inf)
        for g in gammas:
            for b in betas:
                e = float(expval(g, b))
                if e < best[2]:
                    best = (g, b, e)
        g_best, b_best = best[0], best[1]
        pr = np.asarray(probs(g_best, b_best))
        idx = int(np.argmax(pr))
        bits = format(idx, f"0{n}b")[::-1]
        cut = problem.cut_value(edges, bits)
        wall = (time.perf_counter() - t0) * 1e3
        return SolverResult(
            solver=self.name, label=self.label, framework=self.framework, paradigm=self.paradigm,
            value={"cut": cut, "bitstring": bits},
            cost={"wall_ms": round(wall, 1), "qubits": n, "evaluations": self.GRID ** 2},
            notes={"en": "Independent QAOA on PennyLane default.qubit (same (γ,β) grid as the Qiskit "
                         f"adapter); most-probable bitstring cuts {cut} edges, cross-checks Qiskit.",
                   "es": "QAOA independiente en PennyLane default.qubit (misma malla (γ,β) que el adaptador "
                         f"de Qiskit); la cadena más probable corta {cut} aristas, verifica a Qiskit."},
        )
