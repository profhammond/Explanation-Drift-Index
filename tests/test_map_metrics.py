import numpy as np
import pytest

from edi_validation.metrics import compare_maps, normalize_map


def test_identical_maps_have_zero_drift():
    heatmap = np.arange(49, dtype=float).reshape(7, 7)
    result = compare_maps(heatmap, heatmap)
    assert result["pearson_correlation"] == pytest.approx(1.0)
    assert result["ssim"] == pytest.approx(1.0)
    assert result["edi_primary"] == pytest.approx(0.0)


def test_constant_map_rejected():
    with pytest.raises(ValueError):
        normalize_map(np.ones((7, 7)))

