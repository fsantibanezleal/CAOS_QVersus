"""Problem catalog. Importing this package registers every problem (one import line per module).
Adding a problem = add its module here; nothing else changes.
"""

from qversus.problems import (  # noqa: F401  (import = registration)
    bernstein_vazirani,
    chsh,
    deutsch_jozsa,
    grover,
    interference,
    maxcut,
    noise,
    qec_repetition,
    qec_surface,
    qft,
    qml_classifier,
    qpe,
    qrng,
    shor,
    simon,
    single_qubit,
    state_prep,
    superdense,
    teleportation,
    vqe,
)

__all__ = ["state_prep", "maxcut", "bernstein_vazirani", "deutsch_jozsa", "simon", "grover", "qft", "qpe",
           "shor", "vqe", "qml_classifier", "noise", "qec_repetition", "qec_surface", "chsh", "teleportation",
           "superdense", "single_qubit", "qrng", "interference"]
