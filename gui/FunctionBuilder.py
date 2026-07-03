# -*- coding: utf-8 -*-
"""
Created on Sun 7 June 14:27:42 2026

@author: moritzpalang

This Window is for creating or modifying fit functions.

"""

from dataclasses import dataclass
import sys
from pathlib import Path
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import warnings


from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QTabWidget,
    QMessageBox,
    QTextEdit,
    QSizePolicy,
)

# Add personal modules:
if str(Path(__file__).parent.parent) not in sys.path:
      sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import add_logger  
from gui.Elements import (Button,Slider,Dropdown,Inputbox,MplCanvas,Textbox,Label,Spinbox,
                          ParmRow)
from utils.auxiliary import FitFunctions, fitFunction

logger = add_logger(__name__)
import traceback
  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class FunctionBuilder(QDialog):
    def __init__(self):
     # try:
        super().__init__()
        self.setWindowTitle("FunctionBuilder")
        # self.resize(500, 500)
        # self.set_defaults()
        self.parms=[]
        self.p0=[]
        self.p_lower=[]
        self.p_upper=[]
        self.FitFuncs = FitFunctions()
        self.build_gui()
     # except Exception as e:
     #     logger.error(traceback.format_exc())
     #     QMessageBox.critical(self,'error',f'Fatal Error in {__name__}: {e}')

