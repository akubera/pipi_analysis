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
        # print("Class::", cls)
        model = cls.gauss(q_inv, **p)
        res = np.sqrt((ratio - model) ** 2 / errs ** 2)
        return res


class GaussianSlopeModel(Model):
    """
    A combination of a guassian and linear fit.
    This fits data that is expected to be gaussian with a linear background
    """

    @staticmethod
    def gauss(x, radius, lam, norm, intercept, slope):
        epart = -(x * radius / HBAR_C) ** 2
        linpart = intercept + slope * x
        return linpart + GaussianModel.guess(x, norm * (1.0 + lam * np.exp(epart.astype(float))))

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
    """
    Femtoscopic model incorporating quantum statistics and Coulomb FSI.
    """

    @staticmethod
    def gauss(x, radius, lam, norm):
        r"""
        gamow factor : $F(\eta) = \frac{2\pi\eta}{\e^{2\pi\eta}-1}$
        $$\eta = \frac{1}{k a}$$
        $$a_{\pi} = \pm 387.5fm$$
        """
        epart = -(x * radius / HBAR_C) ** 2
        f = np.nan_to_num(GaussianModelCoulomb.gammow(x))
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



class GaussianModelFSI(Model):
    """
    Femtoscopic model incorporating quantum statistics and Coulomb FSI.
    """

    from scipy.interpolate import interp1d

    CC_y = [0.0, 0.09021857522430664, 0.35252963674993537, 0.5680294502329946, 0.6965517352286248, 0.7775404382348255, 0.8315140976146107, 0.8690138853776657, 0.8959912696802774, 0.9161609242972861, 0.9313239619422005, 0.9431200840605862, 0.9522426012515995, 0.9596049512017558, 0.9653974229352557, 0.9702722176631272, 0.9738810367787724, 0.9769579108975665, 0.9795654278494806, 0.9817545408814998, 0.9835675123635027, 0.985247611164176, 0.9865211418075185, 0.9877035763811198, 0.9886618165638349, 0.9895406946851654, 0.9903452706493048, 0.9910092959399456, 0.991616949629362, 0.9921923802531301, 0.9927012990351702, 0.9931151079838972, 0.9935215914532574, 0.9938980027628621, 0.9942643533837463, 0.9945492828464315, 0.9948449566852668, 0.9951294848942347, 0.9953477957711657, 0.9956176714712986, 0.9957965489236554, 0.9959915865696483, 0.9961664488325214, 0.9963449601795403, 0.9964913131207312, 0.9966683125482881, 0.9968223726628401, 0.9969338226936417, 0.9970420464812869, 0.9971559947659605, 0.997269377927236]
    CC_x = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.012, 0.014, 0.016, 0.018, 0.02, 0.022, 0.024, 0.026000000000000002, 0.028, 0.03, 0.032, 0.034, 0.036000000000000004, 0.038, 0.04, 0.042, 0.044, 0.046, 0.048, 0.05, 0.052000000000000005, 0.054, 0.056, 0.058, 0.06, 0.062, 0.064, 0.066, 0.068, 0.07, 0.07200000000000001, 0.074, 0.076, 0.078, 0.08, 0.082, 0.084, 0.086, 0.088, 0.09, 0.092, 0.094, 0.096, 0.098, 0.1]
    CC = interp1d(CC_x, CC_y, kind='cubic', bounds_error=False, fill_value=1.0)


    @staticmethod
    def gauss(x, radius, lam, norm):
        r"""
        gamow factor : $F(\eta) = \frac{2\pi\eta}{\e^{2\pi\eta}-1}$
        $$\eta = \frac{1}{k a}$$
        $$a_{\pi} = \pm 387.5fm$$
        """

        epart = -(x * radius / HBAR_C) ** 2
        fsi_factor = GaussianModelFSI.CC(x)
        return norm * ((1.0 - lam) + lam * np.exp(epart.astype(np.float64)) * fsi_factor)


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
        # print("Class>", cls)
        model = GaussianModelFSI.gauss(q_inv, **p)
        res = np.sqrt((ratio - model) ** 2 / errs ** 2)
        return res
