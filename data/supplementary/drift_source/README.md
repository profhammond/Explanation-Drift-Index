# Matched drift-source pilot

This completed HAM10000 pilot compares fixed-model input-only drift, cross-seed
training-associated variability, and matched total-pipeline drift for DullRazor
and Telea using Grad-CAM and Grad-CAM++. The 40-image cohort and methods are
matched across the contributing experiments. All estimates use 5,000 bootstrap
replications clustered by image identity.

The `total_minus_input` residual is descriptive. The completion record
explicitly prohibits interpreting it as a separately identified model-training
effect or causal fraction.
