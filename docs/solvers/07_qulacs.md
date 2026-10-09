# 07 · Qulacs

**Qulacs** (QunaSys and contributors, MIT) is a fast C++ state-vector simulator with a Python interface. Install
with the `qulacs` extra, which also brings Qiskit: the adapter simulates the circuit Qiskit builds.

## The adapter

**`statevector-qulacs`** asks the Qiskit solver of the instance for its circuit, translates every instruction
into a Qulacs `DenseMatrix` gate built from Qiskit's own matrix for that instruction, evolves |0…0⟩ in Qulacs and
compares the final state with Qiskit's. Building each gate from Qiskit's matrix means no rotation-sign or
qubit-order convention can differ between the two engines (a dense gate's first target is the least significant
bit, as in Qiskit; checked: maximum difference 0.0 on a three-qubit test circuit with H, CX, RY, CP, CCX, MCX, RZ).

It applies to the problems whose Qiskit circuit is made of ordinary gates: `single-qubit`, `interference`, `qft`,
`grover`, `bernstein-vazirani`, `deutsch-jozsa`. It reports `matches_qiskit`, `max_abs_diff` (against the
trace's 6-decimal amplitudes), `top_outcome` and `gates`; the cost holds Qulacs' wall time next to Qiskit's;
`extra.counts` are shots sampled from Qulacs' state with the shared seeded sampler.

Checked: on every instance of the six problems the final states agree to the trace's rounding.

## When it is the right tool

Large state-vector runs on a CPU, variational loops where simulation speed dominates, GPU builds (`qulacs-gpu`).
At the sizes of this catalogue (at most four qubits on these problems) both engines finish in microseconds, so the
adapter is a cross-check of correctness, not a speed claim.
