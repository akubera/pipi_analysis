#
# post_analysis/fitting/gaussian3d.py
#
"""
Gaussian 3d
"""


import numpy as np
from lmfit import Model, Parameters
from ..pionpion.fit import fitfunc_qinv_gauss

HBAR_C = 0.1973269788 # GeV·fm


class Gaussian3dModel(Model):
    """
    Three Dimensional gaussian fit.

    $$f(x, y, z) = norm * \\exp(\\frac{x^2}{2a} + \\frac{y^2}{2b})$$
    """

    @staticmethod
    def guess(data=None, *kws):
        """
        Creates the default Parameters, or if data is given, creates naïve
        initial parameter guess based on this data
        """
        if data is None:
            inorm = 1.0
        elif isinstance(data, tuple):
            num, den = data
            inorm = num[-1] / den[-1]
        else:
            inorm = data[-1]

        p = Parameters()
        #           (Name,  Value,  Vary,   Min,  Max,  Expr)
        p.add_many(('norm', inorm,  True, None, None,  None),
                   ('lam',    0.5,  True, None, None,  None),
                   ('r_o',    5.5,  True,  0.0, None,  None),
                   ('r_s',    5.5,  True,  0.0, None,  None),
                   ('r_l',    5.5,  True,  0.0, None,  None),
                  )
        return p

    @staticmethod
    def gauss(q, norm, lam, r_o, r_s, r_l):
        """
        Parameters
        ----------
        q : 3-dim nd.array
            The center of q-bins related to the

        """
        epart = - ((q[:, 0] * r_o) ** 2 + (q[:, 1] * r_s) ** 2 + (q[:, 2] * r_l) ** 2) / HBAR_C ** 2
        print('fitting:', epart[100:110], q.shape, r_o, r_s, r_l)
        return norm * (1.0 + lam * np.exp(epart.astype(float)))

    def __init__(self, *args, **kwargs):
        super().__init__(self.gauss, *args, **kwargs)

    @classmethod
    def as_chisqr(cls, params, q_inv, ratio, errs):
        model = cls.gauss(q_inv, **p)
        res = np.sqrt(((ratio - model) ** 2 / errs ** 2).astype(np.float64))
        return res

    @classmethod
    def as_loglike(cls, params, q, num, den):
        """
        Log-Likelihood method of fitting
        """
        skip_zeros = (den != 0.0) & (num != 0.0)
        A, B = num[skip_zeros], den[skip_zeros]
        C = cls.gauss(q[skip_zeros], **params)
        ApB_Cp1 = (A + B) / (C + 1)
        log1 = np.log((C / A * ApB_Cp1).astype(np.float64))
        log2 = np.log((ApB_Cp1 / B).astype(np.float64))

        resid = -2 * (A * log1  + B * log2)
        return resid


    @classmethod
    def get_chisquared(cls, params, q_inv, num, den):
        return 0
