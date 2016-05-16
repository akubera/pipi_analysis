#
#
#

import lmfit
import pytest
import numpy as np
import post_analysis.fitting.gaussian as gaussian


@pytest.mark.parametrize('cls', [
    gaussian.GaussianModel,
    gaussian.GaussianModelCoulomb,
])
def test_guess_methods(cls):
    p = cls.guess()

    assert 'radius' in p
    assert 'lam' in p
    assert 'norm' in p


@pytest.mark.parametrize('cls', [
    gaussian.GaussianModel,
    gaussian.GaussianModelCoulomb,
])
def test_gaussian_fit(cls):
    p = cls.guess()
    R, L, N = 8.2, 0.7, 1.4
    p['radius'].value = R
    p['norm'].value = N
    p['lam'].value = L
    C = 100

    np.random.seed(42)
    x = np.linspace(0.0, 1.0, C)
    e = np.random.normal(0.0, 0.23, C)
    y = cls.gauss(x, **p) + e

    # fit = gaussian.GaussianModel.fit(y, p, x=x)
    fit = lmfit.minimize(cls.as_resid, p, args=(x, y, e))
    lmfit.report_fit(fit)
    assert np.fabs(fit.params['radius'] - R) < fit.params['radius'].stderr
    assert np.fabs(fit.params['lam'] - L) < fit.params['lam'].stderr
    assert np.fabs(fit.params['norm'] - N) < fit.params['norm'].stderr
