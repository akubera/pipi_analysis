#
# post_analysis/fitting/gaussian.py
#
"""
Provides a gaussian fitting model.
"""

import numpy as np
from lmfit import Model, Parameters
from post_analysis.pionpion.fit import fitfunc_qinv_gauss

HBAR_C = 0.1973269788 # GeV·fm


class GaussianModel(Model):
    """
    Model of a 'simple' Gaussian fit to a 1D femtoscopic
    correlation function. This includes the parameters norm,
    lam, and radius.
    """

    @staticmethod
    def gauss(x, radius, lam, norm):
        epart = -(x * radius / HBAR_C) ** 2
        return norm * (1.0 + lam * np.exp(epart.astype(float)))

    def __init__(self, *args, **kwargs):
        super().__init__(GaussianModel.gauss, *args, **kwargs)

    @staticmethod
    def guess(data=None, *kws):
        """
        Creates the default Parameters, or if data is given, creates naïve
        initial parameter guess based on this data
        """
        if data is not None:
            inorm = data[-1]
        else:
            inorm = 1.0

        p = Parameters()
        #           (Name,  Value,  Vary,   Min,  Max,  Expr)
        p.add_many(('norm', inorm,  True, None, None,  None),
                   ('lam',    0.5,  True, None, None,  None),
                   ('radius', 6.5,  True,  0.0, None,  None),
                  )
        return p

    @classmethod
    def as_loglike(cls, p, q_inv, num, den):
        """
        Log-Likelihood method of fitting
        """
        A, B = num, den
        C = cls.gauss(q_inv, **p)

        ApB_Cp1 = (A + B) / (C + 1)

        resid = -2 * ( A * np.log(C / A * ApB_Cp1) + B * np.log(ApB_Cp1 / B) )
        # print(resid, np.sum(resid))
        return resid

    @classmethod
    def as_resid(cls, p, q_inv, ratio, errs):
        model = cls.gauss(q_inv, **p)
        res = np.sqrt((ratio - model) ** 2 / errs ** 2)
        return res


class GaussianSlopeModel(Model):
    """
    A combination of a guassian and linear fit.
    This fits data that is expected to be gaussian with a linear
    background
    """

    @staticmethod
    def gauss(x, radius, lam, norm, intercept, slope):
        epart = -(x.astype(float) * radius / HBAR_C) ** 2
        return intercept + slope * x +  norm * (1.0 + lam * np.exp(epart.astype(float)))

    def __init__(self, *args, **kwargs):
        super().__init__(GaussianModel.gauss, *args, **kwargs)

    @staticmethod
    def guess(data=None, **kw):
        """
        Uses same parameters as GaussianModel, along with added intercept
        and slope.
        """
        p = GaussianModel.guess(data, **kws)
        #           (Name,  Value,  Vary,   Min,  Max,  Expr)
        p.add_many(('intercept', 0.0903,  True, None, None,  None),
                   ('slope',  -0.00038845,  True, None, None,  None),
                  )
        return p


class GaussianModel2D(Model):
    """
    Two dimensional gaussian fit.

    $$f(x, y) = norm * \\exp(\\frac{x^2}{2a} + \\frac{y^2}{2b})$$
    """

    @staticmethod
    def gauss(x, y, a, b, lam, norm):
        return norm * (1.0 + lam * np.exp(-(x / a) ** 2))

    def __init__(self, *args, **kwargs):
        super().__init__(self.gauss, *args, **kwargs)


class GaussianModelCoulomb(Model):

    @staticmethod
    def gauss(x, radius, lam, norm):
        r"""
        gamow factor : $F(\eta) = \frac{2\pi\eta}{\e^{2\pi\eta}-1}$
        $$\eta = \frac{1}{k a}$$
        $$a_{\pi} = \pm 387.5fm$$
        """
        epart = -(x * radius / HBAR_C) ** 2
        f = GaussianModelCoulomb.gammow(x)
        return norm * ((1.0 - lam) + lam * np.exp(epart.astype(np.float64)) * f)

    @staticmethod
    def gammow(q):
        eta = HBAR_C / (q * 387.5)
        f = 2 * np.pi * eta
        return f / (np.exp(f) - 1)

    def __init__(self, *args, **kwargs):
        super().__init__(self.gauss, *args, **kwargs)

    @staticmethod
    def guess(data=None, **kws):
        """
        Returns same guess of parameters as standard GaussianModel
        """
        p = GaussianModel.guess(data, **kws)
        return p

    @classmethod
    def as_resid(cls, p, q_inv, ratio, errs):
        model = cls.gauss(q_inv, **p)
        res = np.sqrt((ratio - model) ** 2 / errs ** 2)
        return res
