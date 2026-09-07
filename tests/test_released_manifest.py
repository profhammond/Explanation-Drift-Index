from pathlib import Path
from edi_validation.manifest import audit_manifest, load_manifest


def test_release_manifest_integrity():
    path = Path(__file__).parents[1] / "data" / "edi_manifest_anonymized.csv"
    report = audit_manifest(load_manifest(path))
    assert report["passed"], report
    assert report["rows"] == 46_080
    assert report["factorial_cells"] == 1_152

