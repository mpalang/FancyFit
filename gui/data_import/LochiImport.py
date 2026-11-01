# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 16:26:38 2026

@author: moritzpalang

This Window is for loading data. """

import sys
from pathlib import Path
import numpy as np
from numpy import typing as npt

from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)

from PySide6.QtGui import QIcon

# from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

# Add personal modules:
if str(Path(__file__).parent.parent.parent) not in sys.path:
      sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.logger import add_logger  
from utils.auxiliary import data_class,fancyfitSettings
from utils.plotting import ContourCanvas
from gui.Elements import (Button,Spinbox,Dropdown,Label,Inputbox)

  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

def sigmoid(x):
    """Sigmoid function."""
    return 1 / (1 + np.exp(-x))

class LochiImportWindow(QDialog):
    """A window for loading data from files. It allows the user to select the type of data they want to load and provides input fields for the corresponding file paths. 
    Once the data is loaded, it emits a signal with the loaded data as three separate numpy arrays for x, y, and z."""
    
    
    def __init__(self, wl_table: npt.NDArray | None = None, ta_data: npt.NDArray | None = None):
        super().__init__()
        self.logger = add_logger(__name__)
        self.setWindowTitle("Lochbrunner Format Import")
        icon_path = Path(Path(__file__).parent,'Load_Icon.ico')
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(500, 200)

        self.wl_table = wl_table
        self.ta_data = ta_data

        self.repeats = 1

        self.pretreat_data()
        self.create_ui()
        self.make_plot()


    def pretreat_data(self):
        self.wl = self.wl_table[:,1][np.argsort(self.wl_table[:,0])]
        self.dt = self.ta_data[0,:]
        self.ta = self.ta_data[1:,:]
        self.wl = np.linspace(min(self.wl), max(self.wl), self.ta.shape[0])  # Interpolate to match the number of columns in ta_data...ask about how the data is usually presented.

        breaks = np.where(self.dt[:-1] > self.dt[1:])[0] + 1
        self.repeats = len(breaks) + 1
        dts = np.split(self.dt, breaks) 
        if not all(d.shape == dts[0].shape for d in dts):
            raise ValueError("All segments of dt must have the same shape.")

        self.dt = np.mean(np.array(dts),axis=0)

        tas = np.split(self.ta, breaks, axis=1)
        self.ta = np.nanmean(tas, axis=0)


    def create_ui(self):
        self.layout = QHBoxLayout()

        frame_parameters = QFrame()
        layout_parameters = QGridLayout()
        Label(layout_parameters, "from", grid=(0,1))
        Label(layout_parameters, "to", grid=(0,2))
        Label(layout_parameters, "wl range", grid=(1,0))
        self.wl_from_input = Inputbox(layout_parameters, default= 380, grid=(1,1))
        self.wl_to_input = Inputbox(layout_parameters, default = 850, grid=(1,2))
        Label(layout_parameters, "dt range", grid=(2,0))
        self.dt_from_input = Inputbox(layout_parameters, default=-1, grid=(2,1))
        self.dt_to_input = Inputbox(layout_parameters, default=1, grid=(2,2))
        self.update_button = Button(layout_parameters,"Update", grid=(3,0), connect=self.on_update)
        self.reset_button = Button(layout_parameters,"Reset", grid=(3,1))
        frame_parameters.setLayout(layout_parameters)
        self.layout.addWidget(frame_parameters)

        frame_plot = QFrame()
        layout_plot = QVBoxLayout()
        self.plot = ContourCanvas()
        layout_plot.addWidget(self.plot)
        frame_plot.setLayout(layout_plot)
        self.layout.addWidget(frame_plot)

        self.setLayout(self.layout)


    def make_plot(self):
       wl_from = float(self.wl_from_input.text()) if self.wl_from_input.text() else min(self.wl)
       wl_to = float(self.wl_to_input.text()) if self.wl_to_input.text() else max(self.wl)
       dt_from = float(self.dt_from_input.text()) if self.dt_from_input.text() else min(self.dt)
       dt_to = float(self.dt_to_input.text()) if self.dt_to_input.text() else max(self.dt)
       wl_mask = (self.wl >= wl_from) & (self.wl <= wl_to)
       dt_mask = (self.dt >= dt_from) & (self.dt <= dt_to)      
 
       self.plot.set_contour(self.wl[wl_mask], self.dt[dt_mask], self.ta.T[np.ix_(dt_mask, wl_mask)] , zrange=(0.999,1.001), axis_break=1)


    def on_update(self):
        self.make_plot() 
        self.plot.rescale()

    def on_reset(self):
        self.wl_from_input.setText(str(min(self.wl)))
        self.wl_to_input.setText(str(max(self.wl)))
        self.dt_from_input.setText(str(min(self.dt)))
        self.dt_to_input.setText(str(max(self.dt)))
        self.make_plot()
        self.plot.rescale()

    def on_cancel(self):
        self.reject()
        
        
        
# ---------------------------
# ENTRY POINT (Spyder-safe)
if __name__ == "__main__":
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    wl_table = np.genfromtxt(r"C:\Users\morit\OneDrive\Work\Uni-Rostock\Testdaten\WaveLengthTable.dat", delimiter='\t')
    ta_data = np.genfromtxt(r"C:\Users\morit\OneDrive\Work\Uni-Rostock\Testdaten\Coum153_eth_testmssg.dat", delimiter='\t')
    window = LochiImportWindow(wl_table=wl_table, ta_data=ta_data)
    window.show()

    if not QApplication.instance().startingUp():
        sys.exit(app.exec())
    else:
        app.exec()
