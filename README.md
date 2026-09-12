# Explanation Drift Index validation materials

This repository accompanies **“Evaluating a Composite Explanation Drift Index
Across Attribution Methods and Medical-Imaging Configurations”** (ICTAI 2026).
It provides a path-free, anonymized 46,080-comparison manifest and independently
executable code for calculating and auditing the Explanation Drift Index (EDI).

## Scope

EDI summarizes disagreement between paired attribution maps:

```text
correlation_drift = (1 - Pearson correlation) / 2
structural_drift  = 1 - SSIM
EDI                = (correlation_drift + structural_drift) / 2
```

Lower EDI means greater agreement between the paired maps. It does **not** imply
better preprocessing, explanation correctness, causal faithfulness, localization
accuracy, or clinical validity. EDI currently has no clinically validated cutoff.

## Released data

`data/edi_manifest_anonymized.csv` contains 46,080 repeated paired comparisons:

- 8 evaluation configurations
- 6 preprocessing conditions
- 6 attribution methods
- 4 input resolutions
- 40 images per factorial cell
- 1,152 complete factorial cells

The comparison count is not equivalent to 46,080 independent images. Stable
anonymous image identifiers preserve the clustering needed for resampling.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements.txt
```

## Verify the release

```bash
pytest -q
python analysis/reproduce_results.py
python analysis/formulation_sensitivity.py
python analysis/bootstrap_analysis.py --iterations 2000
python analysis/complementary_metric_analysis.py
python analysis/verify_supplementary_results.py
```

Generated tables are written to `reproduced_results/`.
Reference values for checking a successful run are stored in
`data/expected_results.json`; release-file hashes are recorded in `SHA256SUMS`.

## Map-level calculation

`edi_validation.metrics.compare_maps` independently normalizes two finite 2-D
maps, rejects zero-range maps, aligns a mismatched comparison map using bilinear
interpolation with anti-aliasing, computes Pearson correlation over all flattened
pixels, uses the largest valid odd SSIM window up to 7 by default, and returns the
two drift components and primary EDI.

Synthetic paired arrays in `examples/` demonstrate this interface without
redistributing medical images or derived patient imagery.

## Complementary and controlled analyses

`analysis/complementary_metric_analysis.py` reproduces preprocessing-rank
comparisons between EDI and complementary measures for the 17,280-row internal
cohort. Each comparison uses its pairwise-complete rows and reports the actual
denominator because cosine and Spearman values are unavailable for some
remediated Grad-CAM and Grad-CAM++ records.

Aggregate outputs for the completed construct-validation,
attribution-implementation, and matched drift-source experiments are under
`data/supplementary/`. Their scope and interpretation limits are documented in
`data/supplementary/README.md` and `RELEASE_NOTES_CAMERA_READY.md`.

## Recreating the anonymized manifest

The exact release transformation is documented in
`analysis/anonymize_manifest.py`:

```bash
python analysis/anonymize_manifest.py CANONICAL_MANIFEST.csv data/edi_manifest_anonymized.csv
```

Local paths, heatmap paths, model paths, source filenames, progress records, and
timestamped experiment identifiers are excluded from the public export.
Correlation drift, structural drift, and primary EDI are recalculated from the
released Pearson-correlation and SSIM values rather than copied from cached
composite columns in the research manifest.

All alternative-formulation results are likewise recalculated by
`analysis/formulation_sensitivity.py`. This ensures that sensitivity results use
the final remediated primitive similarity values for every released comparison.

## Limitations

The released manifest reproduces calculations from stored similarity values but
does not include all source attribution arrays. Therefore, it validates EDI and
the reported aggregate analyses, not every upstream attribution-generation step.
Source medical images remain subject to their original providers' licenses.

## Citation

See `CITATION.cff`. Add the final IEEE proceedings citation and DOI when assigned.

## License

The code is released under the MIT License. The derived manifest is provided for
scholarly reproducibility; users remain responsible for complying with the terms
of the original medical-image datasets.
