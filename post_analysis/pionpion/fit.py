#
# post_analysis/fit.py
#

import numpy as np


HBAR_C = 0.1973269788 # GeV·fm


def fitfunc_qinv_gauss(params, q, data=None):
    """
    fitfunc_qinv_gauss
    ~~~~~~~~~~~~
    1D Gaussian fit

    params:
        radius - The qinv radius (units: fm)
        lam - The lambda parameter (unitless)
    q: An numpy array of q_inv values (units: GeV)
    data: {optional} observed data with which we will calculate the residual

    .. math::

        CF(q_{inv}) = λ exp( -(q_{inv} * R)^2 )

    """

    t = -(q * params['radius'] / HBAR_C) ** 2
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


def fitfunc_qinv_lorentz(params, q, data=None):
    """
    fitfunc_qinv_lorentz
    ~~~~~~~~~~~~
    1D Lorentzian fit

    .. math::

        CF(q_{inv}) = 1 + λ \\frac{R^2}{R^2 + q_{inv}^2}


    params:
        radius - ??
        lam - The lambda scaling parameter

    q: An array of q_inv data (units: GeV)
    data: {optional} observed data with which we will calculate the residual
    """
    r_squared = params['radius'].value ** 2
    lam = params['lam']

    model = 1 + lam * r_squared / (r_squared + q ** 2)

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


def fitfunc_qinv_gauss_ll(params, q, data=None):
    """
    Calculate the gaussian fit returning log-likelyhood χ² calculation.

    """
    C = fitfunc_qinv_gauss(params, q)
    if data is None:
        return C
    A, B = data
    ApB_Cp1 = (A + B) / (C + 1)
    res = -2 * ( A * np.log(C / A * ApB_Cp1) + B * np.log(ApB_Cp1 / B) )
    # print(res)
    # print(1.0/res)
    # input()
    return res

fitfunc_qinv = fitfunc_qinv_gauss
# fitfunc_qinv = fitfunc_qinv_gauss_ll
# fitfunc_qinv = fitfunc_qinv_lorentz


def fitfunc_3d(params, q, data=None):
    """
    Do 3D Gaussian fit of data.

    .. math::

        CF(\\vec{q}) = NORM(1 + λ exp( -((qo * [Ro])^2 + (qs * [Rs])^2 + (ql * [Rl])^2) ))

    params:
      norm - "global" normalization factor (unitless)
      lam - lambda parameter (unitless)
      r_out - radius of the out parameter (units: fm)
      r_side - radius of the side parameter (units: fm)
      r_long - radius of the long parameter (units: fm)

    q: 3xN matrix of each point in out-side-long space (units: GeV)
    data: {optional} observed data to which we will calculate the residual
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
    if np.shape(q)[1] == 3:
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



def fitfunc_3d_with_offdiagonal_terms(params, q, data=None):
    """
    Do 3D Gaussian fit of data, including R_{os}, R_{ol}, R_{sl} terms in fit.

    .. math::

        CF(\\vec{q}) = NORM(1 + λ exp( -((qo * [Ro])^2 + (qs * [Rs])^2 + (ql * [Rl])^2
            + 2 * qo * qs * [Ros]^2 + 2 * qo * ql * [Rol]^2+ 2 * qs * ql * [Rsl]^2)
        ))

    params:
      norm - "global" normalization factor (unitless)
      lam - lambda parameter (unitless)
      r_out - radius of the out parameter (units: fm)
      r_side - radius of the side parameter (units: fm)
      r_long - radius of the long parameter (units: fm)

      r_os - radius of the out parameter (units: fm)
      r_ol - radius of the side parameter (units: fm)
      r_sl - radius of the long parameter (units: fm)

    q: 3xN matrix of each point in out-side-long space (units: GeV)
    data: {optional} observed data to which we will calculate the residual
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
    if np.shape(q)[1] == 3:
        t = (rr * q) ** 2
    else:
        t = (rr * q.T) ** 2

    # Sum along the q * r axis (t is now length N array)
    t = np.sum(t, axis=1)
    t += (2 * q[0] * q[1] * params['r_os'].value ** 2
        + 2 * q[0] * q[2] * params['r_ol'].value ** 2
        + 2 * q[1] * q[2] * params['r_sl'].value ** 2)

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
