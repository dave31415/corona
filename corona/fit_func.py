import numpy as np
from scipy import stats


def fit_func(x, y):
    xx = np.array(x)
    yy = np.array(y)
    y_log = np.log2(yy)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xx, y_log)
    doubling_time = 1.0 / slope
    amplitude = 2.0 ** intercept
    y_fit = amplitude * 2**(xx/doubling_time)
    return y_fit, doubling_time, amplitude
