#!/usr/bin/env python3
"""Reproduce preprocessing-rank comparisons for complementary measures."""

import argparse
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

INTERNAL_CONFIGURATIONS = ["HAM10000", "ISIC 2019", "Combined"]
METRICS = {
    "cosine_similarity": "higher",
    "spearman_correlation": "higher",
    "mean_squared_error": "lower",
    "mean_absolute_error": "lower",
    "root_mean_squared_error": "lower",
    "normalized_mean_squared_error": "lower",
    "lpips_distance": "lower",
    "pearson_correlation": "higher",
    "ssim": "higher",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/edi_manifest_anonymized.csv")
    parser.add_argument("--output", default="reproduced_results")
    args = parser.parse_args()
    frame = pd.read_csv(args.manifest, low_memory=False)
    frame = frame[frame["evaluation_configuration"].isin(INTERNAL_CONFIGURATIONS)].copy()
    if len(frame) != 17_280:
        raise ValueError(f"Expected 17,280 internal rows; found {len(frame):,}")

    rank_rows, agreement_rows = [], []
    for metric, preferred_direction in METRICS.items():
        cohort = frame.dropna(subset=["edi_primary", metric]).copy()
        if cohort.empty:
            raise ValueError(f"No complete observations for {metric}")
        grouped = cohort.groupby("preprocessing_condition", as_index=False).agg(
            mean_edi=("edi_primary", "mean"),
            mean_metric=(metric, "mean"),
            observations=(metric, "size"),
        )
        grouped["edi_rank"] = grouped["mean_edi"].rank(ascending=True, method="average")
        grouped["metric_rank"] = grouped["mean_metric"].rank(
            ascending=(preferred_direction == "lower"), method="average"
        )
        grouped["absolute_rank_displacement"] = (
            grouped["edi_rank"] - grouped["metric_rank"]
        ).abs()
        for row in grouped.itertuples(index=False):
            rank_rows.append({
                "metric": metric,
                "preferred_direction": preferred_direction,
                "pairwise_complete_rows": int(len(cohort)),
                "preprocessing_condition": row.preprocessing_condition,
                "mean_edi_on_metric_cohort": row.mean_edi,
                "mean_metric": row.mean_metric,
                "edi_rank": row.edi_rank,
                "metric_rank": row.metric_rank,
                "absolute_rank_displacement": row.absolute_rank_displacement,
            })
        agreement_rows.append({
            "metric": metric,
            "constituent_of_edi": metric in {"pearson_correlation", "ssim"},
            "preferred_direction": preferred_direction,
            "pairwise_complete_rows": int(len(cohort)),
            "preprocessing_levels": int(len(grouped)),
            "spearman_rank_agreement": float(
                spearmanr(grouped["edi_rank"], grouped["metric_rank"]).statistic
            ),
            "maximum_absolute_rank_displacement": float(
                grouped["absolute_rank_displacement"].max()
            ),
        })
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rank_rows).to_csv(
        output / "complementary_metric_preprocessing_ranks.csv", index=False
    )
    agreement = pd.DataFrame(agreement_rows)
    agreement.to_csv(output / "complementary_metric_rank_agreement.csv", index=False)
    print(agreement.to_string(index=False))

if __name__ == "__main__":
    main()
