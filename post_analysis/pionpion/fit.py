#
# post_analysis/fit.py
#

import numpy as np


HBAR_C = 0.1973269788 # GeV·fm


def fitfunc_qinv(params, q, data=None):
    """
    fitfunc_qinv
    ~~~~~~~~~~~~
    1D Gaussian fit

    params:
        radius - The qinv radius
        lam - The lambda parameter
    q: An array of array
    data: {optional} observed data to which we will calculate the residual

    .. math::

        CF(q_{inv}) = λ exp( -(q_{inv} * R)^2 )

    """

    t = -(q * params['radius']) ** 2
    model = 1 + params['lam'] * np.exp(list(t))

    if data is None:
        return model

    shape = np.shape(data)
    func_count = shape[0] / 2

    if func_count % 1:
        raise ValueError("Data shape not multiple of 2. Mismatched data and errors")

    # resid = sum(np.sqrt((data[i] - model) ** 2 / data[i + 1] ** 2)
    #             for i in range(0, shape[0], 2))

    resid = model - data[0]
    res = np.sqrt( resid ** 2 / data[1] ** 2 )
    return res


def fitfunc_3d(params, q, data=None):
    """
    Do 3D Gaussian fit of data.

    params:
      norm - "global" normalization factor
      lam - lambda parameter
      r_out - radius of the out parameter
      r_side - radius of the side parameter
      r_long - radius of the long parameter

    q: 3xN matrix of each point  values in out-side-long
    data: {optional} observed data to which we will calculate the residual

    .. math::

        CF(\\vec{q}) = NORM(1 + λ exp( -((qo * [Ro])^2 + (qs * [Rs])^2 + (ql * [Rl])^2) ))

    """

    # extract parameters
    norm = params['norm'].value
    lam = params['lam'].value
    r_out = params['r_out'].value
    r_long = params['r_long'].value
    r_side = params['r_side'].value

    # create array of radii (1x3)
    rr = np.array([r_out, r_side, r_long]) / HBAR_C

    # create the exponent parameter by multiplying each radius by the
    # appropriate q component (do shape check to ensure appropriate (1x3 * 3xN)
    # matrix multiplication)
    if np.shape(x)[1] == 3:
        t = (rr * q) ** 2
    else:
        t = (rr * q.T) ** 2

    # Sum along the q * r axis (t is now length N array)
    t = np.sum(t, axis=1)

    # Get the final (theoretical) result
    model = norm * (1 + lam * np.exp(-t))

    # we did not ask to compare to data - just return the model
    if data is None:
        return model

    # split data and error
    observed, err = data[:2]

    # get residual result
    res = np.sqrt((model - observed) ** 2 / err ** 2)

    return res
