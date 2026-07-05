# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 09:19:56 2026

@author: moritzpalang
"""

from matplotlib.pyplot import get_cmap
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QSizePolicy
from matplotlib.figure import Figure

import numpy as np

from utils.logger import add_logger
logger = add_logger(__name__)


def make_cmap(name='fancy',n_levels=40,zrange=(-1,1)):
    
    if zrange[0]>zrange[1]:
        zrange = (zrange[1],zrange[0])
        print('Make sure first zrange value is lower than second. Numbers were swapped.')
    
    if not any(zrange) or np.isnan(zrange).any():
        zrange=(-1,1)
    
    if name=='fancy':
        levels = np.linspace(zrange[0],zrange[1],n_levels)
        if zrange[0]<0 and zrange[1]>0:
            zero=np.argmax(levels>0)
            cmap_neg=[get_cmap('Blues')(n/zero) for n in range(zero)]
            cmap_pos=[get_cmap('Reds')(n/(n_levels-zero)) for n in range(n_levels-zero)]
            cmap=cmap_neg[::-1]+ cmap_pos
            if not levels[zero-1] == 0:
                levels = np.insert(levels,zero,0)
                cmap.insert(zero,(1,1,1))
            
        elif zrange[0]<0:
            cmap=[get_cmap('Blues')(n/n_levels) for n in range(n_levels)]
        elif zrange[0]>0:
            cmap=[get_cmap('Reds')(n/n_levels) for n in range(n_levels)]
        
    else:
        levels=n_levels
        levels = np.linspace(zrange[0],zrange[1],levels+1)
        cmap=name
        
    return cmap,levels


# ---------------------------
# PLOT WIDGET WRAPPER
# ---------------------------

class BaseCanvas(FigureCanvasQTAgg):

    def __init__(self, figsize = (6,4), dpi=80):
        self.fig = Figure(figsize=figsize,
                          dpi=dpi)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding,
                            QSizePolicy.Expanding
                            )

        self.axes = {'main': self.fig.add_subplot(111)}
        self._layout = None

    def clear(self):
        self.fig.clear()
        self.axes = {}
        self.draw_idle()
        
        
class LineCanvas(BaseCanvas):

    def __init__(self, layout='single',figsize=None, dpi=100):
        super().__init__(figsize=figsize,dpi=dpi)

        self.lines = {}
        self.set_layout(layout)

    def set_layout(self,layout):
        if layout=='single':
            self._layout = 'single'
            self.clear()
            self.axes["main"] = self.fig.add_subplot(111)
            self.axes['main'].axhline(0,color='k',linewidth=self.axes['main'].spines['left'].get_linewidth())
            self.draw_idle()
        elif layout=='split':
            self._layout = 'split'
            self.clear()
            gs = self.fig.add_gridspec(
                1, 2,
                width_ratios=(2,1),
                wspace=0.1)
            self.axes["main"] = self.fig.add_subplot(gs[0, 0])
            self.axes['main'].axhline(0,color='k',linewidth=self.axes['main'].spines['left'].get_linewidth())
            self.axes["log"] = self.fig.add_subplot(gs[0, 1])
            self.axes['log'].axhline(0,color='k',linewidth=self.axes['log'].spines['left'].get_linewidth())
            self.draw_idle()

    def set_line(self,name, x, y,**kwargs):
        if name not in self.lines:
            if self._layout=='single':
                self.lines[name], = self.axes['main'].plot(x, y,**kwargs)
            
            else:
                pass        
        
        else:
            if self._layout=='single':
                self.lines[name].set_data(x,y)
                 
    
    def clear_lines(self,name=None):
        for line in self.lines.values():
            line.remove()   # removes from axes
        self.lines.clear()
        self.draw_idle()     
        
        
    def set_labels(self,xlabel,ylabel):
        self.axes['main'].set_xlabel=xlabel
        self.axes['main'].set_ylabel=ylabel

class ContourCanvas(BaseCanvas):
    def __init__(self, layout='single',figsize=None, dpi=80):
        super().__init__(figsize=figsize,dpi=dpi)
        self.fig.subplots_adjust(
                                left=0.02,
                                right=0.98,
                                bottom=0.02,
                                top=0.98,
                                wspace=0.01,
                                hspace=0.01
                            )
        self.contours = {}
        self.set_layout(layout=layout)

    def set_layout(self,layout='single'):
        if layout=='single':
            self._layout = 'single'
            self.clear()
            self.axes["main"] = self.fig.add_subplot(111)

        elif layout=='split':
            self._layout = 'split'
            self.clear()

            gs = self.fig.add_gridspec(2, 1, height_ratios=(2, 1),
                                       hspace=0.01
                                       )

            self.axes["log"] = self.fig.add_subplot(gs[0, 0])
            self.axes["main"] = self.fig.add_subplot(gs[1, 0])
            
            self.axes["log"].set_yscale('log')
            self.axes["log"].set_xticks([])

    def set_contour(self, x, y, Z, zrange=(-1,1), axis_break=2, **kwargs):
        cmap,levels = make_cmap(zrange=zrange)
        if self._layout == 'single':
            if 'fill' in self.contours:
                for c in self.contours['fill'].collections:
                    c.remove()
                    
            if 'zero_line' in self.contours:
                for c in self.contours['zero_line'].collections:
                    c.remove()
                
            self.contours['fill'] = self.axes['main'].contourf(x, y, Z, 
                                                           colors=cmap,levels=levels,
                                                           extend='both')
            
        elif self._layout == 'split':
            iy0 = np.argmax(y>axis_break)
            
            if 'fill' in self.contours:
                self.contours['fill'].remove()
                
            if 'fill_log' in self.contours:
                self.contours['fill_log'].remove()

            self.contours['fill'] = self.axes['main'].contourf(x, y[:iy0], Z[:iy0,:], 
                                                colors=cmap,levels=levels, 
                                                extend='both')
            
            self.contours['fill_log'] = self.axes['log'].contourf(x, y[iy0:], Z[iy0:,:], 
                                                colors=cmap,levels=levels, 
                                                extend='both')
            