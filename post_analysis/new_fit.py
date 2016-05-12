#!/usr/bin/env python
#
# post_analysis/new_fit.py
#

import sys
import numpy as np
from lmfit import report_fit
from fitting.gaussian import GaussianModel, GaussianSlopeModel, GaussianModelCoulomb
from lmfit.models import (
    LinearModel,
    PolynomialModel,
    VoigtModel,
    GaussianModel as NormalModel,
    SkewedGaussianModel,
)
from pionpion.femtolist import Femtolist
import matplotlib.pyplot as plt
from matplotlib.pyplot import scatter

fname = sys.argv[1]

femtolist = Femtolist(fname)


analysis = femtolist[0]

num, den = analysis.qinv_pair

ratio = num / den



fitslice = slice(5, 15)
x = ratio.x_axis.bin_centers[fitslice]
y = ratio.data[fitslice]
e = ratio.errors[fitslice]

lin_model = LinearModel()
lin_params = lin_model.guess(y, x=x)

lin_result = lin_model.fit(y, lin_params, weights=1.0/e, x=x)
# report_fit(lin_result)

# FIT_X = np.linspace(x[0], x[-1], 300)
# FIT_Y = model.eval(lin_result.params, x=FIT_X)
#
# plt.plot(FIT_X, FIT_Y)
# plt.errorbar(x, y, yerr=e)
# plt.show()


fitslice = slice(0, 20)
x = ratio.x_axis.bin_centers[fitslice]
y = ratio.data[fitslice]
e = ratio.errors[fitslice]

model = SkewedGaussianModel()
# model = GaussianModelCoulomb()
params = model.guess(y, x=x)

# x = np.array(x.bin_centers)

result = model.fit(y, params, weights=1.0/e, x=x)
report_fit(result)

params = result.params

plotslice = slice(0, 60)
x = ratio.x_axis.bin_centers[plotslice]
y = ratio.data[plotslice]
e = ratio.errors[plotslice]

FIT_X = np.linspace(x[0], x[-1], 300)
FIT_Y = model.eval(params, x=FIT_X)


LIN_Y = lin_model.eval(lin_result.params, x=FIT_X)


plt.plot(FIT_X, FIT_Y)
# plt.plot(FIT_X, LIN_Y)
# plt.plot(FIT_X, GaussianModelCoulomb.gammow(FIT_X), '.')
plt.errorbar(x, y, fmt='.', yerr=e)
plt.show()

# plt.savefig(fname + 'fpp.png', dpi=96)

# scatter(FIT_X, FIT_Y).show()
# model = GaussianModel() + LinearModel()
# model = CubicModel()
