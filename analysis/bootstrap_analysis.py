#!/usr/bin/env python3
"""Configuration-stratified, image-clustered bootstrap for mean EDI."""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from edi_validation.manifest import load_manifest


def clustered_bootstrap(frame, iterations=2000, seed=2026):
    rng = np.random.default_rng(seed)
    groups = {
        name: list(group.groupby("anonymous_image_id")["edi_primary"])
        for name, group in frame.groupby("evaluation_configuration")
    }
    estimates = np.empty(iterations)
    for iteration in range(iterations):
        values = []
        for image_groups in groups.values():
            chosen = rng.integers(0, len(image_groups), size=len(image_groups))
            values.extend(image_groups[index][1].to_numpy(float) for index in chosen)
        estimates[iteration] = np.concatenate(values).mean()
    return estimates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/edi_manifest_anonymized.csv")
    parser.add_argument("--output", default="reproduced_results")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    frame = load_manifest(args.manifest)
    estimates = clustered_bootstrap(frame, args.iterations, args.seed)
    result = pd.DataFrame([{
        "iterations": args.iterations,
        "seed": args.seed,
        "point_estimate": frame["edi_primary"].mean(),
        "bootstrap_mean": estimates.mean(),
        "ci_2_5": np.quantile(estimates, .025),
        "ci_97_5": np.quantile(estimates, .975),
    }])
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    result.to_csv(output / f"clustered_bootstrap_{args.iterations}.csv", index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()

