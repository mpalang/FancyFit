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
    QSizePolicy,
)

# Add personal modules:
if str(Path(__file__).parent.parent) not in sys.path:
      sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import add_logger  
from gui.Elements import (Button,Slider,Dropdown,Inputbox,Textbox,Label,Spinbox,
                          ParmRow)
from utils.auxiliary import FitFunctions, fitFunction
from utils.plotting import LineCanvas
from utils.error_handling import error_handler, ErrorBox

# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class ChirpCorrectionWindow(QDialog):

    def __init__(self, data):
        super().__init__()
        self.logger = add_logger(__name__)
        self.setWindowTitle("Chirp Correction")
        icon_path = Path(Path(__file__).parent,'MainIcon.ico') #TODO: create specific Icon
        self.setWindowIcon(QIcon(str(icon_path)))
        # self.resize(500, 500)
        # self.set_defaults()

        self.data = data

        self.create_ui()

    
    def create_ui(self):
        main_layout = QGridLayout()
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        self.layout = QGridLayout()
        Label(self.layout,'x0',grid=(0,0))
        self.x0 = Inputbox(self.layout,"0",grid=(0,1))
        self.x0_lower = Inputbox(self.layout,"-5",grid=(0,2))
        self.x0_upper = Inputbox(self.layout,"5",grid=(0,3))
        Label(self.layout,'FWHM',grid=(1,0)) 
        self.fwhm0 = Inputbox(self.layout, "1", grid=(1,1))    
        self.fwhm_lower = Inputbox(self.layout, "0.1", grid=(1,2)) 
        self.fwhm_upper = Inputbox(self.layout, "10", grid=(1,3))   
        self.use_first_gauss = Button(self.layout,'gauss',grid=(2,0))
        self.use_second_gauss = Button(self.layout,'dx gauss',grid=(2,1))
        self.use_third_gauss = Button(self.layout,'dx2 gauss',grid=(2,2))

        Button(self.layout,'Fit',connect=self.fit_data, grid=(3,0,1,4))

        Button(self.layout,'Apply',connect=self.on_apply,grid=(20,0,1,2))
        Button(self.layout,'Cancel',connect=self.on_cancel,grid=(20,2,1,2))
        
        frame.setLayout(self.layout)
        main_layout.addWidget(frame,0,0,1,2)
        
        # =============================================================================
        # Plot
        plot_frame = QFrame()
        plot_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_layout = QVBoxLayout()

        self.plot = LineCanvas()
        plot_layout.addWidget(self.plot)
        self.lines = self.plot.axes['main'].plot([None],[None],[None],[None],[None],[None])
        
        plot_frame.setLayout(plot_layout)
        main_layout.addWidget(plot_frame,0,2,2,1)
       
        # =============================================================================
        # Buttons
        self.setLayout(main_layout)

    # =============================================================================
    # Methods
    # =============================================================================
    
    @error_handler
    def refresh_parms(self):
        self.parms_panel.refresh_parms()

    def fit_data(self):
        pass
        
    def on_apply(self):
        self.accept()
    
    def on_cancel(self):
        self.reject()
        
# ---------------------------
# ENTRY POINT (Spyder-safe)
if __name__ == "__main__":
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    window = ChirpCorrectionWindow()
    window.show()

    if not QApplication.instance().startingUp():
        sys.exit(app.exec())
    else:
        app.exec()
