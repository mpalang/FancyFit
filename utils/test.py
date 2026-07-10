# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 19:12:09 2026

@author: morit
"""
from pathlib import Path
import sys
if str(Path(__file__).parent.parent) not in sys.path:
   sys.path.append(str(Path(__file__).parent.parent)) 
from utils.auxiliary import FitFunctions
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import convolve
from fittoolkit import GlobalFit
from numpy.linalg import inv
from iminuit import Minuit as Mi

ff = FitFunctions()
ff.default()



base = Path(__file__).parent.parent/'Test Data'
t = np.genfromtxt(Path(base)/'x.txt')
wl = np.genfromtxt(Path(base)/'y.txt')
s = np.genfromtxt(Path(base)/'z.txt')


#%%


# x = np.linspace(-100,100,2000)
# y = settings['funs'][0](x,*pfit)


# fig,ax = plt.subplots()
# ax.plot(x,y)



#%%

# funobj = ff.funs['exp_decay']
# settings={
#         'funs': [funobj.func],
#         'parms': [funobj.parm_names],
#         'p0': [[-1,1,1]],
#         'p_lower': [[-1,1,0]],
#         'p_upper': [[-1,1,np.inf]],
#         'common_parms': funobj.common_parms,
#          }

# gf = GlobalFit(t,wl,s,settings=settings) 
# pfit = gf.p[0]