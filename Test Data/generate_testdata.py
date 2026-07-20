# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 10:28:16 2026

@author: morit
"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.special import erf
from scipy.signal import convolve

def gauss(x,x0,A,FWHM): #normalized to 1 for IRF
    s=FWHM/(2*np.sqrt(2*np.log(2)))
    y=(1/(np.sqrt(2*np.pi)*s))*np.exp(-((x-x0)**2)/(2*s**2))
    return A*y

def conv(a1,a2,x,mode='full',method='auto'):
    shift=np.argmax(x>0)-1
    y=convolve(a1,a2,mode=mode,method=method)[shift:shift+len(x)]
    return y

def exp_decay(t,t0,A,tau):
    k=1/tau
    return A*np.exp(-(t-t0)/tau)*np.heaviside(t-t0,0)

def exp_decay_conv_gauss(t,t0,A,tau,FWHM):
    t=t-t0
    s=FWHM/(2*np.sqrt(2*np.log(2)))
    y1=np.exp(s**2/(2*tau**2))*np.exp(-t/tau)
    y2=erf((t-(s**2/tau))/(s*np.sqrt(2)))
    y=(A/2)*y1*(1+y2) 
    return y



x = np.linspace(-10,300,300)
y = np.linspace(300,800,100)

DADS1 = gauss(y,320,-0.3,80)+gauss(y,600,0.4,300)+gauss(y,450,0.3,80)
DADS2 = gauss(y,320,-0.2,80)+gauss(y,400,0.5,230)+gauss(y,700,0.5,200)
DADS3 = gauss(y,320,-0.5,80)+gauss(y,650,0.3,400)+gauss(y,520,0.03,100)

D1 = exp_decay(x,-5,1,1200)
D2 = exp_decay(x,-5,2,14)
D3 = exp_decay(x,-5,0.5,3000)

DADS = np.column_stack((DADS1,DADS2,DADS3))
# DADS = DADS+np.random.uniform(-0.001,0.001,DADS.shape)
D = np.column_stack((D1,D2,D3))
D = D+np.random.uniform(-0.01,0.01,D.shape)

Z = DADS@D.T

#%

fig,ax = plt.subplots()
ax.axhline(0,color='k',linewidth=1)
ax.plot(y,DADS[:,0])
ax.plot(y,DADS[:,1])
ax.plot(y,DADS[:,2])

levels = np.linspace(-0.006,0.004,20)
fig,ax = plt.subplots()
ax.contourf(y,x,Z.T,levels=levels)

np.savetxt('signal.txt',Z)
np.savetxt('t.txt',x)
np.savetxt('wl.txt',y)

