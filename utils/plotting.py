# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 09:19:56 2026

@author: moritzpalang
"""

from matplotlib.pyplot import get_cmap
from matplotlib import pyplot as plt
import numpy as np


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

def contour(x,
             y,
             Z,
             xrange=None,
             yrange=None,
             zrange=None,
             separate=True,
             title=None,
             xlabel=None,
             ylabel=None,
             cmap_name='fancy',
             ):
    """


    Returns
    -------
    fig,axs

    """
    
    # from warnings import filterwarnings
    # filterwarnings('ignore',"_nolegend_")
    
    if type(x).__module__ != np.__name__:
        x=np.arange(0,Z.shape[1],1)
        
    if type(y).__module__ != np.__name__:
        y=np.arange(0,Z.shape[0],1)
    
    if zrange:
        zrange=[zrange[0],zrange[1]]
        if zrange[0]==None:
            zrange[0]=np.nanmin(Z)-1e-6
        if zrange[1]==None:
            zrange[1]=np.nanmax(Z)-1e-6
    else:
        zrange=[np.nanmin(Z),np.nanmax(Z)]
       
    cmap,levels = make_cmap(name=cmap_name,zrange=zrange)
    
    fig,ax=plt.subplots()
    
    if cmap_name=='fancy':    
        img=ax.contourf(x,y,Z.T,levels=levels,colors=cmap,extend='both') #TODO: positive extend shows wrong color
    else:
        img=ax.contourf(x,y,Z.T,levels=levels,cmap=cmap,extend='both')
    
    ax.set_xlim(xrange)
    ax.set_ylim(yrange)
        
    plt.colorbar(img,anchor=(1,1))
    
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)

    # plt.tick_params(axis='x', direction='in')
    # plt.tick_params(axis='y', direction='in')
    
    ax.set_title(title)
    
    # mpl.rcParams.update(rcParams) 
    
    return fig,ax
        


# =============================================================================
# Timecontour
# =============================================================================


def timecontour(x,y,Z,
              xrange=[None,None],
              yrange=[None,None],
              zrange=[None,None],
              n_levels=40,
              axis_break=1,
              axis = 'vertical',
              title=None,
              zero_contour=False,
              dpi=200):
    
    """
    This function creates a nice contour plot with semi logarithmic axes and an axis break. It is designed for time-resolved spectroscopy data, where the x-axis represents wavelength, the y-axis represents time delay, and the z-axis represents signal intensity.
    """
        
    if xrange[0]==None:
        xrange[0]=np.nanmin(x)-1e-6
    if xrange[1]==None:
        xrange[1]=np.nanmax(x)-1e-6
        
    if yrange[0]==None:
        yrange[0]=np.nanmin(y)-1e-6
    if yrange[1]==None:
        yrange[1]=np.nanmax(y)-1e-6
        
    if zrange[0]==None:
        zrange[0]=np.nanmin(Z)-1e-6
        if not zrange[0]:
            zrange[0]=0
    if zrange[1]==None:
        zrange[1]=np.nanmax(Z)-1e-6
        if not zrange[1]:
            zrange[1]=1
        
    if axis=='vertical':
        if not (yrange[0]<axis_break<yrange[1] and np.argmax(y>axis_break)>=2):
            fig,ax = contour(x,y,Z,              
                              xrange=xrange,
                              yrange=yrange,
                              zrange=zrange,)
            return fig,ax
    elif axis=='horizontal':
        if not (xrange[0]<axis_break<xrange[1] and np.argmax(x>axis_break)>=2):
            fig,ax = contour(x,y,Z,              
                              xrange=xrange,
                              yrange=yrange,
                              zrange=zrange,)
            return fig,ax
            
        
    cmap,levels = make_cmap(n_levels=n_levels,zrange=zrange)

    ##############
    ####Contour

    if axis=='horizontal': 
        ix1 = np.argmax(x>xrange[0])
        ix2 = np.argmax(x>axis_break)
        ix3 = np.argmax(x>xrange[1])
        
        fig,ax=plt.subplots(1,2,gridspec_kw={'width_ratios':[1,2],'wspace':0.012},dpi=dpi)
 
        ax[0].contourf(x[ix1:ix2],y,Z[ix1:ix2,:].T,
                          levels=levels,colors=cmap,extend='both',
                          vmin=zrange[0],vmax=zrange[1],
                         )
    
        img=ax[1].contourf(x[ix2:ix3],y,Z[ix2:ix3,:].T,
                          levels=levels,colors=cmap,extend='both',
                          vmin=zrange[0],vmax=zrange[1],
                         )

        if zero_contour:
            ax[0].contour(x[ix1:ix2],y,Z[ix1:ix2,:].T,
                                     levels=[0], colors='black', linestyles=':',linewidths=1)
            ax[1].contour(x[ix2:ix3],y,Z[ix2:ix3,:].T, 
                                    levels=[0], colors='black', linestyles=':',linewidths=1)

        # ax[1].set_xscale('log')
        # ax[1].set_yticks([])
  
        # ax[1].text(0.1, -0.15, 'wl/nm', va='center',transform=ax[1].transAxes)
        # fig.colorbar(img,ax=ax[1])
        # ax[0].set_ylabel('$\Delta$t/ps')
        # ax[0].set_title=title
        
        ax[0].set_xlim((xrange[0],axis_break))
        ax[0].set_ylim(yrange)
        ax[1].set_xlim((axis_break,xrange[1]))
        ax[1].set_ylim(yrange)
        
    elif axis=='vertical': 
        
        fig,ax=plt.subplots(2,1,gridspec_kw={'height_ratios':[2,1],'hspace':0.02},dpi=dpi)
   
        iy1 = np.argmax(y>yrange[0])
        iy2 = np.argmax(y>axis_break)
        iy3 = np.argmax(y>yrange[1])

        ax[1].contourf(x,y[iy1:iy2],Z[:,iy1:iy2].T,
                       levels=levels,colors=cmap,extend='both',
                       vmin=zrange[0],vmax=zrange[1],
                      )

        img=ax[0].contourf(x,y[iy2:iy3],Z[:,iy2:iy3].T,
                           levels=levels,colors=cmap,extend='both',
                           vmin=zrange[0],vmax=zrange[1],
                          )

        
        if zero_contour:
            ax[1].contour(x, y[iy1:iy2], Z[:,iy1:iy2], 
                                     levels=[0], colors='black', linestyles=':',linewidths=1)
            ax[0].contour(x, y[iy2:iy3], Z[:,iy2:iy3], 
                                    levels=[0], colors='black', linestyles=':',linewidths=1)
        
        fig.colorbar(img,ax=ax)
        ax[0].set_yscale('log')
        ax[0].set_xticks([])
         
        
        # ax[0].text(-0.2, 0.2, '$\Delta$t', va='center',transform=ax[0].transAxes,rotation='vertical')
        # ax[1].set_xlabel('wl/nm')

        
        # ax[0].set_title(title)
    
        ax[1].set_xlim(xrange)
        ax[1].set_ylim((yrange[0],axis_break))
        ax[0].set_xlim(xrange)
        ax[0].set_ylim((axis_break,yrange[1]))
    
    
    return fig, ax