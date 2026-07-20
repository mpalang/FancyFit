# -*- coding: utf-8 -*-
"""
Created on Sun 7 June 14:27:42 2026

@author: moritzpalang

This Window is for modifying user settings. It will store user settings in a .json file in the user folder. 
Standard settings will be in the python code so they can not accidentally be modified by user.
The settings will also be returned if called by another window.

"""

import sys
from pathlib import Path
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from copy import deepcopy


from PySide6.QtGui import QIcon
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
)

# Add personal modules:
if str(Path(__file__).parent.parent) not in sys.path:
      sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import add_logger  
from utils.auxiliary import fancyfitSettings
from gui.Elements import (Button,Slider,Dropdown,Inputbox,Textbox,Label,Spinbox,Checkbox)

logger = add_logger(__name__)
import traceback
  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class SettingsWindow(QDialog):
    def __init__(self,settings= None):
     try:
        super().__init__()
        self.setWindowTitle("Settings")
        icon_path = Path(Path(__file__).parent,'Settings_Icon.ico')
        self.setWindowIcon(QIcon(str(icon_path)))

        if settings:
            self.settings = deepcopy(settings)
        else:
            self.settings = fancyfitSettings()
        self.input = {}
        self.build_gui()
     except Exception as e:
         logger.error(traceback.format_exc())
         QMessageBox.critical(self,'error',f'Fatal Error in {__name__}: {e}')

# =============================================================================
# Functions:
# =============================================================================
    
    # =============================================================================
    # GUI Functions:
    # =============================================================================
    def build_gui(self):
        main_layout = QGridLayout()
        
        frame_general = QFrame()
        frame_general.setFrameShape(QFrame.StyledPanel)
        frame_general.setFrameShadow(QFrame.Raised)
        layout_general = QGridLayout()
        Label(layout_general,'General Settings',bold=True,layout_args=(0,0))
        Label(layout_general,'Scaling Factor z',layout_args=(1,0))
        self.input['scaling_factor_z'] = Inputbox(layout_general,default=str(self.settings.scaling_factor_z),layout_args=(1,1))
        Label(layout_general,'Scaling Factor x',layout_args=(2,0))
        self.input['scaling_factor_x'] = Inputbox(layout_general,default=str(self.settings.scaling_factor_x),layout_args=(2,1))
        Label(layout_general,'Scaling Factor y',layout_args=(3,0))
        self.input['scaling_factor_y'] = Inputbox(layout_general,default=str(self.settings.scaling_factor_y),layout_args=(3,1))
        frame_general.setLayout(layout_general)
        main_layout.addWidget(frame_general,0,0)
        
        frame_fit = QFrame()
        frame_fit.setFrameShape(QFrame.StyledPanel)
        frame_fit.setFrameShadow(QFrame.Raised)
        layout_fit = QGridLayout()
        Label(layout_fit,'Fit Settings',bold=True,layout_args=(0,0))
        Label(layout_fit,'Iterations',layout_args=(1,0))
        self.input['fit_iterations'] = Spinbox(layout_fit,1,10,self.settings.fit_iterations,layout_args=(1,1))
        Label(layout_fit,'Default Fit Method',layout_args=(2,0))
        self.input['default_method'] = Inputbox(layout_fit,default=self.settings.default_method,layout_args=(2,1))
        Label(layout_fit,'Use IRF',layout_args=(3,0))
        self.input['use_irf'] = Checkbox(layout_fit,default=self.settings.use_irf,grid=(3,1))
        frame_fit.setLayout(layout_fit)
        main_layout.addWidget(frame_fit,0,1)
        
        frame_plot = QFrame()
        frame_plot.setFrameShape(QFrame.StyledPanel)
        frame_plot.setFrameShadow(QFrame.Raised)
        layout_plot = QGridLayout()
        Label(layout_plot,'Plot Settings',bold=True,layout_args=(0,0))
        Label(layout_plot,'z 3D stretch',layout_args=(1,0))
        self.input['z_3Dstretch'] = Inputbox(layout_plot,default=str(self.settings.z_3Dstretch),layout_args=(1,1))
        Label(layout_plot,'plot layout',layout_args=(2,0))
        self.input['plot_style'] = Inputbox(layout_plot,default=str(self.settings.axes_break),layout_args=(2,1))
        Label(layout_plot,'axes_break',layout_args=(3,0))
        self.input['axes_break'] = Inputbox(layout_plot,default=str(self.settings.axes_break),layout_args=(3,1))
        frame_plot.setLayout(layout_plot)
        main_layout.addWidget(frame_plot,1,0)

        frame_data = QFrame()
        frame_data.setFrameShape(QFrame.StyledPanel)
        frame_data.setFrameShadow(QFrame.Raised)
        layout_data = QGridLayout()
        Label(layout_data,'Data Settings',bold=True,layout_args=(0,0))
        Label(layout_data,'label',layout_args=(1,1))
        Label(layout_data,'units',layout_args=(1,2))
        Label(layout_data,'x',layout_args=(2,0))
        self.input['x_label'] = Inputbox(layout_data,default=self.settings.x_label,layout_args=(2,1))
        self.input['x_unit'] = Inputbox(layout_data,default=self.settings.x_unit,layout_args=(2,2))
        Label(layout_data,'y',layout_args=(3,0))
        self.input['y_label'] = Inputbox(layout_data,default=self.settings.y_label,layout_args=(3,1))
        self.input['y_unit'] = Inputbox(layout_data,default=self.settings.y_unit,layout_args=(3,2))  
        Label(layout_data,'z',layout_args=(4,0))
        self.input['z_label'] = Inputbox(layout_data,default=self.settings.z_label,layout_args=(4,1))
        self.input['z_unit'] = Inputbox(layout_data,default=self.settings.z_unit,layout_args=(4,2))  
        frame_data.setLayout(layout_data)
        main_layout.addWidget(frame_data,1,1)
        
        Button(main_layout,'Save',command=self.on_save,layout_args=(2,0,1,2))
        Button(main_layout,'Cancel',command=self.on_cancel,layout_args=(3,0,1,2))
        
        self.setLayout(main_layout)
    
    def read_input(self):
        for key in self.input:
            if isinstance(self.input[key], Inputbox):
                self.settings.__dict__[key] = self.input[key].text()
            elif isinstance(self.input[key], Spinbox):
                self.settings.__dict__[key] = self.input[key].value()

    def on_save(self):
        self.read_input()
        self.accept()
    
    def on_cancel(self):
        self.close()
        
        
        

    #%% =============================================================================
    # Data and Settings Functions:
    # =============================================================================
     
    
# ---------------------------
# ENTRY POINT (Spyder-safe)
if __name__ == "__main__":
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    window = SettingsWindow()
    window.show()

    if not QApplication.instance().startingUp():
        sys.exit(app.exec())
    else:
        app.exec()
