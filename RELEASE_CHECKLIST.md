# Release checklist

Before making this repository public:

- Confirm the final paper title, author order, and author affiliations.
- Obtain every coauthor's approval for the code and derived-manifest release.
- Confirm that MIT is the intended code license; replace `LICENSE` if needed.
- Add the public repository URL to `CITATION.cff` and the manuscript.
- Add the final proceedings citation and DOI to `CITATION.cff` when assigned.
- Run `pytest -q` in a clean environment.
- Run all analysis scripts listed in `README.md`.
- Confirm `reproduced_results/supplementary_audit.json` reports that all checks passed.
- Confirm that the manifest audit passes and contains no local paths or filenames.
- Create a tagged release and archive it with a DOI service if desired.

The repository intentionally excludes source medical images, trained models,
and patient-derived attribution arrays. Those artifacts remain governed by their
source datasets, storage constraints, and applicable approvals.
