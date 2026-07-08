# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 23:58:36 2026

@author: morit
"""
from PySide6.QtCore import QStandardPaths
import json
from dataclasses import dataclass
from pathlib import Path

import sympy as sp
import numpy as np
from copy import deepcopy

# Add personal modules:
from utils.logger import add_logger  
logger = add_logger(__name__)

@dataclass
class data_class:
    TestData: bool =False
    Empty: bool = False
    scaling_factors: tuple = (1,1,1)
    x: np.ndarray | None = None
    y: np.ndarray | None = None
    z: np.ndarray | None = None
    
    def __post_init__(self):
        settings = fancyfitSettings()
        
        if self.TestData:
            try:
                self.z_full = np.genfromtxt(settings.z_testdata_path).T
                self.y_full = np.sort(np.genfromtxt(settings.y_testdata_path),delimiter=',')
                self.x_full = np.sort(np.genfromtxt(settings.x_testdata_path),delimiter=',')
            except:
                raise ValueError('could not load testdata. specify path in settings.json')
                
        elif self.Empty or self.z is None:
            self.z_full = np.full((2,2),np.nan)
            self.y_full = np.linspace(0,1,2)
            self.x_full = np.linspace(0,1,2)
            
        else:
            self.x_full = deepcopy(self.x)
            self.y_full = deepcopy(self.y)
            self.z_full = deepcopy(self.z)
        
        self.x = self.x_full*self.scaling_factors[0]
        self.y = self.y_full*self.scaling_factors[1]
        self.z = self.z_full*self.scaling_factors[2]
        self.check_data()
        self.x_fit = deepcopy(self.x)
        self.y_fit = deepcopy(self.y)
        self.z_fit = np.full(self.z.shape,np.nan)
        self.residuum = np.full(self.z.shape,np.nan)
        self.DADS = None
    
    def check_data(self):
        if self.z.shape == (np.squeeze(self.x.shape),np.squeeze(self.y.shape)):
            pass
        elif self.z.shape == (np.squeeze(self.y.shape),np.squeeze(self.x.shape)):
            self.z = self.z.T
            self.z_full = self.z_full.T
        else:
            raise ValueError(f'Loading Data failed: Z-shape ({self.z.shape}) should be (x-shape,y-shape) (({self.x.shape},{self.y.shape}))')
            return False
        
    def cut_data(self,x_low=None,x_high=None,y_low=None,y_high=None):    
        ixlow = np.argmax(self.x_full>float(x_low))
        ixhigh = np.argmax(self.x_full>float(x_high))
        iylow = np.argmax(self.y_full>float(y_low))
        iyhigh = np.argmax(self.y_full>float(y_high))
        if ixhigh == 0:
            ixhigh = len(self.x_full)
        if iyhigh == 0:
            iyhigh = len(self.y_full)
        self.x = self.x_full[ixlow:ixhigh]*self.scaling_factors[0]
        self.y = self.y_full[iylow:iyhigh]*self.scaling_factors[1]
        self.z = self.z_full[ixlow:ixhigh,iylow:iyhigh]*self.scaling_factors[2]
            
        return self


@dataclass
class fancyfitSettings:
    def __init__(self):
        
        self.user_dir = Path(QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation))
        self.settings_file = self.user_dir / 'settings.json'

        self.load()

    def to_dict(self):
        return {k:v for k,v in self.__dict__.items() if k not in ['user_dir','settings_file']}
    
    def load(self):
        try: 
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.__dict__.update(data)
            else:
                self.default()
                self.save()
                logger.info(f"User settings file created:\n {str(self.settings_file)}")
        except Exception as e:
            self.default()
            logger.exception('Failed to load user settings.')
            logger.info(f'Failed to load user settings. Using defaults instead.\n {e}')
    
    def save(self):
        self.user_dir.mkdir(parents=True, exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(self.to_dict(),f,indent=4)

    def default(self):
        self.scaling_factor_z = 1000
        self.scaling_factor_x = 1
        self.scaling_factor_y = 1
        self.fit_iterations = 3
        self.z_3Dstretch = 2.5
        self.axes_break = 'auto'
        self.x_label = 'dt'
        self.y_label = 'wl'
        self.z_label = 'signal'
        self.x_unit = 'ps'
        self.y_unit = 'nm'
        self.z_unit = '\u0394mOD'
        self.x_name = 'Kinetics'
        self.y_name = 'Spectra'
        self.fit_mode = 'global'
        self.fit_method = 'iminuit'
        self.use_irf = True
        self.default_funs = ['exp_decay','exp_decay']
        self.use_testdata = False
        self.z_data_path = str(Path(Path(__file__).parent.parent,'Test Data','Z.txt'))
        self.y_data_path = str(Path(Path(__file__).parent.parent,'Test Data','wl.txt'))
        self.x_data_path = str(Path(Path(__file__).parent.parent,'Test Data','t.txt'))
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class fitFunction:
    name: str
    expr: str
    parm_names: list[str]
    p0: list[float]
    p_lower: list[float]
    p_upper: list[float]
    common_parms: list[str]
    
    def __post_init__(self):
        parms = ['x']
        for parm in self.parm_names:
            parms.append(sp.symbols(parm))
        expr = sp.sympify(self.expr)
        self.func = sp.lambdify(parms,expr,'numpy')
    
    def to_dict(self):
        out_dict={}
        for key,value in self.__dict__.items():
            if key not in ['func']:
                out_dict[key]=value
        return out_dict
    
    def copy(self,parm_names,p0,p_lower,p_upper):
        """creates a copy of this fitFunction Object with different parameter settings"""
        copy_func = deepcopy(self)
        copy_func.parm_names=parm_names
        copy_func.p0=p0
        copy_func.p_lower=p_lower
        copy_func.p_upper=p_upper
        
        return copy_func
                
class FitFunctions:
    def __init__(self):
        self.user_dir = Path(QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation))
        self.functions_file = self.user_dir / 'FitFunctions.json'
        self.funs={}
        
        def conv(y, yc):
            yc = np.asarray(yc, dtype=float)
            yc = yc / np.sum(yc) #normalize convolution function
            y_conv = np.convolve(y, yc, mode="full")
            # center kernel
            k = len(yc) // 2
            return y_conv[k:k + len(y)]
        self.conv = conv
        
        self.load()
#             
    def from_dict(self,funs):
        for name,value in funs.items():
            self.funs[name] = fitFunction(name,value['expr'],value['parm_names'],
                              value['p0'],value['p_lower'],value['p_upper'],
                              value['common_parms'])
            # self.__dict__.setdefault(name,self.funs[name]) #I think I want to change the architecture here. See if that makes sense with how functions are called. Just make sure all old references in the code are replaced before removing the old .funs['funname'] structure
                
    def names(self):
        return list(self.funs.keys())
    
    def new_function(self,fitFunction_obj):
        self.funs[fitFunction_obj.name] = fitFunction_obj
    
    def load(self):
        try: 
            if self.functions_file.exists():
                pass
                with open(self.functions_file, 'r') as f:
                    user_funcs = json.load(f)
                    self.from_dict(user_funcs)
            else:
                self.default()
                self.save()
                logger.info(f"User functions file created:\n {self.functions_file}")
        except Exception as e:
            self.default()
            logger.exception('Failed to load user user functions.')
            logger.info(f'Failed to load user user functions. Using defaults instead.\n {e}')
    
    def save(self):
        self.user_dir.mkdir(parents=True, exist_ok=True)
        out_dict={}
        for key,value in self.funs.items():
            out_dict[key] = value.to_dict()
            
        with open(self.functions_file, 'w') as f:
            json.dump(out_dict,f,indent=4)
    

    def default(self):
        
        gauss = "A/(s*sqrt(2*pi))*exp(-(x-x0)**2/(2*s**2))"
        self.funs['gauss'] = fitFunction('gauss',gauss,['x0','A','s'],
                                      [0,1,1],[-1,0,0],[1,10,10],
                                      ['x0'])
        
        dgauss = "-A*(x-x0)/(s**3*sqrt(2*pi))*exp(-(x-x0)**2/(2*s**2))"
        self.funs['dgauss'] = fitFunction('dgauss',dgauss,['x0','A','s'],
                                      [0,1,1],[-1,0,0],[1,10,10],
                                      ['x0'])
        
        d2gauss = "A*((x-x0)**2/s**4 - 1/s**2)/(s*sqrt(2*pi))*exp(-(x-x0)**2/(2*s**2))"
        self.funs['d2gauss'] = fitFunction('d2gauss',d2gauss,['x0','A','s'],
                                      [0,1,1],[-1,0,0],[1,10,10],
                                      ['x0'])

        exp_decay = "A*exp(-(x-x0)/tau)*heaviside(x-x0,0)"
        self.funs['exp_decay'] = fitFunction('exp_decay',exp_decay,['x0','A','tau'],
                                      [0,1,1e7],[-1,1,1e5],[1,1,1e9],
                                      ['x0'])
        
        second_order = "heaviside((x-x0),0)*A/(1+c0*k*(x-x0))"
        self.funs['second_order'] = fitFunction('second_order',second_order,['x0','A','k','c0'],
                                      [0,1,1e-6,1],[-1,1,1e-8,1],[1,1,1e-5,1],
                                      ['x0'])
        
        # exp_decay_conv_gauss = """((A/2)*
        #                         exp((FWHM/(2*sqrt(2*log(2))))**2/
        #                         (2*tau**2))*exp(-x/tau)*
        #                         (1+erf((t-((FWHM/(2*sqrt(2*log(2))))**2/tau))/
        #                         ((FWHM/(2*sqrt(2*log(2))))*sqrt(2)))))"""
        # setattr(self,'exp_decay_conv_gauss',Function(exp_decay_conv_gauss,['t0','FWHM','A','tau'],
        #                               [0,1,0.004,1e7],[-1e5,1e-8,1e-6,1e5],[1e5,1e5,1,1e9],
        #                               ['t0','FWHM']))

