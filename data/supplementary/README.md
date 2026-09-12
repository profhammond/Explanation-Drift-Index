# Supplementary controlled analyses

This directory contains aggregate, paper-facing outputs from three completed
and audited experiments added after the original repository release:

- `construct_validation/`: controlled perturbation-severity validation;
- `attribution_implementation/`: signed-fallback provenance and sensitivity;
- `drift_source/`: fixed-model, cross-seed, and total-pipeline comparisons.

The files intentionally exclude medical images, model weights, attribution
arrays, local paths, and unfinished dissertation experiments. Run
`python analysis/verify_supplementary_results.py` to audit the released counts,
completion flags, bootstrap replicates, and paper-facing tables.

The construct-validation release contains validated aggregate summaries rather
than its 18,600-row research checkpoint table. The attribution-implementation
release includes 4,000 aggregate bootstrap replicates. The drift-source release
contains final clustered-bootstrap estimates and contrasts; it does not
authorize interpreting residuals as causal fractions.
