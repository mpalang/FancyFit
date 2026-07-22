# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:05:55 2026

@author: moritzpalang

This contains all widgets used in the Main Window.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QTabWidget,
    QSizePolicy,
    QMessageBox
)

from PySide6.QtCore import Signal

from gui.Elements import Button,Inputbox,Label,Dropdown
from utils.auxiliary import FitFunctions

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
        Label(layout,'x', (1, 0))
        self.x_low = Inputbox(layout, '1', (1, 1))
        self.x_high = Inputbox(layout, '2', (1,2))
        Label(layout,'y', (2,0))
        self.y_low = Inputbox(layout, '3', (2,1))
        self.y_high = Inputbox(layout, '4', (2,2))
        
        self.old_style = self.y_high.styleSheet() # store old style so it can be reset after validate
        
    def create_connections(self):
        # self.x_low.
        self.cut_button.clicked.connect(self._cut_requested)
        self.uncut_button.clicked.connect(self._uncut_requested)
    
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
            self.set_bg_color('red')
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
    
    def _uncut_requested(self):
        if self.validate():
            self.uncut_requested.emit()
    
    def set_defaults(self):
        pass
    
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
            
  
# =============================================================================
# Parm Row Widget used in ParmsPanel         
# =============================================================================
class ParmRow(QWidget):
    def __init__(self,name,p0,p_lower,p_upper):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        layout = QHBoxLayout(self)
        self.name_input = Inputbox(layout,default=name)
        self.p0_input = Inputbox(layout,default=str(p0))
        self.p_lower_input = Inputbox(layout,default=str(p_lower))
        self.p_upper_input = Inputbox(layout,default=str(p_upper))
                 
        self.p0_input.textChanged.connect(self.validate_on_the_fly)
        self.p_lower_input.textChanged.connect(self.validate_on_the_fly)
        self.p_upper_input.textChanged.connect(self.validate_on_the_fly)
        
    def validate_on_the_fly(self):
        try:
            ok = (
                float(self.p_lower_input.text())
                <= float(self.p0_input.text())
                <= float(self.p_upper_input.text())
                )
            if ok:
               self.setStyleSheet("")
               return True
            else:
                self.setStyleSheet("background:#ffcccc;")
                return False
        except:
            pass #We don't need to do anything here yet...otherwise too many errors are raised.
        
    def validate(self):
        try:
            ok = (
                float(self.p_lower_input.text())
                <= float(self.p0_input.text())
                <= float(self.p_upper_input.text())
                )
            if ok:
               self.setStyleSheet("")
               return True
            else:
                self.setStyleSheet("background:#ffcccc;")
                return False
        except Exception as e:
            # logger.error(f'Problem with parameter input:\n {e}') #can activate for debugging. Otherwise it would write too much if user is typing.
            raise ValueError(f'Make sure you only put in numbers:\n {e}')
            return False
  
    def values(self):
        if self.validate():
            name = self.name_input.text()
            p0 = float(self.p0_input.text())
            p_lower = float(self.p_lower_input.text())
            p_upper = float(self.p_upper_input.text())
            
            return name,p0,p_lower,p_upper
        else:
            QMessageBox.critical(self,'Check Parameters','Please make sure parameter inputs are valid.')


# =============================================================================
#  Parms Panel Widget used in FunctionsInputPanel       
# =============================================================================
class ParmsPanel(QWidget):
    def __init__(self,FitFuns,fun_name=None):
        super().__init__()
        self.FitFuns = FitFuns
        self.fun_name = fun_name
        self.layout = QGridLayout()
        # self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.fun_input = (Dropdown(self.layout,
                                    FitFuns.names(),
                                    standard=fun_name,
                                    command=lambda:self.on_function_change(),
                                    grid=(0,0,1,4)
                                    ))
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
            parm_row = (ParmRow(parm,
                          self.FitFuns.funs[fun_name].p0[n],
                          self.FitFuns.funs[fun_name].p_lower[n],
                          self.FitFuns.funs[fun_name].p_upper[n])) 
            Parms_layout.addWidget(parm_row)
            self.parm_rows.append(parm_row)
            
        Parms_layout.addStretch()
        self.Parms.setLayout(Parms_layout)
        self.layout.addWidget(self.Parms,3,0,1,4)
        
    def on_function_change(self):
        self.Parms.deleteLater()
        self.build_parms_input()
    
    def values(self):
        fields = [row.values() for row in self.parm_rows]
        
        func = self.FitFuns.funs[self.fun_input.currentText()].copy(
                            [d[0] for d in fields],#parm names
                            [d[1] for d in fields],#p0
                            [d[2] for d in fields],#p lower
                            [d[3] for d in fields]#p upper
                            )
            
        return func
    
    
