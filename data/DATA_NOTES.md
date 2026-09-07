# Data notes

`edi_manifest_anonymized.csv` is a path-free derivative of the audited 46,080-row
research manifest used for the associated ICTAI 2026 paper. It contains derived
attribution-comparison measurements and experimental factors, not medical images,
patient records, model files, local paths, or original experiment timestamps.

The stable `anonymous_image_id` preserves the repeated-measure clustering required
for image-clustered bootstrap analyses. It is not an original dataset filename.

The manifest supports independent reproduction of EDI formulas, descriptive
statistics, rankings, component correlations, sensitivity analyses, and clustered
bootstrap calculations. It does not contain the full attribution arrays and thus
does not independently reproduce Pearson correlation or SSIM from raw maps. The
`examples/` directory provides synthetic maps for demonstrating that calculation.

Blank complementary-metric values indicate that the metric was not available for
that comparison. No missing value is silently converted to zero.

