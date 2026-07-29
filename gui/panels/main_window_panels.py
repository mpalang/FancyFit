# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:05:55 2026

@author: moritzpalang

This contains all widgets used in the Main Window.
"""
import numpy as np

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QTabWidget,
    QSizePolicy,
    QMessageBox,
    QPlainTextEdit,
)

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from gui.Elements import Button,Inputbox,Label,Dropdown,Slider,ParmRow
from utils.plotting import LineCanvas, ContourCanvas
from utils.auxiliary import FitFunctions
from utils.error_handling import ErrorBox

# =============================================================================
# Data Tweak Panel
# =============================================================================
class DataTweakPanel(QWidget):
    
    """
    This Panel handles user input to treat data and then triggers actions if inputs are valid.
    """
    
    cut_requested = Signal()
    uncut_requested = Signal()
    
    def __init__(self,defaults:dict=None):
        super().__init__()
        # Data Tweak
        
        # self.setSizePolicy(
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding
        #             )
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.main_layout = QGridLayout(frame)
        
        self.create_ui()
        self.create_connections()
        
        central = QVBoxLayout()
        self.setLayout(central)
        central.addWidget(frame)
        
        if defaults:
            self.set_defaults()
    
    def create_ui(self):
        
        layout = self.main_layout
        
        Label(layout,"Set Ranges",(0,0))
        self.cut_button = Button(layout,'cut data',(0,1))
        self.uncut_button = Button(layout,'full data', (0, 2))
        self.x_label = Label(layout,'x', (1, 0))
        self.x_low = Inputbox(layout, '', (1, 1))
        self.x_high = Inputbox(layout, '', (1,2))
        self.y_label = Label(layout,'y', (2,0))
        self.y_low = Inputbox(layout, '', (2,1))
        self.y_high = Inputbox(layout, '', (2,2))
        
        self.old_style = self.y_high.styleSheet() # store old style so it can be reset after validate
        
        
    def create_connections(self):
        self.x_low.textChanged.connect(self.validate)
        self.x_high.textChanged.connect(self.validate)
        self.y_low.textChanged.connect(self.validate)
        self.y_high.textChanged.connect(self.validate)
        
        self.cut_button.clicked.connect(self._cut_requested)
        self.uncut_button.clicked.connect(self.uncut_requested)
    
    
    def set_bg_color(self,color):
        self.x_low.setStyleSheet(f"background-color: {color};")
        self.x_high.setStyleSheet(f"background-color: {color};")
        self.y_low.setStyleSheet(f"background-color: {color};")
        self.y_high.setStyleSheet(f"background-color: {color};")
        
        
    def reset_style(self):
        self.x_low.setStyleSheet(self.old_style)
        self.x_high.setStyleSheet(self.old_style)
        self.y_low.setStyleSheet(self.old_style)
        self.y_high.setStyleSheet(self.old_style)
        
        
    def validate(self):
        try:
            x_low = float(self.x_low.text())
            x_high = float(self.x_high.text())
            y_low = float(self.y_low.text())
            y_high = float(self.y_high.text())
        except:
            self.set_bg_color('rgba(255, 150, 150, 120)')
            return False
        
        if x_low < x_high and y_low < y_high:
            self.reset_style()
            return True
        else:
            self.set_bg_color('rgba(255, 150, 150, 120)')
            return False
            
        
    def _cut_requested(self):
        if self.validate():
            self.cut_requested.emit()
        else:
            ErrorBox('Value Error','Input values have to be floats. Left needs to be lower.')
    
    
    def set_labels(self,x_label,y_label):
        self.x_label.setText(x_label)
        self.y_label.setText(y_label)
    
    
    def set_limits(self,x_limits,y_limits):
        self.x_low.setText(f'{x_limits[0]:.4g}')
        self.x_high.setText(f'{x_limits[1]:.4g}')
        self.y_low.setText(f'{y_limits[0]:.4g}')
        self.y_high.setText(f'{y_limits[1]:.4g}')
        
        
    @property
    def x_limits(self):
        return (float(self.x_low.text()),float(self.x_high.text()))
    
    @property
    def y_limits(self):
        return (float(self.y_low.text()),float(self.y_high.text()))
        

# =============================================================================
# Fit Settings
# =============================================================================
class FitSettingsPanel(QWidget):
    
    """
    This Panel handles fit settings user input.
    """
    
    mode_changed= Signal()
    method_changed= Signal()
    
    def __init__(self,defaults:dict=None):
        super().__init__()
        
        # self.setSizePolicy(
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding
        #             )
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.main_layout = QGridLayout(frame)
        
        self.create_ui()
        self.create_connections()
        
        central = QVBoxLayout()
        self.setLayout(central)
        central.addWidget(frame)
        
        if defaults:
            self.set_defaults(defaults)
    
    
    def create_ui(self):
        layout = self.main_layout
        
        Label(layout,'Mode', (0,0))
        self.mode_input = Dropdown(layout,['Global','Simple'], (0,1))
        Label(layout, 'Method', (1,0))
        method_options = ['migrad','L-BFGS-B','TNC','COBYLA','SLSQP','trust-constr','CG','Powell','BFGS',]
        self.method_input = Dropdown(layout, method_options, (1,1))


    def create_connections(self):
        self.mode_input.currentTextChanged.connect(self.mode_changed)
        self.method_input.currentTextChanged.connect(self.method_changed)
        
        
    def set_defaults(self,defaults):
        for key,value in defaults.items():
            getattr(self,f'{key}_input').setCurrentText(value)
            
    
    @property
    def method(self):
        return self.method_input.currentText()
            
  



# =============================================================================
  
# =============================================================================
class ParmsPanel(QWidget):
    """
    Parms Panel Widget allowing user input for fit functions and their parameters. Used in FunctionsInputPanel 
    """
    def __init__(self,FitFuns,fun_name:str|None=None):
        super().__init__()
        self.FitFuns = FitFuns

        self.layout = QGridLayout()
        
        self.fun_input = Dropdown(self.layout,
                                    FitFuns.names(),
                                    standard=fun_name,
                                    command=lambda:self.on_function_change(),
                                    grid=(0,0,1,4)
                                    )
        Label(self.layout,'name',layout_args=(1,0))
        Label(self.layout,'p0',layout_args=(1,1))
        Label(self.layout,'p-',layout_args=(1,2))
        Label(self.layout,'p+',layout_args=(1,3))
    
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line, 2, 0, 1, 4)
        
        self.build_parms_input()
        
        self.setLayout(self.layout)
    
    
    def build_parms_input(self):
        self.Parms=QWidget()
        Parms_layout=QVBoxLayout()
        # Parms_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        fun_name = self.fun_input.currentText()
        
        self.parm_rows=[]
        for n, parm in enumerate(self.FitFuns.funs[fun_name].parm_names):
            parm_row = ParmRow(parm,
                          self.FitFuns.funs[fun_name].p0[n],
                          self.FitFuns.funs[fun_name].p_lower[n],
                          self.FitFuns.funs[fun_name].p_upper[n])
            Parms_layout.addWidget(parm_row)
            self.parm_rows.append(parm_row)
            
        Parms_layout.addStretch()
        self.Parms.setLayout(Parms_layout)
        self.layout.addWidget(self.Parms,3,0,1,4)
        
        
    def on_function_change(self):
        self.Parms.deleteLater()
        self.build_parms_input()


    @property
    def fun_name(self):
        return self.fun_input.currentText()
    
    @property
    def parm_names(self):
        return tuple([row.values[0] for row in self.parm_rows])

    @property
    def parms(self):
        "dict with parm_names as keys and p0 as values"
        return {row.values[0]:row.values[1] for row in self.parm_rows}

    @property
    def p0(self):
        "tuple with p0 as values"
        return tuple([row.values[0] for row in self.parm_rows])

    @property
    def p_lower(self):
        "tuple with lower bound as values"
        return tuple([row.values[2] for row in self.parm_rows]) 

    @property
    def p_upper(self):
        "tuple with upper bound as values"
        return tuple([row.values[3] for row in self.parm_rows]) 
    
    @property
    def bounds(self):
        "dict with parm_names as keys and bounds as values"
        out = {}
        for row in self.parm_rows:
                out[row.values[0]] = (row.values[2],row.values[3])
        return out

    @property
    def funObj(self):
        out = self.FitFuns.funs[self.fun_name].copy(
            self.parm_names,self.p0,self.p_lower, self.p_upper)
        return out
    
    
# =============================================================================
# Functions Panel
# =============================================================================        
class FunctionsInputPanel(QWidget):
    """
    This Panel handles user input for functions and their parameters.
    It returns FitFunction (siehe utils.auxiliary) objects.
    """
    
    function_added= Signal()
    common_parms_changed= Signal()
    
    def __init__(self,defaults:list=None, irf:str=''):
        super().__init__()
        
        self.FitFuns = FitFunctions() #loads available fit functions.
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.main_layout = QVBoxLayout(frame)
        
        self.create_ui()
        
        central = QVBoxLayout()
        self.setLayout(central)
        central.addWidget(frame)
        
        if defaults:
            self.set_defaults(defaults)
           
        if irf:
            self.add_irf(irf)
    
    
    def create_ui(self):
        layout = self.main_layout
        
        layout_header = QGridLayout()
        Label(layout_header, 'Common Parms.', (0,0))
        self.common_parms_input = Inputbox(layout_header, '', (0,1))
        Button(layout_header,'add component', (1,0), connect=lambda:self.add_component())
        Button(layout_header,'remove component', (1,1), connect=self.remove_component)
        layout.addLayout(layout_header)
        
        self.parm_tabs = QTabWidget()
        self.parm_tabs.setFixedSize(250, 300)
        
        layout.addWidget(self.parm_tabs)
    
    
    @property
    def tab_count(self):
        return sum(1 for i in range(self.parm_tabs.count())
            if "IRF" not in self.parm_tabs.tabText(i))

        
    def set_defaults(self,defaults):
       for fun_name in defaults:
           self.add_component(fun_name)
           
   
    def add_irf(self,irf_function):
        if irf_function not in self.FitFuns.funs.keys():
            irf_function = 'gauss'
        tab = ParmsPanel(self.FitFuns,fun_name=irf_function)
        self.parm_tabs.addTab(tab,'IRF')

   
    def add_component(self,fun_name='exp_decay',tab_name=None):  
           if not tab_name:
               tab_name = 'fun'+str(self.tab_count+1)      
           tab = ParmsPanel(self.FitFuns,fun_name=fun_name)
           self.parm_tabs.insertTab(self.tab_count,tab,tab_name)
           self.relabel_tabs()
           self.update_common_parms(self.FitFuns.funs[fun_name].common_parms)


    def relabel_tabs(self):
       for i in range(self.tab_count):
           if not 'IRF' in self.parm_tabs.tabText(i):
               self.parm_tabs.setTabText(i, f"fun{i+1}")
               
               
    def update_common_parms(self,new_common_parms=[]):
       common_parms = self.common_parms_input.text().split(',')
       for new_common_parm in new_common_parms:
           if new_common_parm not in common_parms:
               common_parms.append(new_common_parm)
               common_parms = [v for v in common_parms if v!='' and v!=' ']
       self.common_parms_input.setText((','.join(common_parms)))
       
   
    def remove_component(self):
       if self.parm_tabs.count()>1:
           widget = self.parm_tabs.currentWidget()
           index = self.parm_tabs.indexOf(widget)
       
           if index != -1:#-1 is returned if widget not found.
               self.parm_tabs.removeTab(index)
               widget.deleteLater()
               self.relabel_tabs()
       else:
           QMessageBox.warning(self,'Not so fast!',"Can't remove all components")
    

    @property
    def no_comps(self):
        return self.parm_tabs.count()
    
    @property
    def irf_index(self):
        irf_index = [n for n in range(self.parm_tabs.count()) if self.parm_tabs.tabText(n)=='IRF']
        if irf_index:
            return irf_index[0]
        else:
            None

    @property
    def IRF(self):
        if self.irf_index:
            return self.parm_tabs.widget(self.irf_index).values
        else:
            return None

    @property
    def fun_names(self):
        return tuple([self.parm_tabs.tabText(n) for n in range(self.parm_tabs.count())])
          
    @property
    def funObjs(self):
        out = {}
        for n in range(self.no_comps):
            out[self.parm_tabs.tabText(n)] = self.parm_tabs.widget(n).funObj
        return out

    @property
    def funs(self):
        out = {}
        ff = self.funObjs
        for name in ff:
            out[name] = ff[name].func
        return out
    
    @property
    def common_parms(self):
        return tuple(self.common_parms_input.text().replace(' ','').split(','))

    @property
    def parms(self):
        out = {}
        for n in range(self.no_comps):
            out[self.parm_tabs.tabText(n)] = self.parm_tabs.widget(n).parms
        return out

    @property
    def bounds(self):
        out = {}
        for n in range(self.no_comps):
            out[self.parm_tabs.tabText(n)] = self.parm_tabs.widget(n).bounds
        return out
    
# =============================================================================
# Plot Panel
# =============================================================================
class LinesWidget(QWidget):
    
    data = dict()
    
    kwargs_raw ={'linestyle': 'None',
                'marker': 'o',
                'markerfacecolor': 'None',
                'markeredgecolor': 'k',
                'markeredgewidth': 0.5,
                'markersize': 6}
    kwargs_raw_inner ={'linestyle': 'None',
                'marker': 'o',
                'markerfacecolor': 'k',
                'markeredgecolor': 'k',
                'markeredgewidth': 0.1,
                'markersize': 0.8}
    
    
    def __init__(self, figsize = (18,9), plot_style='linear'):
        super().__init__()
        
        self.create_ui(figsize=figsize,plot_style=plot_style)
        self.create_connections()
    
    
    def create_ui(self,figsize=(18,9), plot_style='linear'):
        layout = QVBoxLayout()

        self.kin = LineCanvas(figsize=figsize,plot_style=plot_style)
        self.y_slider = Slider()
        self.rescale_kin = Button(text='rescale')
        self.auto_scale_kin = Button(text='auto scale')
        self.spec = LineCanvas(figsize=figsize)
        self.x_slider = Slider()
        self.rescale_spec = Button(text='rescale')
        self.auto_scale_spec = Button(text='auto scale')
        
        self.auto_scale_kin.setCheckable(True)
        self.auto_scale_spec.setCheckable(True)
        
        self.auto_scale_kin.setStyleSheet(':checked {background-color: rgb(80,180,80);}')
        self.auto_scale_spec.setStyleSheet(':checked {background-color: rgb(80,180,80);}')       
        
        layout.addWidget(self.kin)
        x_foot_layout = QHBoxLayout()
        x_foot_layout.addWidget(self.y_slider)
        x_foot_layout.addWidget(self.rescale_kin)
        x_foot_layout.addWidget(self.auto_scale_kin)
        layout.addLayout(x_foot_layout)
        layout.addWidget(self.spec)
        y_foot_layout = QHBoxLayout()
        y_foot_layout.addWidget(self.x_slider)
        y_foot_layout.addWidget(self.rescale_spec)
        y_foot_layout.addWidget(self.auto_scale_spec)
        layout.addLayout(y_foot_layout)
        
        self.setLayout(layout)
        
    
    def create_connections(self):
        self.y_slider.moved.connect(self.refresh_kin_plot)
        self.x_slider.moved.connect(self.refresh_spec_plot)
        
        self.rescale_kin.clicked.connect(self.kin.rescale)
        self.rescale_spec.clicked.connect(self.spec.rescale)
    
        
    def set_slider_limits(self, x_limits, y_limits):
        self.x_slider.set_limits(x_limits)
        self.y_slider.set_limits(y_limits)
        
        
    def make_plots(self,data):
        """
        This function draws the lines.

        Parameters
        ----------
        data : This is the fancy fit custon data_class.

        """
        
        self.data = data
        
        x = data.x
        y = data.y
        Z = data.z
        
        x_fit = data.x_fit
        y_fit = data.y_fit
        Z_fit = data.z_fit
        
        iy0 = np.argmax(y>=self.y_slider.value)
        ix0 = np.argmax(x>=self.x_slider.value)

        self.kin.set_line('raw',x,Z[:,iy0],**self.kwargs_raw)
        self.kin.set_line('raw_inner',x,Z[:,iy0],**self.kwargs_raw_inner)
        self.kin.set_line('fit',x_fit,Z_fit[:,iy0],color='red')           
        self.kin.draw_idle()
        
        self.spec.set_line('raw',y,Z[ix0,:],**self.kwargs_raw)
        self.spec.set_line('raw_inner',y,Z[ix0,:],**self.kwargs_raw_inner)
        self.spec.set_line('fit',y_fit,Z_fit[ix0,:],color='red')           
        self.spec.draw_idle()
       
        if self.auto_scale_kin.isChecked():
           self.kin.rescale()
           
        if self.auto_scale_spec.isChecked():
           self.spec.rescale()
           
        self.set_slider_limits((min(self.data.x),max(self.data.x)),
                               (min(self.data.y),max(self.data.y)))
           
    
    def refresh_kin_plot(self):
        iy0 = np.argmax(self.data.y>=self.y_slider.value)

        self.kin.set_line('raw',self.data.x,self.data.z[:,iy0],**self.kwargs_raw)
        self.kin.set_line('raw_inner',self.data.x,self.data.z[:,iy0],**self.kwargs_raw_inner)
        self.kin.set_line('fit',self.data.x_fit,self.data.z_fit[:,iy0],color='red')           
        self.kin.draw_idle()
       
        if self.auto_scale_kin.isChecked():
           self.kin.rescale()

        
    def refresh_spec_plot(self):
        ix0 = np.argmax(self.data.x>=self.x_slider.value)
        
        self.spec.set_line('raw',self.data.y,self.data.z[ix0,:],**self.kwargs_raw)
        self.spec.set_line('raw_inner',self.data.y,self.data.z[ix0,:],**self.kwargs_raw_inner)
        self.spec.set_line('fit',self.data.y_fit,self.data.z_fit[ix0,:],color='red')           
        self.spec.draw_idle()
           
        if self.auto_scale_spec.isChecked():
           self.spec.rescale()
        


class ContoursWidget(QWidget):
    
    def __init__(self, figsize=(9,9), plot_style='linear'):
        super().__init__()
        
        self.Z = ContourCanvas(figsize=figsize,layout=plot_style)
        self.Z_fit = ContourCanvas(figsize=figsize,layout=plot_style)
        self.residuum = ContourCanvas(figsize=figsize,layout=plot_style)
        self.DADS = LineCanvas(figsize=figsize)

        layout = QGridLayout()
        layout.addWidget(self.Z,0,0)
        layout.addWidget(self.Z_fit,0,1)
        layout.addWidget(self.residuum,1,0)
        layout.addWidget(self.DADS,1,1)
        
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        
        self.setLayout(layout)
        
    def make_plots(self, data, sc = 1):
       zrange = np.array([np.median(data.z[data.z<0]),
                 np.median(data.z[data.z>0])])
       zrange = list(zrange*5*sc)#5 works well in the datasets I had so far. That's why this is defined as a stretch factor of 1.
       if np.isnan(zrange).any():
           zrange = [0,1]
       
       self.Z.set_contour(data.y,data.x,data.z,zrange=zrange)
       self.Z_fit.set_contour(data.y_fit,data.x_fit,data.z_fit,zrange=zrange)
       self.residuum.set_contour(data.y_fit,data.x_fit,data.residuum,zrange=zrange)
       
       self.DADS.clear_lines()
       for n in range(data.no_comps):
           self.DADS.set_line(f'f{n+1}',data.y_fit,data.DADS[n,:])
       
       self.Z.draw_idle()
       self.Z_fit.draw_idle()
       self.residuum.draw_idle()
       self.DADS.draw_idle()
       

    def rescale(self):
        self.Z.rescale()
        self.Z_fit.rescale()
        self.residuum.rescale()
        self.DADS.rescale()
        

class PlotPanel(QWidget):
    """
    This Panel holds the different plots in various tabs.
    """
    
    figsize_2D = (18,9)
    figsize_3D = (9,9)
    
    def __init__(self,plot_style = 'linear'):
        super().__init__()
        
        self.plot_style = plot_style
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.main_layout = QGridLayout(frame)
        
        self.create_ui()
        
        central = QVBoxLayout()
        self.setLayout(central)
        central.addWidget(frame)
    
    
    def create_ui(self):
        layout = self.main_layout
        
        Tabs = QTabWidget()
        
        self.lines = LinesWidget(figsize=self.figsize_2D, plot_style=self.plot_style)
        self.contours = ContoursWidget(figsize=self.figsize_3D, plot_style=self.plot_style)
        
        Tabs.addTab(self.lines,'2D plots')
        Tabs.addTab(self.contours,'3D plots')
        
        layout.addWidget(Tabs)
     
    
    def make_plots(self,data,plot_style='linear'):
        self.lines.make_plots(data)
        self.contours.make_plots(data)


    def set_labels(self,x_name=None,x_label=None,x_unit=None,
                       y_name=None,y_label=None,y_unit=None,
                                   z_label=None,z_unit=None,):
       self.lines.kin.fig.suptitle(x_name)
       self.lines.kin.set_labels(x_label+'/'+x_unit,z_label+'/'+z_unit)
       self.lines.spec.fig.suptitle(y_name)
       self.lines.spec.set_labels(y_label+'/'+y_unit,
                                 z_label+'/'+z_unit)
       
       
    def rescale(self):
        self.lines.kin.rescale()
        self.lines.spec.rescale()
        self.contours.rescale()


    
# =============================================================================
# Results Panel    
# =============================================================================
class ResultsPanel(QWidget):
    """
    This Panel shows results.
    """
    
    requested_parm_transfer = Signal()
    
    def __init__(self):
        super().__init__()
     
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.main_layout = QVBoxLayout(frame)
        
        Label(self.main_layout,'Results')
        self.results_box = QPlainTextEdit(self)
        self.results_box.setFixedWidth(300)
        self.results_box.setReadOnly(True)
        self.results_box.setFont(QFont("Courier New"))        
        self.main_layout.addWidget(self.results_box)
        
        Button(self.main_layout,'Copy Results to p0', connect=self.requested_parm_transfer)
        
        central = QVBoxLayout()
        self.setLayout(central)
        central.addWidget(frame)


    def appendText(self,text):
        self.results_box.appendPlainText(text)
        self.results_box.verticalScrollBar().setValue(
            self.results_box.verticalScrollBar().maximum())
    
    def setText(self,text):
        self.results_box.setPlainText(text)
