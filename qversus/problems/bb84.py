"""BB84 quantum key distribution: an eavesdropper who measures leaves errors behind.

Alice sends random bits, each encoded in a random basis (Z: |0⟩, |1⟩; X: |+⟩, |−⟩). Bob measures each qubit in
a random basis; they keep the rounds where the bases matched (about half) and compare a sample to estimate the
quantum bit error rate (QBER). An intercept-resend eavesdropper must guess the basis: half the time she guesses
wrong, disturbs the state, and Bob then gets a random bit, so intercepting a fraction f of the rounds raises the
QBER by f/4. With channel error p the expected QBER is f/4 + p - f·p/2. Classically, a copied bit leaves no trace.
The genuine quantum value is that the eavesdropping is detectable; the honest limits are that BB84 needs an
authenticated classical channel, and real links trade key rate for distance.
"""

from __future__ import annotations

import math

import numpy as np

from qversus.core.rng import make_rng
from qversus.problems.base import Instance, Problem
from qversus.registry import register_problem

# Shor & Preskill (2000): with one-way error correction and privacy amplification, BB84 still yields a secret key
# while the QBER stays below about 11%; above it Alice and Bob abort.
ABORT_QBER = 0.11


def expected_qber(f: float, p: float) -> float:
    """Expected QBER of the sifted key: intercept-resend on a fraction f of the rounds and channel error p.

    Eve's wrong-basis guesses flip a sifted bit with probability f/4 and the channel flips it with probability p,
    independently, so the observed error is their exclusive or.
    """
    e = f / 4
    return e + p - 2 * e * p


def binary_entropy(q: float) -> float:
    if q <= 0 or q >= 1:
        return 0.0
    return -q * math.log2(q) - (1 - q) * math.log2(1 - q)


def secret_fraction(q: float) -> float:
    """Asymptotic secret-key fraction of the sifted key, 1 - 2·h(QBER) (Shor-Preskill), floored at zero."""
    return max(0.0, 1 - 2 * binary_entropy(q))


def draw_rounds(n: int, f: float, p: float, seed: int) -> dict[str, np.ndarray]:
    """Every random choice of an exchange, drawn once from the seed so the quantum and classical runs share them.

    Bases: 0 = Z, 1 = X. `eve` marks the intercepted rounds, `flip` the rounds the channel corrupts; `u_eve` and
    `u_bob` are the uniforms that turn a measurement probability into an outcome.
    """
    rng = make_rng(seed)
    return {
        "alice_bit": rng.integers(0, 2, n), "alice_basis": rng.integers(0, 2, n),
        "eve": rng.random(n) < f, "eve_basis": rng.integers(0, 2, n), "u_eve": rng.random(n),
        "flip": rng.random(n) < p, "bob_basis": rng.integers(0, 2, n), "u_bob": rng.random(n),
    }


def sift(rounds: dict[str, np.ndarray], bob_bit: np.ndarray) -> dict:
    """Keep the rounds where Alice's and Bob's bases matched and measure the error rate of that sifted key."""
    keep = rounds["alice_basis"] == rounds["bob_basis"]
    m = int(keep.sum())
    errors = int((rounds["alice_bit"][keep] != bob_bit[keep]).sum())
    q = errors / m if m else 0.0
    # Eve knows a sifted bit exactly when she intercepted it in the basis Alice used.
    known = rounds["eve"] & (rounds["eve_basis"] == rounds["alice_basis"])
    return {
        "sifted": m, "errors": errors, "qber": round(q, 6),
        "stderr": round(math.sqrt(q * (1 - q) / m), 6) if m else 0.0,
        "eve_known_fraction": round(float(known[keep].mean()) if m else 0.0, 6),
        "abort": bool(q > ABORT_QBER),
        "secret_fraction": round(secret_fraction(q), 6),
        "key_bits": int(m * secret_fraction(q)),
    }


