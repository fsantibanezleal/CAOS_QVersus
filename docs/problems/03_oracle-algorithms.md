# 03 · Oracle algorithms

Query complexity separations: each problem counts how many calls to a black-box function a method needs.
The separations are real; the functions are tiny, so the classical methods still finish first on a clock.

## `deutsch-jozsa`: constant or balanced in one query

f: {0,1}ⁿ → {0,1} is promised constant or balanced. One quantum query decides; a deterministic classical
algorithm needs 2ⁿ⁻¹ + 1 in the worst case.

| Parameter | Meaning |
|---|---|
| `n` | input bits |
| `kind` | `constant` or `balanced` |
| `value` | the constant's value (constant instances) |
| `secret` | s for the balanced function f(x) = s·x mod 2 |

Instances: `dj-const0-3`, `dj-const1-3`, `dj-bal-101`, `dj-bal-parity`, `dj-const0-4`, `dj-bal-1011`.

| Solver | `value` fields |
|---|---|
| `dj-qiskit` | `verdict`, `correct`, `quantum_queries` (= 1) |
| `dj-classical` | `verdict`, `correct`, `classical_queries` |

Checked: both decide correctly on a constant and a balanced instance, with one quantum query. Reference:
Deutsch and Jozsa, Proc. R. Soc. Lond. A 439, 553 (1992), doi:10.1098/rspa.1992.0167.

## `bernstein-vazirani`: a hidden string in one query

f(x) = s·x mod 2. One quantum query returns s; classically each query reveals one bit, so n queries.

| Parameter | Meaning |
|---|---|
| `n` | string length (3 to 6) |
| `secret` | s; position u is qubit u |

Instances: `bv-101`, `bv-0111`, `bv-1101`, `bv-11010`, `bv-101101`, `bv-111111`.

| Solver | `value` fields |
|---|---|
| `bv-qiskit` | `recovered`, `correct`, `quantum_queries` (= 1) |
| `bv-classical` | `recovered`, `correct`, `classical_queries` (= n) |

Checked: `11010` recovered with 1 quantum query and 5 classical ones. Reference: Bernstein and Vazirani,
SIAM J. Comput. 26, 1411 (1997), doi:10.1137/S0097539796300921.

## `simon`: a hidden period, the first exponential separation

f is 2-to-1 with f(x) = f(x ⊕ s). Quantum: O(n) queries, each yielding a y with y·s = 0, then classical
linear algebra over GF(2); classical: Θ(2^{n/2}) queries to find a collision. A hybrid algorithm, and
honestly so: the post-processing is classical.

| Parameter | Meaning |
|---|---|
| `n` | input bits |
| `secret` | the period s |

Instances: `simon-2-11`, `simon-3-001`, `simon-3-101`, `simon-3-110`, `simon-3-011`, `simon-3-111`.

| Solver | `value` fields (and `extra`) |
|---|---|
| `simon-qiskit` | `recovered`, `correct`, `quantum_queries`; `extra.observed_y` |
| `simon-classical` | `recovered`, `correct`, `classical_queries` |

Checked: s = `101` recovered by both. Reference: Simon, SIAM J. Comput. 26, 1474 (1997),
doi:10.1137/S0097539796298637.
