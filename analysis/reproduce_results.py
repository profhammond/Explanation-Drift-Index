#!/usr/bin/env python3
"""Reproduce principal descriptive results from the anonymized manifest."""

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from edi_validation.manifest import audit_manifest, load_manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/edi_manifest_anonymized.csv")
    parser.add_argument("--output", default="reproduced_results")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    frame = load_manifest(args.manifest)
    audit = audit_manifest(frame)
    (output / "manifest_audit.json").write_text(json.dumps(audit, indent=2))
    if not audit["passed"]:
        raise RuntimeError(f"Manifest audit failed: {audit}")

    values = frame["edi_primary"]
    overall = pd.DataFrame([{
        "n": len(values),
        "mean": values.mean(),
        "median": values.median(),
        "standard_deviation": values.std(ddof=1),
        "interquartile_range": values.quantile(.75) - values.quantile(.25),
        "p10": values.quantile(.10),
        "p90": values.quantile(.90),
        "minimum": values.min(),
        "maximum": values.max(),
    }])
    overall.to_csv(output / "edi_distribution_overall.csv", index=False)

    for factor in [
        "evaluation_configuration", "preprocessing_condition",
        "attribution_method", "resolution",
    ]:
        summary = frame.groupby(factor, as_index=False).agg(
            n=("edi_primary", "size"),
            mean_edi=("edi_primary", "mean"),
            median_edi=("edi_primary", "median"),
            mean_correlation_drift=("correlation_drift", "mean"),
            mean_structural_drift=("structural_drift", "mean"),
        )
        summary.to_csv(output / f"edi_by_{factor}.csv", index=False)

    correlations = pd.DataFrame([
        {
            "aggregation_level": "observation",
            "n": len(frame),
            "pearson": frame[["correlation_drift", "structural_drift"]].corr("pearson").iloc[0, 1],
            "spearman": frame[["correlation_drift", "structural_drift"]].corr("spearman").iloc[0, 1],
        }
    ])
    grouped = frame.groupby(
        ["evaluation_configuration", "attribution_method"], as_index=False
    )[["correlation_drift", "structural_drift"]].mean()
    correlations.loc[1] = {
        "aggregation_level": "configuration_by_attribution_mean",
        "n": len(grouped),
        "pearson": grouped[["correlation_drift", "structural_drift"]].corr("pearson").iloc[0, 1],
        "spearman": grouped[["correlation_drift", "structural_drift"]].corr("spearman").iloc[0, 1],
    }
    correlations.to_csv(output / "component_correlations.csv", index=False)
    print(overall.to_string(index=False))
    print(f"Wrote results to {output}")


if __name__ == "__main__":
    main()