@register_problem
class BB84(Problem):
    id = "bb84"
    category = "fundamentals"
    live_capable = False  # many measured rounds with classical sifting: precompute
    title = {"en": "BB84 quantum key distribution", "es": "Distribución cuántica de claves BB84"}
    concept = {
        "en": (
            "Alice sends random bits, each in a random basis (Z or X); Bob measures each in a random basis, and "
            "the two keep the rounds where their bases matched, about half. They compare a sample to estimate the "
            "quantum bit error rate (QBER). An eavesdropper who intercepts and resends must guess the basis; a "
            "wrong guess disturbs the qubit, so intercepting a fraction f of the rounds adds f/4 to the QBER, "
            "which Alice and Bob see; above about 11% no secret key survives and they abort. Over a classical "
            "channel a copied bit leaves no trace at all. That "
            "detectability is a genuine quantum capability, not a speedup; BB84 still needs an authenticated "
            "classical channel, and real links trade key rate for distance."
        ),
        "es": (
            "Alice envía bits aleatorios, cada uno en una base aleatoria (Z o X); Bob mide cada uno en una base "
            "aleatoria, y ambos conservan las rondas donde sus bases coincidieron, cerca de la mitad. Comparan una "
            "muestra para estimar la tasa de error de bits cuánticos (QBER). Una espía que intercepta y reenvía "
            "debe adivinar la base; una base equivocada perturba el qubit, así que interceptar una fracción f de "
            "las rondas suma f/4 al QBER, y Alice y Bob lo ven; sobre cerca de 11% no sobrevive clave secreta y "
            "abortan. Por un canal clásico un bit copiado no deja rastro alguno. Esa detectabilidad es una capacidad cuántica genuina, no una aceleración; BB84 sigue "
            "necesitando un canal clásico autenticado, y los enlaces reales cambian tasa de clave por distancia."
        ),
    }
    metric = {"en": "QBER of the sifted key", "es": "QBER de la clave tamizada"}
    references = [
        {"label": "Bennett & Brassard, Quantum cryptography: public key distribution and coin tossing (1984), "
                  "reprinted in Theoretical Computer Science 560 (2014)",
         "doi": "10.1016/j.tcs.2014.05.025"},
        {"label": "Shor & Preskill, Simple proof of security of the BB84 quantum key distribution protocol, "
                  "Phys. Rev. Lett. 85 (2000)",
         "doi": "10.1103/PhysRevLett.85.441"},
        {"label": "Scarani et al., The security of practical quantum key distribution, Rev. Mod. Phys. 81 (2009)",
         "doi": "10.1103/RevModPhys.81.1301"},
    ]

    def instances(self) -> list[Instance]:
        defs = [
            ("bb84-clean", "No eavesdropper, clean channel", "Sin espía, canal limpio",
             {"n": 2048, "f": 0.0, "p": 0.0}),
            ("bb84-eve-all", "Eve intercepts every qubit", "Eve intercepta cada qubit",
             {"n": 2048, "f": 1.0, "p": 0.0}),
            ("bb84-eve-half", "Eve intercepts half the qubits", "Eve intercepta la mitad de los qubits",
             {"n": 2048, "f": 0.5, "p": 0.0}),
            ("bb84-noise", "No eavesdropper, 5% channel error", "Sin espía, 5% de error de canal",
             {"n": 2048, "f": 0.0, "p": 0.05}),
            ("bb84-eve-noise", "Eve on half, 5% channel error", "Eve en la mitad, 5% de error de canal",
             {"n": 2048, "f": 0.5, "p": 0.05}),
            ("bb84-short", "Short exchange, Eve on every qubit", "Intercambio corto, Eve en cada qubit",
             {"n": 128, "f": 1.0, "p": 0.0}),
        ]
        out = []
        for iid, en, es, params in defs:
            q = expected_qber(params["f"], params["p"])
            out.append(Instance(
                iid, {"en": en, "es": es}, params,
                {"en": f"{params['n']} rounds, Eve on {params['f']:.0%}, channel error {params['p']:.0%}: expected "
                       f"QBER f/4 + p - f·p/2 = {q:.4f}.",
                 "es": f"{params['n']} rondas, Eve en {params['f']:.0%}, error de canal {params['p']:.0%}: QBER "
                       f"esperado f/4 + p - f·p/2 = {q:.4f}."},
            ))
        return out
