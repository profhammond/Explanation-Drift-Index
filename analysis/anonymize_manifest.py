#!/usr/bin/env python3
"""Create the public, path-free manifest from the canonical research export."""

import argparse
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd


def token(value, prefix):
    digest = hashlib.sha256(f"EDI-ICTAI-2026|{value}".encode()).hexdigest()[:16]
    return f"{prefix}_{digest}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("output")
    args = parser.parse_args()
    source = pd.read_csv(args.source, low_memory=False)
    configuration = source["configuration"].fillna(source["dataset_domain"]).astype(str)
    image = source["image_id"].astype(str)
    pearson = pd.to_numeric(source["pearson_corr"], errors="raise").to_numpy(float)
    ssim = pd.to_numeric(source["ssim"], errors="raise").to_numpy(float)

    # Derive every released EDI field from the two primitive similarities. This
    # deliberately avoids carrying forward cached composite columns that may
    # predate a remediation or recalculation step in an upstream manifest.
    correlation = (1.0 - pearson) / 2.0
    structural = 1.0 - ssim
    primary = (correlation + structural) / 2.0
    if not np.isfinite(np.column_stack([pearson, ssim, correlation, structural, primary])).all():
        raise ValueError("Source similarities produced nonfinite released metrics.")

    public = pd.DataFrame({
        "comparison_id": [f"cmp_{index:05d}" for index in range(1, len(source) + 1)],
        "anonymous_image_id": image.map(lambda value: token(value, "img")),
        "evaluation_configuration": configuration,
        "preprocessing_condition": source["preprocess"].astype(str),
        "attribution_method": source["attribution_method"].astype(str),
        "resolution": source["resolution"].astype(int),
        "model_architecture": source["model_architecture"].fillna("EfficientNetB0"),
        "pearson_correlation": pearson,
        "ssim": ssim,
        "correlation_drift": correlation,
        "structural_drift": structural,
        "edi_primary": primary,
        "cosine_similarity": source["cosine_similarity"],
        "spearman_correlation": source["spearman_corr"],
        "mean_squared_error": source["mse"],
        "mean_absolute_error": source["mae"],
        "root_mean_squared_error": source["rmse"],
        "normalized_mean_squared_error": source["nmse_pooled"],
        "lpips_distance": source["lpips_distance"],
    })
    public = public.sort_values([
        "evaluation_configuration", "preprocessing_condition", "attribution_method",
        "resolution", "anonymous_image_id",
    ]).reset_index(drop=True)
    public["comparison_id"] = [f"cmp_{index:05d}" for index in range(1, len(public) + 1)]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    public.to_csv(output, index=False, float_format="%.15g")
    print(f"Wrote {len(public):,} rows and {len(public.columns)} columns to {output}")


if __name__ == "__main__":
    main()
