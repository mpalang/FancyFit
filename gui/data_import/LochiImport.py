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
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)

from PySide6.QtGui import QIcon

# Add personal modules:
if str(Path(__file__).parent.parent.parent) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.logger import add_logger  
from utils.plotting import ContourCanvas
from utils.error_handling import ErrorBox
from gui.Elements import (Button, Label, Inputbox, Dropdown)

# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class LochiImportWindow(QDialog):
    """A window for loading data from files. It allows the user to select the type of data they want to load and provides input fields for the corresponding file paths. 
    Once the data is loaded, it emits a signal with the loaded data as three separate numpy arrays for x, y, and z."""
    
    def __init__(self, wl_table: npt.NDArray | None = None, ta_data: npt.NDArray | None = None,
                 name: str | None = None, parent_folder: Path | None = None):
    
        super().__init__()
        self.logger = add_logger(__name__)
        self.setWindowTitle("Lochbrunner Format Import")
        icon_path = Path(Path(__file__).parent,'Load_Icon.ico')
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(1000, 500)

        self.name = name if name is not None else ""
        self.parent_folder = parent_folder if parent_folder is not None else Path("")

        self.repeats = 1

        self.load_data(wl_table, ta_data)
        self.pretreat_data()
        self.create_ui()
        self.make_plot()


    def load_data(self, wl_table: npt.NDArray | Path, ta_data: npt.NDArray | Path):
        """Load data from files or arrays."""
        if isinstance(wl_table, Path):
            self.wl_table = np.genfromtxt(wl_table, delimiter='\t')
            self.parent_folder = wl_table.parent
        else:
            self.wl_table = wl_table

        if isinstance(ta_data, Path):
            self.ta_data = np.genfromtxt(ta_data, delimiter='\t')
            self.name = ta_data.stem
            self.parent_folder = ta_data.parent
        else:
            self.ta_data = ta_data


    def pretreat_data(self):
        if self.wl_table is None or self.ta_data is None:
            raise ValueError("both wl_table and ta_data are required")

        self._wl = self.wl_table[:,1][np.argsort(self.wl_table[:,0])]
        self._dt = self.ta_data[0,:]
        self._ta = self.ta_data[1:,:]
        self._ta[np.where(self._ta < 0)] = np.nan  # Set negative values to NaN to protect against log10 errors  
        self.wl = np.linspace(min(self._wl), max(self._wl), self._ta.shape[0])  # Interpolate to match the number of columns in ta_data...ask about how the data is usually presented.

        breaks = np.where(self._dt[:-1] > self._dt[1:])[0] + 1
        self.repeats = len(breaks) + 1
        dts = np.split(self._dt, breaks) 
        if not all(d.shape == dts[0].shape for d in dts):
            ErrorBox("Data Error", "All segments of dt must have the same shape. Please check the input data.")
            raise ValueError("All segments of dt must have the same shape.")

        self.dt = np.mean(np.array(dts),axis=0)

        tas = np.split(self._ta, breaks, axis=1)
        self.ta = -np.log10(np.nanmean(tas, axis=0)) # correct sign?


    def create_ui(self):
        self.main_layout = QHBoxLayout()

        frame_parameters = QFrame()
        layout_parameters = QGridLayout()
        Label(layout_parameters, "Name", grid=(0,0))
        self.name_input = Inputbox(layout_parameters, default=self.name, grid=(0,1))
        Label(layout_parameters, "Folder", grid=(1,0))
        self.folder_input = Inputbox(layout_parameters, default=str(self.parent_folder), grid=(1,1))
        Label(layout_parameters, "Repeats", grid=(2,0))
        self.repeats_spinbox = Inputbox(layout_parameters, default=self.repeats, grid=(2,1))
        self.repeats_spinbox.setReadOnly(True)
        Label(layout_parameters, "Sign", grid=(3,0))
        self.sign_input = Dropdown(layout_parameters, items=['+','-'], command=self.make_plot, grid=(3,1))
        Label(layout_parameters, "time points total", grid=(4,0))
        self.number_dt_points = Inputbox(layout_parameters, default=len(self._dt), grid=(4,1))
        self.number_dt_points.setReadOnly(True)
        Label(layout_parameters, "wavelength points total", grid=(5,0))
        self.number_wl_points = Inputbox(layout_parameters, default=len(self._wl), grid=(5,1))
        self.number_wl_points.setReadOnly(True)
        self.update_button = Button(layout_parameters, "Save", connect=self.on_save, grid=(6,0))
        self.reset_button = Button(layout_parameters, "Cancel", connect=self.on_cancel, grid=(6,1))
        frame_parameters.setLayout(layout_parameters)
        self.main_layout.addWidget(frame_parameters)

        frame_plot = QFrame()
        layout_plot = QVBoxLayout()
        self.plot = ContourCanvas()
        layout_plot.addWidget(self.plot)
        frame_plot.setLayout(layout_plot)
        self.main_layout.addWidget(frame_plot)
        self.plot.set_layout("linlog")

        self.setLayout(self.main_layout)

    @property
    def sign(self):
        return 1 if self.sign_input.currentText() == '+' else -1

    def make_plot(self): 
       self.plot.set_contour(self.wl, self.dt, self.sign *self.ta.T , zrange=(-0.001,0.001), axis_break=1)


    def on_save(self):
        np.savetxt(Path(self.folder_input.text()) / f"{self.name_input.text()}_wl.csv", self.wl, delimiter=',')
        np.savetxt(Path(self.folder_input.text()) / f"{self.name_input.text()}_dt.csv", self.dt, delimiter=',')
        np.savetxt(Path(self.folder_input.text()) / f"{self.name_input.text()}_ta.csv", self.sign * self.ta, delimiter=',')   
        self.accept()


    def on_cancel(self):
        self.reject()
        
          
# ---------------------------
# ENTRY POINT (Spyder-safe)
if __name__ == "__main__":
    from utils.error_handling import excepthook
    from utils.logger import setup_logger
    setup_logger()
    sys.excepthook = excepthook


    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    # wl_table_path = Path(r"C:\Users\morit\OneDrive\Work\Uni-Rostock\Testdaten\WaveLengthTable.dat")
    # ta_data_path = Path(r"C:\Users\morit\OneDrive\Work\Uni-Rostock\Testdaten\Coum153_eth_testmssg.dat")

    window = LochiImportWindow()
    window.show()

    if not QApplication.instance().startingUp():
        sys.exit(app.exec())
    else:
        app.exec()