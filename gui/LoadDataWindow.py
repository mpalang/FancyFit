# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 16:26:38 2026

@author: moritzpalang

This Window is for loading data. """

import sys
from pathlib import Path
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt


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

# from PySide6.QtGui import QFont

# from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

# Add personal modules:
if str(Path(__file__).parent.parent) not in sys.path:
      sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import add_logger  
from utils.auxiliary import data_class,fancyfitSettings
from gui.Elements import (Button,Slider,Dropdown,Inputbox,MplCanvas,Textbox,Label,Spinbox,
                          open_path,)

logger = add_logger(__name__)
import traceback
  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class LoadDataWindow(QDialog):
    def __init__(self):
     try:
        super().__init__()
        self.setWindowTitle("Load Data")
        # self.resize(500, 500)
        self.set = fancyfitSettings()
        self.build_gui()
     except Exception as e:
         logger.exception('Load Data Window error')
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
        layout_general = QVBoxLayout()
        Dropdown(layout_general,['Multiple Files','One File'])

        Label(layout_general,'x data',bold=True)
        self.x_path = open_path(layout_general,default_path=self.set.x_data_path)
        Label(layout_general,'y data',bold=True)
        self.y_path = open_path(layout_general,default_path=self.set.y_data_path)
        Label(layout_general,'Z data',bold=True)
        self.z_path = open_path(layout_general,default_path=self.set.z_data_path)
        
        frame_general.setLayout(layout_general)
        main_layout.addWidget(frame_general)
    
        frame_action = QFrame()
        layout_action = QHBoxLayout()
        Button(layout_action,'Load',command=self.on_save)
        Button(layout_action,'Cancel',command=self.on_cancel)
        frame_action.setLayout(layout_action)
        main_layout.addWidget(frame_action)
        
        self.setLayout(main_layout)
    
    def on_save(self):
        x_path = self.x_path.input_path
        x = np.genfromtxt(x_path)
        self.set.x_data_path = x_path
        y_path = self.y_path.input_path
        y = np.genfromtxt(y_path)
        self.set.y_data_path = y_path
        z_path = self.z_path.input_path
        z = np.genfromtxt(z_path)
        self.set.z_data_path = z_path
        
        self.set.save()
        
        self.data = data_class(x=x,y=y,z=z)
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

    window = LoadDataWindow()
    window.show()

    if not QApplication.instance().startingUp():
        sys.exit(app.exec())
    else:
        app.exec()
