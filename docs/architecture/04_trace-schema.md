# 04 · Trace schema (`qversus-trace/1`)

A `Trace` (`qversus/core/trace.py`) is a replayable recording of one circuit run. It is JSON-first (via
`Trace.to_dict()` / `write_json()`), compact, and contains no framework type, so a reader in any language can
use it. Version string: `qversus.core.trace.SCHEMA_VERSION == "qversus-trace/1"`.

## Trace

| Field | Type | Content |
|---|---|---|
| `schema_version` | `str` | `"qversus-trace/1"` |
| `case_id` | `str` | the problem id |
| `title`, `concept` | `{"en","es"}` | copied from the problem |
| `qubits` | `int` | width of the traced circuit |
| `steps` | `list[Step]` | one frame per applied instruction, plus the initial `|0...0>` frame |
| `measurements` | `{"counts": {key: int}, "shots": int}` | seeded histogram sampled from the exact final state |
| `circuit_ops` | `list[{"gate", "targets", "params"}]` | flat op list (barriers excluded) for drawing the circuit |
| `provenance` | `{"engine", "engine_version", "seed", "lane", "ran_on"}` | framework and version that produced it, the seed, and `ran_on` (`"simulator"` or a backend name) |
| `references` | `list[{"label", "doi" or "url"}]` | from the problem |
| `extra` | `dict` | problem-specific blocks (Grover's `iterations`, `success_prob` and `marked`; noisy and mitigated curves; ...) |

`provenance.lane` is written as `"tbd"` by the engine; a consumer that classifies runs (for example into an
interactive lane and a precomputed lane) fills it in.

## Step

| Field | Type | Content |
|---|---|---|
| `index` | `int` | 0 for the initial frame, then 1, 2, ... |
| `gate` | `str` | upper-case instruction name (`H`, `CX`, `RZZ`, ...) or `init` |
| `targets` | `list[int]` | qubit indices |
| `label` | `{"en","es"}` | caption; defaults to `"<GATE> q[<targets>]"` |
| `statevector` | `list[{"re","im"}]` | all 2^n amplitudes after the step, rounded to 6 decimals |
| `bloch` | `list[[x, y, z]]` | per-qubit reduced Bloch vector `[<X>, <Y>, <Z>]` from the partial trace |
| `probabilities` | `list[float]` | basis-state probabilities after the step |
| `params` | `list[float]` | the gate's real scalar parameters (matrix-valued gates carry none) |

Rounding to 6 decimals keeps traces small and gzip-friendly while leaving the norm equal to 1 to float
tolerance. `Trace.nbytes()` is the UTF-8 size of the serialised JSON, which a consumer can use as a budget.

The tracer (`qversus/core/circuit_trace.py`) replays a `qiskit.QuantumCircuit` one instruction at a time on a
`Statevector` (`evolve`), records each frame (`step_of`), flattens the circuit (`circuit_ops`) and samples the
histogram from the exact final state (`measure_counts`). Measurements and barriers are skipped in the step
list; adapters for other frameworks build their circuit in Qiskit for tracing, so every framework yields the
same shape.

Read next: [05 · Reproducibility and bit order](05_reproducibility.md).