# =============================================================================
# Functions:
# =============================================================================
    
    # =============================================================================
    # GUI Functions:
    # =============================================================================
    def build_gui(self):
        main_layout = QGridLayout()
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.layout = QGridLayout()
        self.fun_name_input = Inputbox(self.layout,"func name",grid=(0,0))
        # Label(self.layout,'Template:',grid=(0,1))
        # Dropdown(self.layout,self.FitFuncs.names(),self.FitFuncs.names()[0],layout_args=(0,2))
        self.expr_input = Inputbox(self.layout,"a*(x-x0)+b+c*exp(-d*(x-x0))",grid=(1,0,1,3))
        Label(self.layout,'parm names',grid=(2,0))
        Label(self.layout,'common parms',grid=(2,1))
        self.parms_input = Inputbox(self.layout,"x0, a, b, c, d",grid=(3,0))
        self.common_parms_input = Inputbox(self.layout,default='x0',grid=(3,1))
        Button(self.layout,'Refresh',command=self.refresh_parms,grid=(3,2))
        
        self.frame_parms = QFrame()
        self.frame_parms.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.layout_parms = QGridLayout
            
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line, 5, 0, 1, 4)
        
        self.parms_panel = self.ParmsPanelClass(self)
        self.layout.addWidget(self.parms_panel,6,0,1,3)
        
        frame.setLayout(self.layout)
        main_layout.addWidget(frame,0,0,1,2)
        
        # =============================================================================
        # Plot
        plot_frame = QFrame()
        plot_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_layout = QVBoxLayout()

        test_inputs_frame = QFrame()
        test_inputs_layout = QHBoxLayout()
        Label(test_inputs_layout,'x range:')
        self.x_lower = Inputbox(test_inputs_layout,default='-100')
        Label(test_inputs_layout,'-')
        self.x_upper = Inputbox(test_inputs_layout,default='100')
        test_inputs_frame.setLayout(test_inputs_layout)
        plot_layout.addWidget(test_inputs_frame)

        Button(plot_layout,'Test Data',command=self.test_data)
        self.plot = MplCanvas()
        self.plot.ax.axhline(0,color='k',linewidth=self.plot.ax.spines['left'].get_linewidth())
        plot_layout.addWidget(self.plot)
        self.lines = self.plot.ax.plot([None],[None],[None],[None],[None],[None])
        
        plot_frame.setLayout(plot_layout)
        main_layout.addWidget(plot_frame,0,2,2,1)
       
        # =============================================================================
        # Buttons
        Button(main_layout,'Save',command=self.on_save,layout_args=(1,0))
        Button(main_layout,'Cancel',command=self.on_cancel,layout_args=(1,1))
        
        self.setLayout(main_layout)

    # =============================================================================
    #    Functions
    # =============================================================================
    def get_parms(self):
        parms = self.parms_input.text().replace(' ','').split(',')
        parms = [p for p in parms if p != '']
        return parms
    
    def refresh_parms(self):
        self.parms_panel.refresh_parms()

    def test_data(self):
        # with warnings.catch_warnings():#TODO: catch numpy warnings like divide by zero.
        #   warnings.simplefilter('error')
        #   with np.errstate(divide="raise",over="raise",under="ignore",invalid="raise",):

        #     try:
                x_lower = float(self.x_lower.text())
                x_upper = float(self.x_upper.text())
                func = self.build_function()

                x = np.linspace(x_lower,x_upper,500)
                y0 = func.func(x,*func.p0)
                ylower = func.func(x,*func.p_lower)
                yupper = func.func(x,*func.p_upper)

                for n,y in enumerate([y0,ylower,yupper]):
                    self.lines[n].set_xdata(x)
                    self.lines[n].set_ydata(y)
                self.plot.ax.relim()
                self.plot.ax.autoscale_view()
                self.plot.draw()

            # except FloatingPointError as e:
            #     QMessageBox.warning(self,"Invalid function",f"Numerical error:\n{e}")
            # except Warning as e:
            #     QMessageBox.warning(self,'Problem with the definition',f'{e}')
            # except Exception as e:
            #     QMessageBox.critical(self,'Problem with the definition:',f'{e}')
        
    class ParmsPanelClass(QWidget):
        def __init__(self,parent):
            super().__init__()
            self.parent = parent
            self.layout = QGridLayout()
            Label(self.layout,'name',layout_args=(1,0))
            Label(self.layout,'initial guess',layout_args=(1,1))
            Label(self.layout,'lower boundary',layout_args=(1,2))
            Label(self.layout,'upper boundary',layout_args=(1,3))
        
            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            self.layout.addWidget(line, 2, 0, 1, 4)
            
            self.build_parms_input()
            
            self.setLayout(self.layout)
        
        def build_parms_input(self):
            self.Parms=QWidget()
            Parms_layout=QVBoxLayout()
                        
            self.parm_rows=[]
            for n, parm in enumerate(self.parent.get_parms()):
                parm_row = ParmRow(parm,0,-1,1)
                Parms_layout.addWidget(parm_row)
                self.parm_rows.append(parm_row)
                
            Parms_layout.addStretch()
            self.Parms.setLayout(Parms_layout)
            self.layout.addWidget(self.Parms,3,0,1,4)
            
        def refresh_parms(self):
            self.Parms.deleteLater()
            self.build_parms_input()
        
        def values(self):
            fields = [row.values() for row in self.parm_rows]
                
            return fields
        
    def build_function(self):
        fun_name = self.fun_name_input.text().replace(' ','')
        expr = self.expr_input.text().replace(' ','')
        parms = self.parms_panel.values()
        parm_names = [d[0] for d in parms]
        p0 = [d[1] for d in parms]
        p_lower = [d[2] for d in parms]
        p_upper = [d[3] for d in parms]
        common_parms = self.common_parms_input.text().replace(' ','').split(',')
        return fitFunction(fun_name,expr,parm_names,p0,p_lower,p_upper,common_parms)
    
    def on_save(self):
        new_func = self.build_function()
        fs = FitFunctions()
        fs.new_function(new_func)
        fs.save()
        self.accept()
    
    def on_cancel(self):
        self.reject()
    
        
        

    #%% =============================================================================
    # Data and Settings Functions:
    # =============================================================================
     
    
# ---------------------------
# ENTRY POINT (Spyder-safe)
if __name__ == "__main__":
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    window = FunctionBuilder()
    window.show()

    if not QApplication.instance().startingUp():
        sys.exit(app.exec())
    else:
        app.exec()