# =============================================================================
# Functions Panel
# =============================================================================

        # # Parameters
        # layout.addWidget(QLabel("Parameters"))
        
        # layout_common_parms_and_add_comp = QGridLayout()
        # # layout.addWidget(QLabel("Common Param"))
        # Label(layout_common_parms_and_add_comp,'Common Parms.',layout_args=(0,0))
        # self.common_parms_input = Inputbox(layout_common_parms_and_add_comp,layout_args=(1,0,1,1))
        # Button(layout_common_parms_and_add_comp,'add component',command=lambda :self.build_parm_panel(),layout_args=(0,1))
        # Button(layout_common_parms_and_add_comp,'remove component',command=lambda :self.remove_parm_panel(),layout_args=(1,1))
        # layout.addLayout(layout_common_parms_and_add_comp)
        
        # self.layout_functions = QVBoxLayout()
        # self.parm_tabs = QTabWidget()
        # self.parm_tabs.setFixedSize(250, 300)

        # for f in self.set.default_funs:
        #     self.create_parm_panel(fun_name=f)     
        # if self.set.use_irf:
        #     self.create_parm_panel(fun_name='gauss',tab_name='IRF')
        # self.layout_functions.addWidget(self.parm_tabs)
        # layout.addLayout(self.layout_functions)   
        
        
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

         self.main_layout = QGridLayout(frame)
         
         self.create_elements()
         self.create_layout()
         self.create_connections()
         
         central = QVBoxLayout()
         self.setLayout(central)
         central.addWidget(frame)
         
         if defaults:
             self.set_defaults(defaults)
            
         if irf:
             self.add_irf(irf)
     
     
     def create_elements(self):
         layout = self.main_layout
         
         layout_header = QGridLayout()
         Label(layout_header,'Common Parms.',layout_args=(0,0))
         self.common_parms_input = Inputbox(layout_header, '', (1,0,1,1))
         Button(layout_header,'add component',(0,1),command=lambda :self.build_parm_panel())
         Button(layout_header,'remove component',(1,1),command=lambda :self.remove_parm_panel())
         layout.addLayout(layout_header,0,0,1,2)
         
         self.parm_tabs = QTabWidget()
         self.parm_tabs.setFixedSize(250, 300)
         
         
     def create_layout(self):
         layout = self.main_layout
         
         layout.addWidget(self.parm_tabs)
         

     def create_connections(self):
         pass
         # self.mode_input.currentTextChanged.connect(self.mode_changed)
         # self.method_input.currentTextChanged.connect(self.method_changed)
         
     def set_defaults(self,defaults):
        for fun_name in defaults:
            self.create_parm_panel(fun_name)
            
    
     def add_irf(self,irf_function):
         if irf_function in self.FitFuns.funs.keys():
             irf_function = 'gauss'
         tab = ParmsPanel(self.FitFuns,fun_name=irf_function)
         self.parm_tabs.addTab(tab,'IRF')

    
     def create_parm_panel(self,fun_name='exp_decay',tab_name=None):  
            if not tab_name:
                tab_name = 'fun'+str(self.parm_tabs.count()+1)      
            tab = ParmsPanel(self.FitFuns,fun_name=fun_name)
            self.parm_tabs.addTab(tab,tab_name)
            self.relabel_tabs()
            self.update_common_parms(self.FitFuns.funs[fun_name].common_parms)


     def relabel_tabs(self):
        for i in range(self.parm_tabs.count()):
            if not 'IRF' in self.parm_tabs.tabText(i):
                self.parm_tabs.setTabText(i, f"fun{i+1}")
                
                
     def update_common_parms(self,new_common_parms=['']):
        common_parms = self.common_parms_input.text().split(',')
        for new_common_parm in new_common_parms:
            if new_common_parm not in common_parms:
                common_parms.append(new_common_parm)
                common_parms = [v for v in common_parms if v!='' and v!=' ']
        self.common_parms_input.setText((','.join(common_parms)))
        
    
     def remove_parm_panel(self):
        if self.parm_tabs.count()>1:
            widget = self.parm_tabs.currentWidget()
            index = self.parm_tabs.indexOf(widget)
        
            if index != -1:#-1 is returned if widget not found.
                self.parm_tabs.removeTab(index)
                widget.deleteLater()
                self.relabel_tabs()
        else:
            QMessageBox.warning(self,'Not so fast!',"Can't remove all components")
    


