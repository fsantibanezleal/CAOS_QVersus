"""Solver adapters. Importing this package registers every adapter whose framework is installed.

Each import is guarded: a missing framework (e.g. PennyLane not installed) disables only THAT adapter,
never the others, so the lab degrades gracefully and adding a framework is purely additive.
"""

import importlib

# (module, friendly framework name): extend this list to add a framework; nothing else changes.
_ADAPTER_MODULES = [
    ("qversus.solvers.classical_solvers", "classical (NumPy)"),
    ("qversus.solvers.qiskit_solvers", "Qiskit + Aer"),
    ("qversus.solvers.pennylane_solvers", "PennyLane"),
    ("qversus.solvers.cirq_solvers", "Cirq"),
    ("qversus.solvers.stim_solvers", "Stim (QEC)"),
    ("qversus.solvers.qulacs_solvers", "Qulacs"),
    ("qversus.solvers.pytket_solvers", "pytket"),
    ("qversus.solvers.hardware_solvers", "Real hardware (IBM, opt-in)"),
]

LOADED: dict[str, bool] = {}

for _mod, _fw in _ADAPTER_MODULES:
    try:
        importlib.import_module(_mod)
        LOADED[_fw] = True
    except Exception as exc:  # noqa: BLE001, a missing optional framework must not break the others
        LOADED[_fw] = False
        import warnings

        warnings.warn(f"qversus solver adapter {_mod} unavailable ({_fw}): {exc}", stacklevel=2)
