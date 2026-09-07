#!/usr/bin/env python3
"""Reproduce EDI formulation and SSIM-treatment sensitivity summaries."""

import argparse
from pathlib import Path
import pandas as pd

from edi_validation.metrics import correlation_drift, structural_drift, edi_variants
from edi_validation.manifest import load_manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/edi_manifest_anonymized.csv")
    parser.add_argument("--output", default="reproduced_results")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    frame = load_manifest(args.manifest)
    corr = correlation_drift(frame["pearson_correlation"])
    variants = edi_variants(corr, structural_drift(frame["ssim"]))
    for name, values in variants.items():
        frame[f"edi_{name}"] = values
    frame["edi_zero_clipped_ssim"] = (corr + structural_drift(frame["ssim"], "zero_clipped")) / 2
    frame["edi_symmetric_ssim"] = (corr + structural_drift(frame["ssim"], "symmetric_normalized")) / 2

    edi_columns = [column for column in frame if column.startswith("edi_")]
    summary = frame[edi_columns].agg(["mean", "median", "std"]).T.reset_index(names="formulation")
    summary.to_csv(output / "formulation_summary.csv", index=False)
    ranks = []
    for column in edi_columns:
        means = frame.groupby("preprocessing_condition")[column].mean().sort_values()
        ranks.extend({"formulation": column, "preprocessing_condition": key,
                      "mean": value, "rank": rank}
                     for rank, (key, value) in enumerate(means.items(), start=1))
    pd.DataFrame(ranks).to_csv(output / "formulation_preprocessing_ranks.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

