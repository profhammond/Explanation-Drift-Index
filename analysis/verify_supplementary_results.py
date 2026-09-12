#!/usr/bin/env python3
"""Audit aggregate supplementary results cited by the ICTAI paper."""

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

def load_json(path):
    return json.loads(Path(path).read_text())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/supplementary")
    parser.add_argument("--output", default="reproduced_results/supplementary_audit.json")
    args = parser.parse_args()
    root = Path(args.root)

    construct = load_json(root / "construct_validation" / "validation_status.json")
    severity = pd.read_csv(root / "construct_validation" / "severity_correlations.csv")
    measures = pd.read_csv(root / "construct_validation" / "comparison_measure_correlations.csv")
    construct_passed = bool(
        construct["run_complete"] and construct["validation_passed"]
        and construct["completed_source_maps"] == construct["expected_source_maps"] == 600
        and construct["observations"] == construct["expected_observations"] == 18_600
        and construct["errors"] == construct["duplicate_keys"] == 0
        and construct["invalid_checkpoint_files"] == 0
        and construct["maximum_edi_formula_error"] <= 1e-12
        and len(severity) == 6 and len(measures) == 10
        and np.isfinite(severity.select_dtypes("number")).all().all()
    )

    attr = root / "attribution_implementation"
    integrity = load_json(attr / "manifest_integrity_audit.json")
    decision = load_json(attr / "decision_audit.json")
    bootstrap = pd.read_csv(attr / "bootstrap_replicates.csv")
    stored = pd.read_csv(attr / "table_bootstrap_gradcampp_minus_gradcam.csv")
    recomputed = bootstrap.groupby("cohort")["gradcampp_minus_gradcam"].agg(
        replications="size", mean_difference="mean",
        ci_low=lambda x: x.quantile(0.025), ci_high=lambda x: x.quantile(0.975),
        probability_gradcampp_higher=lambda x: (x > 0).mean(),
    ).reset_index()
    merged = stored.merge(recomputed, on="cohort", suffixes=("_stored", "_recomputed"))
    fields = ["mean_difference", "ci_low", "ci_high", "probability_gradcampp_higher"]
    attr_error = max(float(np.max(np.abs(
        merged[f"{field}_stored"] - merged[f"{field}_recomputed"]
    ))) for field in fields)
    attr_passed = bool(
        integrity["passed"] and integrity["rows"] == 7_680
        and integrity["duplicate_keys"] == integrity["nonfinite_values"] == 0
        and integrity["maximum_edi_formula_error"] <= 1e-12
        and decision["manifest_integrity_passed"] and decision["fallback_rows"] == 1_081
        and len(bootstrap) == 4_000 and attr_error <= 1e-12
    )

    drift = root / "drift_source"
    preflight = load_json(drift / "preflight_status.json")
    compatibility = load_json(drift / "compatibility_status.json")
    final = load_json(drift / "final_status.json")
    contrasts = pd.read_csv(drift / "table_matched_source_contrasts.csv")
    estimates = pd.read_csv(drift / "table_matched_source_estimates.csv")
    drift_passed = bool(
        preflight["passed"] and compatibility["passed"]
        and final["run_complete"] and final["validation_passed"]
        and not final["causal_fraction_claim_authorized"]
        and len(contrasts) == final["contrast_rows_expected"] == 24
        and len(estimates) == final["source_estimate_rows_expected"] == 32
        and np.isfinite(contrasts.select_dtypes("number")).all().all()
        and np.isfinite(estimates.select_dtypes("number")).all().all()
    )

    report = {
        "construct_validation_passed": construct_passed,
        "attribution_implementation_passed": attr_passed,
        "attribution_bootstrap_maximum_reproduction_error": attr_error,
        "drift_source_decomposition_passed": drift_passed,
        "all_supplementary_checks_passed": bool(construct_passed and attr_passed and drift_passed),
        "scope_note": "Aggregate paper-facing results; no medical images, model weights, or attribution arrays are redistributed.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["all_supplementary_checks_passed"]:
        raise RuntimeError("Supplementary audit failed")

if __name__ == "__main__":
    main()
