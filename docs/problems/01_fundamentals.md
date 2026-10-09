# 01 · Fundamentals

## `single-qubit`: single-qubit gates and the Bloch sphere

Walk |0⟩ through a gate sequence and read the Bloch vector `[⟨X⟩, ⟨Y⟩, ⟨Z⟩]`. X flips, H creates
superposition, Z and S add phase, RX and RY are continuous rotations.

| Parameter | Meaning |
|---|---|
| `n` | 1 |
| `gates` | list of `[name]` or `[name, angle]`, applied in order |

Instances: `sq-x` (X), `sq-h` (H), `sq-hz` (H, Z), `sq-hs` (H, S), `sq-ry` (RY(π/3)), `sq-rx` (RX(π/2)).

| Solver | `value` fields |
|---|---|
| `gates-qiskit` | `bloch`, `gates`, `norm` |
| `bit-classical` | `poles`, `states`, `retrievable_bits` (a classical bit has 2 states; a qubit's continuum still yields 1 bit on readout) |

Checked: X gives `[0, 0, -1]`; H gives `[1, 0, 0]`; H then S gives `[0, 1, 0]`; the classical bit has 2 states.
References: Nielsen and Chuang (2010), doi:10.1017/CBO9780511976667; Holevo (1973), mi.mathnet.ru/eng/ppi903.

## `qrng`: superposition and the quantum random-number generator

H on each of n qubits gives a uniform distribution over 2ⁿ outcomes (n bits of entropy); RY(θ) tilts a coin.

| Parameter | Meaning |
|---|---|
| `n` | qubits (1 to 4) |
| `theta` | optional RY angle for a biased coin |

Instances: `qrng-1` to `qrng-4` (uniform), `qrng-bias30` (RY(π/3)), `qrng-bias60` (RY(2π/3)).

| Solver | `value` fields |
|---|---|
| `qrng-qiskit` | `entropy_bits`, `max_entropy_bits`, `n_outcomes`, `uniform`, `true_randomness` |
| `qrng-classical` | `entropy_bits`, `max_entropy_bits`, `deterministic`, `true_randomness` (a seeded PRNG: high entropy, fully reproducible) |

Checked: `qrng-3` gives exactly 3.0 bits; `qrng-bias30` is not uniform and below 1 bit; the classical generator
is deterministic. References: Herrero-Collantes and Garcia-Escartin, Rev. Mod. Phys. 89, 015004 (2017),
doi:10.1103/RevModPhys.89.015004; Nielsen and Chuang (2010).

## `interference`: the single-qubit interferometer H · P(φ) · H

The Mach-Zehnder in circuit form: P(0) = cos²(φ/2), from fully constructive (φ = 0) to fully destructive (φ = π).

| Parameter | Meaning |
|---|---|
| `n` | 1 |
| `phi` | relative phase |

Instances: φ = 0, π/4, π/2, 2π/3, 3π/4, π (`itf-0` ... `itf-pi`).

| Solver | `value` fields |
|---|---|
| `interference-qiskit` | `p0`, `p1`, `fringe` (`constructive`, `destructive` or `mixed`), `phi` |
| `interference-classical` | `intensity` (a classical wave's two-path intensity), `law`, `phi` |

Checked: P(0) is 1 at φ = 0, 0 at φ = π, 0.5 at φ = π/2; the classical wave reproduces cos²(φ/2) at every
instance: interference is a wave phenomenon, not by itself a quantum advantage. References: Feynman Lectures
III-1, feynmanlectures.caltech.edu/III_01.html; Nielsen and Chuang (2010).

## `bb84`: quantum key distribution, where listening leaves errors

Alice sends random bits in random bases (Z or X), Bob measures in random bases, and they keep the rounds whose
bases matched. An intercept-resend eavesdropper on a fraction f of the rounds guesses the wrong basis half the
time and then randomises Bob's bit, adding f/4 to the error rate of the sifted key; a channel that flips a bit
with probability p adds independently, so the expected QBER is f/4 + p - f·p/2. Above about 11% QBER no secret
key survives one-way post-processing (Shor-Preskill) and Alice and Bob abort; below it, a fraction 1 - 2·h(QBER)
of the sifted key is secret. The channel's error is a Pauli Y with probability p, which flips the outcome in
either basis.

| Parameter | Meaning |
|---|---|
| `n` | qubits sent (rounds) |
| `f` | fraction of the rounds Eve intercepts and resends |
| `p` | channel error probability |

Instances: `bb84-clean` (f = 0, p = 0), `bb84-eve-all` (f = 1), `bb84-eve-half` (f = 0.5), `bb84-noise`
(p = 0.05), `bb84-eve-noise` (f = 0.5, p = 0.05), all with n = 2048; `bb84-short` (n = 128, f = 1).

| Solver | `value` fields |
|---|---|
| `bb84-qiskit` | `qber`, `expected_qber`, `stderr`, `sifted`, `errors`, `abort`, `eve_present`, `eve_known_fraction`, `secret_fraction`, `key_bits` |
| `bb84-classical` | `qber`, `errors`, `key_length`, `eve_known_fraction`, `abort`, `eve_present`, `detectable` (always false) |

`bb84-qiskit` takes every measurement probability from a Qiskit statevector (preparation, the channel's Y, the
rotation into the measuring basis), draws the rounds from the seed, and traces one representative round: Alice
sends |+⟩, Eve's Z measurement written as a CNOT onto her probe, Bob measures in X. Its trace `extra` also
carries the QBER against f at the instance's p (`qber_vs_f`) and the first 24 rounds (`sample_rounds`).
`bb84-classical` runs the same draws over a classical wire: Eve copies the bits she taps without disturbing
them, so the error rate is the channel's alone.

Checked: the outcome table is the textbook one (matched basis gives the bit, a wrong basis a fair coin, the Y
flips either basis); every instance's QBER is within four standard errors of f/4 + p - f·p/2; about half the
rounds survive sifting; Eve knows a fraction f/2 of the sifted key; the run aborts exactly on the instances with
an eavesdropper; the classical error rate is p whatever Eve does. References: Bennett and Brassard (1984),
reprinted in Theor. Comput. Sci. 560 (2014), doi:10.1016/j.tcs.2014.05.025; Shor and Preskill, Phys. Rev.
Lett. 85, 441 (2000), doi:10.1103/PhysRevLett.85.441; Scarani et al., Rev. Mod. Phys. 81, 1301 (2009),
doi:10.1103/RevModPhys.81.1301.
