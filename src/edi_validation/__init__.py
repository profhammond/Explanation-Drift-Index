"""Public calculation and validation utilities for the Explanation Drift Index."""

from .metrics import (
    correlation_drift,
    structural_drift,
    edi_primary,
    edi_variants,
    normalize_map,
    compare_maps,
)
from .manifest import audit_manifest, load_manifest

__all__ = [
    "correlation_drift",
    "structural_drift",
    "edi_primary",
    "edi_variants",
    "normalize_map",
    "compare_maps",
    "audit_manifest",
    "load_manifest",
]

