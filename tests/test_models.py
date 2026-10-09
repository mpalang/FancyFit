import numpy as np
import pytest
from scipy.signal import fftconvolve
from scipy.special import erf

from utils.models import exp_decay, exp_decay_conv_gauss


def test_exp_decay_zero_before_onset():
    x = np.linspace(-5, -0.01, 50)
    assert np.all(exp_decay(x, x0=0.0, A=2.0, tau=3.0) == 0.0)


def test_exp_decay_values():
    A, tau = 2.0, 3.0
    assert exp_decay(0.0, 0.0, A, tau) == pytest.approx(A)
    assert exp_decay(tau, 0.0, A, tau) == pytest.approx(A / np.e)


def test_conv_gauss_matches_numerical_convolution():
    x0, fwhm, A, tau = 5.0, 2.0, 1.5, 10.0
    dx = 0.005
    x = np.arange(-50, 150, dx)
    s = fwhm / (2 * np.sqrt(2 * np.log(2)))
    n = int(8 * s / dx)
    k = dx * np.arange(-n, n + 1)  # symmetric kernel, centred on 0
    irf = np.exp(-k**2 / (2 * s**2))
    irf /= irf.sum()
    numeric = fftconvolve(exp_decay(x, x0, A, tau), irf, mode="same")
    analytic = exp_decay_conv_gauss(x, x0, fwhm, A, tau)
    inner = slice(len(k), -len(k))  # ignore edge effects of the convolution
    # the sampled step at x0 limits the numerical result to an error of order dx
    np.testing.assert_allclose(analytic[inner], numeric[inner], atol=0.005)


def test_conv_gauss_reduces_to_decay_for_narrow_irf():
    x = np.linspace(1, 50, 200)  # away from the onset
    np.testing.assert_allclose(
        exp_decay_conv_gauss(x, 0.0, 1e-4, 1.0, 10.0),
        exp_decay(x, 0.0, 1.0, 10.0),
        rtol=1e-6,
    )


def test_conv_gauss_is_finite_for_extreme_parameters():
    x = np.linspace(-1000, 1000, 2001)
    y = exp_decay_conv_gauss(x, 0.0, 50.0, 1.0, 0.01)
    assert np.all(np.isfinite(y))


def test_conv_gauss_matches_erf_closed_form():
    """Cross-check against the erf form of the same convolution."""
    x0, fwhm, A, tau = 5.0, 2.0, 1.5, 10.0
    x = np.linspace(-20, 100, 2000)
    s = fwhm / (2 * np.sqrt(2 * np.log(2)))
    t = x - x0
    expected = (A / 2) * np.exp(s**2 / (2 * tau**2) - t / tau) * (
        1 + erf((t - s**2 / tau) / (s * np.sqrt(2)))
    )
    np.testing.assert_allclose(
        exp_decay_conv_gauss(x, x0, fwhm, A, tau), expected, atol=1e-9
    )
