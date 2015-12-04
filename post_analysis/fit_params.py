
from collections import namedtuple

FitParam = namedtuple("fitparam", ('name', 'ival', 'min', 'max'))

fit_params = [
    FitParam(name='radius', ival=4, min=0, max=None),
    FitParam(name='f0_re', ival=1, min=0, max=None),
    FitParam(name='f0_im', ival=.1, min=0, max=None),
]

# FitParams = namedtuple("fitparam", ('radius', 'f0_re', 'f0_im', 'D0', 'norm'))
