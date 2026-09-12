# Attribution-implementation robustness

This release contains the completed manifest, bootstrap, and fallback-sensitivity
outputs for 7,680 remediated Grad-CAM and Grad-CAM++ comparisons. The optional
redundant array reaudit in the source notebook was unavailable because the
remediation table did not expose usable heatmap-path columns; accordingly,
`decision_audit.json` records `map_audit_completed` as false. This does not
invalidate the released fallback-stratified analysis: the regenerated arrays
had already passed direct map-quality control in the remediation workflow.

`bootstrap_replicates.csv` contains 2,000 full-cohort and 2,000
conventional-only aggregate bootstrap differences. The released table can be
reproduced directly from those values by
`analysis/verify_supplementary_results.py`.
