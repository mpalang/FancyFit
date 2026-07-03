# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 19:12:09 2026

@author: morit
"""

from auxiliary import FitFunctions
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import convolve

ff = FitFunctions()
ff.default()


def conv(y, yc):
    yc = np.asarray(yc, dtype=float)
    yc = yc / np.sum(yc)

    y_conv = np.convolve(y, yc, mode="full")

    # center kernel
    k = len(yc) // 2

    return y_conv[k:k + len(y)]

x = np.linspace(-100,100,2000)
y = ff.funs['exp_decay'].func(x,0,1,20)
y2 = ff.funs['gauss'].func(x,0,1,1)
y3 = ff.funs['dgauss'].func(x,0,1,1)
y4 = ff.funs['d2gauss'].func(x,0,1,1)
y6 = conv(y,y2)



fig,ax = plt.subplots()
# ax.plot(x,y)
ax.plot(x,y3)
ax.plot(x,y6)

