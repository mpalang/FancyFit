# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 17:30:23 2026

@author: morit
"""

import sys
from pathlib import Path

if str(Path(__file__).parent.parent) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent))
    
from utils.error_handling import error_handler


# =============================================================================
# Convolute Functions with irf
# =============================================================================
@error_handler
def convolute_functions(self,FunObjs,IRF):
    """f: functions, p: parm names, p0: initial guesses, pl: lower boundaries, p: upper boundaries, cp: common parameters"""
    funs = [fun_obj.func for fun_obj in FunObjs]
    parms =[fun_obj.parm_names for fun_obj in FunObjs]
    p0 = [fun_obj.p0 for fun_obj in FunObjs]
    pl = [fun_obj.p_lower for fun_obj in FunObjs]
    pu = [fun_obj.p_upper for fun_obj in FunObjs]
    cp = [fun_obj.common_parms for fun_obj in FunObjs]
    
    for n,fobj in enumerate(FunObjs):
        fun_parms = fobj.parm_names
        cp = self.common_parms_input.text().replace(' ','').split(',')
        for parm in fobj.parm_names:
            if parm in cp:
                if parm in fun_parms:
                    continue
                fun_parms.append(parm)
            else:
                pass
                    
        def new_fun(x,fun_kwargs,irf_kwargs):
            y_fun = fobj.func(x,*parms)
            y_irf = IRF.func(x,*IRF.parm_names)
            return self.FitFuns.conv(y_fun,y_irf)

        # common_parms = list(dict.fromkeys(common_parms + IRF.parms)) # add irf parameters to common parameters, while preserving order and removing duplicates.
    