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
