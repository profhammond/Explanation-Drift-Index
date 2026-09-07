"""EDI formulas and optional end-to-end attribution-map comparison."""

from __future__ import annotations

import numpy as np


def correlation_drift(pearson_correlation):
    """Transform Pearson correlation from [-1, 1] to drift in [0, 1]."""
    return (1.0 - np.asarray(pearson_correlation, dtype=float)) / 2.0


def structural_drift(ssim_value, treatment: str = "primary"):
    """Calculate structural drift using a documented SSIM treatment."""
    value = np.asarray(ssim_value, dtype=float)
    if treatment == "primary":
        return 1.0 - value
    if treatment == "zero_clipped":
        return 1.0 - np.maximum(value, 0.0)
    if treatment == "symmetric_normalized":
        return (1.0 - value) / 2.0
    raise ValueError(f"Unknown SSIM treatment: {treatment}")


def edi_primary(pearson_correlation, ssim_value, ssim_treatment: str = "primary"):
    """Calculate the equal-weight primary EDI."""
    corr = correlation_drift(pearson_correlation)
    struct = structural_drift(ssim_value, ssim_treatment)
    return (corr + struct) / 2.0


def edi_variants(corr_drift, struct_drift):
    """Return the primary and five prespecified aggregation variants."""
    corr = np.asarray(corr_drift, dtype=float)
    struct = np.asarray(struct_drift, dtype=float)
    if np.any(corr < 0) or np.any(struct < 0):
        raise ValueError("Drift components must be nonnegative.")
    return {
        "primary": (corr + struct) / 2.0,
        "structural_weighted": 0.25 * corr + 0.75 * struct,
        "correlation_weighted": 0.75 * corr + 0.25 * struct,
        "geometric": np.sqrt(corr * struct),
        "maximum": np.maximum(corr, struct),
        "rms": np.sqrt((corr**2 + struct**2) / 2.0),
    }


def normalize_map(heatmap):
    """Convert a finite two-dimensional map to an independent [0, 1] scale."""
    array = np.asarray(heatmap, dtype=np.float32)
    if array.ndim != 2:
        raise ValueError(f"Expected a two-dimensional heatmap; received {array.shape}.")
    if not np.isfinite(array).all():
        raise ValueError("Heatmap contains nonfinite values.")
    minimum, maximum = float(array.min()), float(array.max())
    if maximum <= minimum:
        raise ValueError("Zero-range or constant heatmap rejected.")
    return ((array - minimum) / (maximum - minimum)).astype(np.float32)


def _largest_valid_window(shape_a, shape_b, cap=7):
    extent = min(shape_a[0], shape_a[1], shape_b[0], shape_b[1])
    if extent < 3:
        raise ValueError("Heatmaps must be at least 3x3 for SSIM.")
    window = min(int(cap), int(extent))
    return window if window % 2 else window - 1


def compare_maps(baseline, comparison, win_size=None):
    """Calculate Pearson, SSIM, component drifts, and primary EDI.

    Pearson correlation uses all flattened pixels. If dimensions differ, the
    comparison map is resized to the baseline map using bilinear interpolation
    with anti-aliasing. Maps are normalized independently before comparison.
    """
    try:
        from skimage.metrics import structural_similarity
        from skimage.transform import resize
    except ImportError as exc:
        raise ImportError(
            "Map-level comparison requires scikit-image; install the repository requirements."
        ) from exc

    base = normalize_map(baseline)
    comp = normalize_map(comparison)
    resized = False
    if base.shape != comp.shape:
        comp = resize(
            comp,
            base.shape,
            order=1,
            preserve_range=True,
            anti_aliasing=True,
        ).astype(np.float32)
        resized = True
    corr = float(np.corrcoef(base.ravel(), comp.ravel())[0, 1])
    window = _largest_valid_window(base.shape, comp.shape) if win_size is None else int(win_size)
    if window < 3 or window % 2 == 0 or window > min(*base.shape, *comp.shape):
        raise ValueError(f"Invalid SSIM window {window} for {base.shape} and {comp.shape}.")
    ssim = float(structural_similarity(base, comp, data_range=1.0, win_size=window))
    corr_d = float(correlation_drift(corr))
    struct_d = float(structural_drift(ssim))
    return {
        "pearson_correlation": corr,
        "ssim": ssim,
        "correlation_drift": corr_d,
        "structural_drift": struct_d,
        "edi_primary": (corr_d + struct_d) / 2.0,
        "ssim_window": window,
        "alignment_resize_applied": resized,
    }
