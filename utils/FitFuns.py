
import numpy as np
from scipy.special import erf
from scipy.signal import convolve
#Initialize Fit Functions Dictionary
FitFuns={}

def conv(a1,a2,x,mode='full',method='auto'):
    shift=np.argmax(x>0)-1
    y=convolve(a1,a2,mode=mode,method=method)[shift:shift+len(x)]
    return y

def gauss(x,x0,A,FWHM): #normalized to 1 for IRF
    s=FWHM/(2*np.sqrt(2*np.log(2)))
    y=np.exp(-((x)**2)/(2*s**2))
    return A*y/np.sum(y)
FitFuns['gauss']={'fun': gauss,
                  'parms':['x0','A','FWHM'],
                  'p0':[0,1,1],
                  'p-':[-1,0,0],
                  'p+':[1,10,10],
                  'common_parms': ['t0'],
                  }

# def exp_decay(t,t0,A,k):
#     return A*np.exp(-(t-t0)*k)*np.heaviside(t-t0,0)
# FitFuns['exp_decay']={'fun': exp_decay,
#                       'parms':['t0','A','tau'],
#                       'p0':[0,1,1e-10],
#                       'p-':[-1,0,1e-12],
#                       'p+':[1,10,1e12]
#                       }

def exp_decay(t,t0,A,tau):
    k=1/tau
    return A*np.exp(-(t-t0)/tau)*np.heaviside(t-t0,0)
FitFuns['exp_decay']={'fun': exp_decay,
                      'parms':['t0','A','tau'],
                      'p0':[0,1,1e7],
                      'p-':[0,1,1e5],
                      'p+':[0,1,1e9],
                      'common_parms': ['t0'],
                      }

def exp_decay_conv_gauss(t,t0,A,tau,FWHM):
    t=t-t0
    s=FWHM/(2*np.sqrt(2*np.log(2)))
    y1=np.exp(s**2/(2*tau**2))*np.exp(-t/tau)
    y2=erf((t-(s**2/tau))/(s*np.sqrt(2)))
    y=(A/2)*y1*(1+y2) 
    return y
FitFuns['exp_decay_conv_gauss']={'fun': exp_decay_conv_gauss,
                                 'parms':['t0','A','tau','FWHM'],
                                'p0':[0,1,1,1],
                                'p-':[-1,1,0,1],
                                'p+':[1,1,10,10],
                                'common_parms': ['t0'],
                                }

def second_order(t,t0,A,k,c0):
    return A-np.heaviside((t-t0),0)*A/(1+c0*k*(t-t0))-np.heaviside(-(t-t0),0)
FitFuns['second_order']={'fun': second_order,
                         'parms':['t0','A','k','c0'],
                        'p0':[0,1,1,1],
                        'p-':[-1,1,0,1],
                        'p+':[1,1,10,1],
                        'common_parms': ['t0'],
                        }

# def exp_growth(t,t0,A,k):
#     return (A-A*np.exp(-(t-t0)*k))*np.heaviside(t-t0,0)
# FitFuns['exp_growth']={'fun': exp_growth,'parms':[('t0','ps'),('A','arb.u.'),('k','1/ps')]}

# def exp_growth_conv_gauss(t,t0,A1,A2,tau,FWHM):
#     t=t-t0
#     s=FWHM/(2*np.sqrt(2*np.log(2)))
#     y1=np.exp(s**2/(2*tau**2))*np.exp(-t/tau)
#     y2=erf((t-(s**2/tau))/(s*np.sqrt(2)))
#     y=(A2/2)*y1*(1+y2) 
#     return A1-y
# FitFuns['exp_growth_conv_gauss']={'fun': exp_growth_conv_gauss,
#                                   'parms':[('t0','arb.u.'),('A1','arb.u.'),('A2','arb.u.'),('tau','arb.u.'),('FWHM','arb.u.')]}

# def logistic(t,t0,A,k):
#     y=A/(1+np.exp(-k*(t-t0)))
#     return y
# FitFuns['logistic']={'fun': logistic,
#                      'parms':[('t0','ps'),('A','arb.u.'),('k','arb.u.')]}




# x=np.arange(-10,100)
# p1=100
# p2=1
# p3=1
# y=
# plot(x,y)