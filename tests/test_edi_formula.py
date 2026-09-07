import numpy as np

from edi_validation.metrics import correlation_drift, structural_drift, edi_primary, edi_variants


def test_known_values():
    assert correlation_drift(1.0) == 0.0
    assert correlation_drift(0.0) == 0.5
    assert correlation_drift(-1.0) == 1.0
    assert structural_drift(1.0) == 0.0
    assert structural_drift(-1.0) == 2.0
    assert edi_primary(1.0, 1.0) == 0.0
    assert edi_primary(-1.0, -1.0) == 1.5


def test_variant_shapes():
    values = edi_variants(np.array([0.1, 0.2]), np.array([0.3, 0.4]))
    assert set(values) == {
        "primary", "structural_weighted", "correlation_weighted",
        "geometric", "maximum", "rms",
    }
    assert all(value.shape == (2,) for value in values.values())

