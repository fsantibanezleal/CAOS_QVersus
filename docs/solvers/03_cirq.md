# 03 · Cirq

**Cirq** (Google, Apache-2.0) is a framework for near-term circuits with explicit qubit topology and
moment-level control. Install with the `cirq` extra (`cirq-core`, not the full metapackage: the vendor
modules are not needed for simulation).

## The adapter

**`qaoa-cirq`** is the third independent QAOA implementation for MaxCut: `cirq.LineQubit`s, a Hadamard
layer, `cirq.ZZ(u, v) ** γ` per edge and `cirq.rx(2β)` mixers, simulated with `cirq.Simulator` over the same
(γ, β) grid; ⟨C⟩ is read straight from `final_state_vector` and the cut from the most probable basis state.
Cirq orders basis states big-endian (qubit 0 is the most significant bit), the opposite of Qiskit, so that
index written in binary already reads position u = qubit u = vertex u: the same meaning as the other
adapters' bit strings, with no conversion.

It was added as one module and one line in the adapter list, with no change anywhere else: the extension
contract in practice.

## When it is the right tool

Explicit hardware topology and moment scheduling, Google-style device models, OpenFermion and qsim
integration. Smaller vendor coverage than Qiskit and a thinner noise library.

Reference: Cirq documentation, quantumai.google/cirq.
