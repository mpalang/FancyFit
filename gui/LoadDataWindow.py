# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 16:26:38 2026

@author: moritzpalang

This Window is for loading data. """

import sys
from pathlib import Path
import numpy as np

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
if str(Path(__file__).parent.parent) not in sys.path:
      sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import add_logger  
from utils.auxiliary import data_class,fancyfitSettings
from gui.Elements import (Button,Dropdown,Label,open_path,)

  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class LoadDataWindow(QDialog):
    
    data_loaded = Signal(object)
    
    def __init__(self,settings=None,no_comps=1):
        super().__init__()
        self.logger = add_logger(__name__)
        self.setWindowTitle("Load Data")
        icon_path = Path(Path(__file__).parent,'Load_Icon.ico')
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(500, 200)
        
        self.no_comps = no_comps
        
        if not settings:
            self.set = fancyfitSettings()
        else:
            self.set = settings
        
        self.create_ui()


    def create_ui(self):
        
        self.layout = QVBoxLayout()
        self.data_type_dropdown = Dropdown(self.layout, ['Multiple Files','Lochi', 'One File'], command = self.on_data_type_change)

        self.input_fields = self.create_files_input()
        self.layout.addWidget(self.input_fields)
    
        frame_action = QFrame()
        layout_action = QHBoxLayout()
        Button(layout_action,'Load',connect=self.on_load)
        Button(layout_action,'Cancel',connect=self.on_cancel)
        frame_action.setLayout(layout_action)
        self.layout.addWidget(frame_action)
        
        self.setLayout(self.layout)


    def on_data_type_change(self):
        # Get index of input widget
        index = self.layout.indexOf(self.input_fields)

        # Remove the old input fields
        self.layout.removeWidget(self.input_fields)
        self.input_fields.deleteLater()

        # Create new input fields based on the selected data type
        self.input_fields = self.create_files_input()
        self.layout.insertWidget(index,self.input_fields)


    def create_files_input(self):
        data_type = self.data_type_dropdown.currentText()
        if data_type == 'Multiple Files':
            return self.create_multiple_files_input()
        elif data_type == 'Lochi':
            return self.create_lochi_input()
        elif data_type == 'One File':
            return self.create_one_file_input()
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        

    def create_multiple_files_input(self):
        widget = QWidget()
        layout = QVBoxLayout()
        Label(layout,'x data',bold=True)
        self.x_path = open_path(layout,default_path=self.set.x_data_path)
        Label(layout,'y data',bold=True)
        self.y_path = open_path(layout,default_path=self.set.y_data_path)
        Label(layout,'Z data',bold=True)
        self.z_path = open_path(layout,default_path=self.set.z_data_path)

        widget.setLayout(layout)
        return widget


    def create_lochi_input(self):
        widget = QWidget()
        layout = QVBoxLayout()
        Label(layout,'WL Table',bold=True)
        self.x_path = open_path(layout,default_path=self.set.x_data_path)
        Label(layout,'TA Data',bold=True)
        self.y_path = open_path(layout,default_path=self.set.y_data_path)
        Label(layout,'Pump Spectra',bold=True)
        self.z_path = open_path(layout,default_path=self.set.z_data_path)

        widget.setLayout(layout)
        return widget


    def create_one_file_input(self):
        widget = QWidget()
        layout = QVBoxLayout()
        Label(layout,'Data Path',bold=True)
        self.data_path = open_path(layout,default_path=self.set.x_data_path)
        widget.setLayout(layout)
        return widget


    def on_load(self):
        data_type = self.data_type_dropdown.currentText()

        if data_type == 'Multiple Files':
            x_path = self.x_path.entry_inputpath.text()
            y_path = self.y_path.entry_inputpath.text()
            z_path = self.z_path.entry_inputpath.text()
        
            x = np.genfromtxt(x_path)
            y = np.genfromtxt(y_path)
            z = np.genfromtxt(z_path)        

        elif data_type == 'lochi':
            pass

        #Update User path for next time
        self.set.x_data_path = x_path
        self.set.y_data_path = y_path
        self.set.z_data_path = z_path
        self.set.save()
        
        self.data = data_class(x=x,y=y,z=z)
        self.data_loaded.emit(self.data)
        self.accept()

    
    def on_cancel(self):
        self.reject()
        
        
        
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
