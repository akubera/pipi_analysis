#
# loglikelihood_1d_fit.py
#

from .gaussian import GaussianModelFSI
from lmfit import minimize, report_fit


def gauss(num, den, *, fit_range=(0.0, 0.17), model=GaussianModelFSI):
    """
    Subroutine for fitting a numerator and denominator 1D correlation
    function histogram pair.
    """

    fit_slice = num.x_axis.get_slice(fit_range)
    assert num.x_axis == den.x_axis

    q = num.x_axis.bin_centers[fit_slice]
    num_slice, den_slice = num[fit_slice], den[fit_slice]

    params = model.guess()
    # fitres = GaussianModelFSI.as_loglike(params, q, num, den)
    fitres = minimize(model.as_loglike, params, args=(q, num, den))
    report_fit(fitres)

    FIT_X = np.linspace(x[0], x[-1], 300)
    FIT_Y = model().eval(qinv_fit.params, x=FIT_X)
