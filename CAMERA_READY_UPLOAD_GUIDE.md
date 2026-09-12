# GitHub update instructions

The archive contains the complete updated repository. To revise the public
GitHub repository without deleting its history:

1. Extract this archive locally.
2. Copy the contents of the extracted `EDI-validation` folder into the root of
   the existing `Explanation-Drift-Index` checkout, preserving the directory
   structure.
3. Review the Git diff. The existing manifest and core implementation should be
   unchanged; the README, release checklist, expected results, reproduced
   results, tests, checksums, and supplementary materials should be added or
   updated.
4. In a clean Python environment, run the installation and verification
   commands in `README.md`.
5. Confirm that `reproduced_results/supplementary_audit.json` contains
   `"all_supplementary_checks_passed": true` and run `sha256sum -c SHA256SUMS`.
6. Commit and push only after verifying that no medical images, model weights,
   attribution arrays, credentials, or local filesystem paths appear in the
   staged changes.

Do not add architecture-generalization, BT MRI, lesion-localization, or other
unfinished dissertation experiments to this paper-specific release.
