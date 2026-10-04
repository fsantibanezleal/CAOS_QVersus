# 02 · Entanglement

## `state-prep`: Bell, GHZ and W states

Prepare an entangled state and report its fidelity with the target.

| Parameter | Meaning |
|---|---|
| `kind` | `bell`, `ghz` or `w` |
| `variant` | for Bell: `phi_plus`, `phi_minus`, `psi_plus`, `psi_minus` |
| `n` | qubits (2 for Bell, 3 or 4 for GHZ, 3 for W) |

Instances: the four Bell states, `ghz-3`, `ghz-4`, `w-3`.

| Solver | `value` fields |
|---|---|
| `state-qiskit` | `fidelity`, `shots` (cost: `depth`, `qubits`) |
| `state-classical` | `nonzero_probabilities` (the amplitudes written down directly; trivial at this size) |

Checked: Φ⁺ has probability 0.5 on |00⟩ and on |11⟩ and its counts contain only `00` and `11`.
References: Nielsen and Chuang (2010); Dür, Vidal and Cirac, Phys. Rev. A 62, 062314 (2000),
doi:10.1103/PhysRevA.62.062314 (GHZ and W are inequivalent classes).

## `chsh`: the CHSH inequality

S = E(a0,b0) + E(a0,b1) + E(a1,b0) − E(a1,b1). Local hidden variables give |S| ≤ 2; quantum mechanics
reaches Tsirelson's bound 2√2 on a Bell state at the optimal angles. A genuine quantum effect, not a speedup.

| Parameter | Meaning |
|---|---|
| `a0`, `a1`, `b0`, `b1` | measurement angles of Alice and Bob |
| `entangled` | Bell state (`true`) or a product state (`false`) |
| `n` | 2 |

Instances: `chsh-optimal`, `chsh-suboptimal`, `chsh-weak`, `chsh-aligned`, `chsh-rotated`, `chsh-product`.

| Solver | `value` fields |
|---|---|
| `chsh-qiskit` | `S`, `correlators`, `exceeds_classical`, `tsirelson_bound` |
| `chsh-classical` | `max_S` (= 2), `model` |

Checked: the optimal setting gives S = 2√2 within 1e-3 and exceeds 2; the product state does not; the
classical maximum is 2. References: Clauser, Horne, Shimony and Holt, Phys. Rev. Lett. 23, 880 (1969),
doi:10.1103/PhysRevLett.23.880; the 2022 Nobel Prize in Physics summary, nobelprize.org.

## `teleportation`: move an unknown qubit with entanglement and two classical bits

The coherent (deferred-measurement) form, so the trace shows the Bloch vector moving from Alice's qubit to Bob's.

| Parameter | Meaning |
|---|---|
| `theta`, `phi` | the input state cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩ |
| `n` | 3 |

Instances: |0⟩, |1⟩, |+⟩, |−⟩, |i⟩ and a generic state (θ = π/3, φ = π/4).

| Solver | `value` fields |
|---|---|
| `teleport-qiskit` | `fidelity`, `input_bloch`, `output_bloch`, `perfect` |
| `teleport-classical` | `best_fidelity` (the measure-and-resend bound, 2/3 on average), `strategy` |

Checked: fidelity above 0.999 and identical input and output Bloch vectors on the generic state; the classical
strategy stays below 0.7. References: Bennett et al., Phys. Rev. Lett. 70, 1895 (1993),
doi:10.1103/PhysRevLett.70.1895; Nielsen and Chuang (2010).

## `superdense`: two classical bits in one transmitted qubit

| Parameter | Meaning |
|---|---|
| `message` | `00`, `01`, `10` or `11` (encoded by I, X, Z, ZX) |
| `n` | 2 |

| Solver | `value` fields |
|---|---|
| `superdense-qiskit` | `decoded`, `message`, `correct`, `bits_decoded`, `qubits_sent` |
| `superdense-classical` | `bits_per_qubit` (= 1), `qubits_needed_for_2_bits` |

Checked: every message decodes correctly; the classical carrier moves one bit. References: Bennett and Wiesner,
Phys. Rev. Lett. 69, 2881 (1992), doi:10.1103/PhysRevLett.69.2881; Nielsen and Chuang (2010).
