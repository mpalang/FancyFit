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

from PySide6.QtCore import Signal

from utils.logger import add_logger  
from utils.auxiliary import fancyfitSettings
from gui.Elements import (Button,Slider,Dropdown,Inputbox,Textbox,Label,Spinbox,Checkbox)

from utils.logger import add_logger
from utils.error_handling import error_handler

import traceback
  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class SaveWindow(QDialog):
    
    change_dict = {'function_panel':False,
                   'needs_replot':False,}
    
    @error_handler
    def __init__(self):
        super().__init__()
        self.logger = add_logger(__name__)
        self.setWindowTitle("Save Fit Results")
        icon_path = Path(Path(__file__).parent,'Load_Icon.ico')
        self.setWindowIcon(QIcon(str(icon_path)))

        self.data_input = {}
        self.plots_input = {}

        self.data = {}
        self.plots = {}

        self.build_ui()


# =============================================================================
# Functions:
# =============================================================================
    
    # =============================================================================
    # GUI Functions:
    # =============================================================================
    def build_ui(self):
        main_layout = QVBoxLayout()
        
        frame_data = QFrame()
        frame_data.setFrameShape(QFrame.StyledPanel)
        frame_data.setFrameShadow(QFrame.Raised)
        layout_data = QGridLayout()
        Label(layout_data,'Cut Data',(1,0))
        self.data_input['cut'] = Checkbox(layout_data,False,(1,1))
        Label(layout_data,'Fit Data',(1,2))
        self.data_input['fit'] = Checkbox(layout_data,True,(1,3))
        Label(layout_data,'DADS Data',(2,0))
        self.data_input['DADS'] = Checkbox(layout_data,True,(2,1))
        Label(layout_data,'Kinetics Data',(2,2))
        self.data_input['D'] = Checkbox(layout_data,True,(2,3))
        Label(layout_data,'Residuum',(3,0))
        self.data_input['residuum'] = Checkbox(layout_data,True,(3,1))
        Label(layout_data,'Fit Report',(4,0))
        self.data_input['fit_report'] = Checkbox(layout_data,True,(4,1))
        frame_data.setLayout(layout_data)
        main_layout.addWidget(frame_data)

        frame_plots = QFrame()
        frame_plots.setFrameShape(QFrame.StyledPanel)
        frame_plots.setFrameShadow(QFrame.Raised)
        layout_plots = QGridLayout()
        Label(layout_plots,'Kinetics',(1,0))
        self.plots_input['kin'] = Checkbox(layout_plots,False,(1,1))
        Label(layout_plots,'Spectrum',(1,2))
        self.plots_input['spec'] = Checkbox(layout_plots,True,(1,3))
        Label(layout_plots,'Raw Contour',(2,0))
        self.plots_input['raw_contour'] = Checkbox(layout_plots,True,(2,1))
        Label(layout_plots,'Fit Contour',(2,2))
        self.plots_input['fit_contour'] = Checkbox(layout_plots,True,(2,3))
        Label(layout_plots,'Residuum',(3,0))
        self.plots_input['residuum'] = Checkbox(layout_plots,True,(3,1))
        Label(layout_plots,'DADS',(4,0))
        self.plots_input['DADS'] = Checkbox(layout_plots,True,(4,1))
        frame_plots.setLayout(layout_plots)
        main_layout.addWidget(frame_plots)

        Button(main_layout,'Save',connect=self.on_save)
        Button(main_layout,'Cancel',connect=self.on_cancel)
        
        self.setLayout(main_layout)

    
    def read_input(self):

        for key in self.data_input:
            self.data[key] = self.data_input[key].isChecked()

        for key in self.plots_input:
            self.plots[key] = self.plots_input[key].isChecked()
    

    def on_save(self):
        self.read_input()
        self.accept()
    
    
    def on_cancel(self):
        self.close()
        
        
# ---------------------------
# ENTRY POINT (Spyder-safe)
# ---------------------------
if __name__ == "__main__":
    
    if str(Path(__file__).parent.parent) not in sys.path:
        sys.path.append(str(Path(__file__).parent.parent))
    
    # Create QApplication only once
    app = QApplication.instance()
    app.setStyle("Fusion")
    if app is None:
        app = QApplication(sys.argv)
    
    window = SettingsWindow()
    window.show()
    
    app.exec()