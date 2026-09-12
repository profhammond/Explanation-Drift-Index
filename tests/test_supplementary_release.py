import json
import os
from pathlib import Path
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).parents[1]


def run_analysis(script, *arguments):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [sys.executable, str(ROOT / "analysis" / script), *map(str, arguments)],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def test_complementary_metric_release(tmp_path):
    run_analysis("complementary_metric_analysis.py", "--output", tmp_path)
    agreement = pd.read_csv(tmp_path / "complementary_metric_rank_agreement.csv")
    nonconstituent = agreement[~agreement["constituent_of_edi"]]
    cosine = agreement.loc[agreement["metric"].eq("cosine_similarity")].iloc[0]
    assert int(cosine["pairwise_complete_rows"]) == 12_211
    assert float(cosine["spearman_rank_agreement"]) == 0.942857142857143
    assert float(nonconstituent["spearman_rank_agreement"].min()) == 0.8857142857142858
    assert float(nonconstituent["maximum_absolute_rank_displacement"].max()) == 1.0


def test_supplementary_audit(tmp_path):
    output = tmp_path / "supplementary_audit.json"
    run_analysis("verify_supplementary_results.py", "--output", output)
    report = json.loads(output.read_text())
    assert report["all_supplementary_checks_passed"]
    assert report["attribution_bootstrap_maximum_reproduction_error"] <= 1e-12
