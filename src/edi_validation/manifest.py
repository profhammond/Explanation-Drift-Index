"""Loading and structural audit helpers for the released EDI manifest."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "comparison_id",
    "anonymous_image_id",
    "evaluation_configuration",
    "preprocessing_condition",
    "attribution_method",
    "resolution",
    "pearson_correlation",
    "ssim",
    "correlation_drift",
    "structural_drift",
    "edi_primary",
]


def load_manifest(path):
    frame = pd.read_csv(Path(path), low_memory=False)
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Manifest lacks required columns: {missing}")
    return frame


def audit_manifest(frame, expected_rows=46_080, expected_images_per_cell=40):
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Manifest lacks required columns: {missing}")
    keys = [
        "evaluation_configuration",
        "preprocessing_condition",
        "attribution_method",
        "resolution",
        "anonymous_image_id",
    ]
    numeric = [
        "pearson_correlation",
        "ssim",
        "correlation_drift",
        "structural_drift",
        "edi_primary",
    ]
    recalculated = (
        ((1.0 - frame["pearson_correlation"]) / 2.0)
        + (1.0 - frame["ssim"])
    ) / 2.0
    cell_counts = frame.groupby(keys[:-1])["anonymous_image_id"].nunique()
    report = {
        "rows": int(len(frame)),
        "expected_rows": int(expected_rows),
        "duplicate_keys": int(frame.duplicated(keys).sum()),
        "duplicate_comparison_ids": int(frame["comparison_id"].duplicated().sum()),
        "nonfinite_numeric_values": int((~np.isfinite(frame[numeric].to_numpy(float))).sum()),
        "factorial_cells": int(len(cell_counts)),
        "cells_with_unexpected_image_count": int((cell_counts != expected_images_per_cell).sum()),
        "maximum_edi_formula_error": float(np.max(np.abs(frame["edi_primary"] - recalculated))),
    }
    report["passed"] = bool(
        report["rows"] == expected_rows
        and report["duplicate_keys"] == 0
        and report["duplicate_comparison_ids"] == 0
        and report["nonfinite_numeric_values"] == 0
        and report["cells_with_unexpected_image_count"] == 0
        and report["maximum_edi_formula_error"] <= 1e-12
    )
    return report

