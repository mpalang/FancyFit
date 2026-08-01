# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:36:40 2026

@author: moritzpalang
"""
# from curses.textpad import Textbox

from PySide6 import QtWidgets
import numpy as np
from pathlib import Path
from collections.abc import Callable

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QFrame,
    QSpinBox,
    QDoubleSpinBox,
    QSlider,
    QMessageBox,
    QTextEdit,
    QAbstractSpinBox,
    QStyle,
    QFileDialog,
)
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QSizePolicy

from utils.logger import add_logger
logger = add_logger(__name__)

from utils.error_handling import ErrorBox

# ---------------------------
# SIMPLE PLOT WIDGET WRAPPER
# --------------------------
class Checkbox(QCheckBox):
    def __init__(self,root=None,default=True,grid=(),connect=lambda:None):
        super().__init__()
        self.setChecked(default)
        if root:
            root.addWidget(self,*grid)
        if connect:
            self.stateChanged.connect(connect)

class Dropdown(QComboBox):
    def __init__(self,root=None,items=None,layout_args=(),standard=None,command=lambda:None,grid=()):
        super().__init__()
        if grid and not layout_args:
            layout_args = grid 
        if items:
            self.addItems(items)
        if standard:
            self.setCurrentText(standard)
        self.currentTextChanged.connect(command)
        root.addWidget(self,*layout_args)
  
class Spinbox(QSpinBox):
    def __init__(self,root=None,standard=0,layout_args=(),lower=0,upper=100,grid=(),expand=False,connect=lambda:None):
        super().__init__()
        if grid and not layout_args:
            layout_args = grid        
        if lower and upper:
            self.setRange(lower,upper)
        if standard:
            self.setValue(standard)
        if root:
            root.addWidget(self,*layout_args)
        if expand:
            self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
            )  
        if connect:
           self.valueChanged.connect(connect)


class SpinboxDouble(QDoubleSpinBox):
    def __init__(self,root=None,default=0,grid=(),limits=(-1e9,1e9)):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        if any(limits):
            self.setRange(*limits)
        if default:
            self.setValue(default)
        if root:
            root.addWidget(self,*grid)

class Button(QPushButton):
    def __init__(self,root=None,text='',layout_args=(),connect: Callable|None=None,grid=(),expand=False):
        super().__init__(text)
        if layout_args and not grid:
            grid = layout_args    
        if root:
            if grid:
                root.addWidget(self,*grid)
            else:
                root.addWidget(self)
        if connect:
            self.clicked.connect(connect)
        if expand:
            self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
              
            
class Inputbox(QLineEdit):
    def __init__(self,root=None,default='',layout_args=(),grid=(),expand=False):
        super().__init__()
        if grid and not layout_args:
            layout_args = grid
        if root:
            root.addWidget(self,*layout_args)
        if default:
            self.setText(str(default))
        if expand:
            self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
            )


class Textbox(QTextEdit):
    def __init__(self, root=None, default='', layout_args=(), geometry=None,  grid=()):
        super().__init__()
        if grid and not layout_args:
            layout_args = grid

        # w.setGeometry(*geometry)
        if root:
            root.addWidget(self,*layout_args)
    
    
class Label(QLabel):
    def __init__(self,root=None,text='',layout_args=(), bold=False,grid=()):
        super().__init__(text)
        if grid and not layout_args:
            layout_args = grid
        if bold:
            self.setStyleSheet('font-weight: bold;')
        if root:
            root.addWidget(self,*layout_args)


class Slider(QWidget):
    
    moved = Signal(float)
    
    def __init__(self,root=None,value_range=(0, 100), label_format="plain"):
        
        super().__init__()

        self.label_format = label_format

        layout = QHBoxLayout(self)

        self.slider = QSlider(Qt.Horizontal)
        self.label = Label(text="")

        if np.nan in value_range:
            value_range = (0, 1)

        self.slider.setRange(*value_range)
        self.slider.setValue((value_range[0] + value_range[1]) // 2)

        self.slider.valueChanged.connect(self.on_slide)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        
        self.on_slide()

        if root:
            root.addWidget(self)
            
    def set_limits(self,limits):
        self.slider.setRange(*limits)
        self.slider.setValue((limits[0] + limits[1]) // 2)

    def format_value(self, value):
        if self.label_format == "sci":
            return f"{value:.2e}"
        return str(value)

    def on_slide(self):
        value = self.slider.value()
        self.label.setText(self.format_value(value))
        self.moved.emit(value)
        
    @property
    def value(self):
        return self.slider.value()
           
       
        
def open_path(root,default_path = ''):
    class open_path_class(QWidget):
        def __init__(self,default_path=''):
            super().__init__()
            layout_folder = QHBoxLayout()
            self.entry_inputpath = QLineEdit()
            self.entry_inputpath.setText(default_path)
            layout_folder.addWidget(self.entry_inputpath)
            button_folder = QPushButton()
            button_folder.clicked.connect(self.filepath_dialog)
            button_folder.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
            layout_folder.addWidget(button_folder)
            self.setLayout(layout_folder)
            self.input_path = default_path
        
        def filepath_dialog(self):
            self.input_path = QFileDialog.getOpenFileName(self, "Select Directory", self.entry_inputpath.text())[0]
            if Path(self.input_path).exists():
                self.entry_inputpath.setText(self.input_path)
                
    w = open_path_class(default_path=default_path)
    root.addWidget(w)
    
    return w


# =============================================================================
# Parm Row Widget used in ParmsPanel and FunctionBuilder       
# =============================================================================
class ParmRow(QWidget):
    
    changed = Signal()
    _STYLE = """
        ParmRow[invalid="true"] {
                background-color: #ffe6e6;
                color: black;
                    }
        """
    
    def __init__(self,name,p0,p_lower,p_upper):
        super().__init__()
                
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        layout = QHBoxLayout(self)
        self.name_input = Inputbox(layout,default=name)
        self.p0_input = Inputbox(layout,default=str(p0))
        self.p_lower_input = Inputbox(layout,default=str(p_lower))
        self.p_upper_input = Inputbox(layout,default=str(p_upper))
        self.fix_button = Button(layout,'fix')

        self.fix_button.setCheckable(True)
        self.fix_button.setStyleSheet("""
                                        QPushButton:checked {
                                            background-color: lightgreen;
                                        }
                                    """)
                                    
        self.create_connections()
                   

    def create_connections(self):
        self.name_input.textChanged.connect(self.validate)
        self.p0_input.textChanged.connect(self.validate)
        self.p_lower_input.textChanged.connect(self.validate)
        self.p_upper_input.textChanged.connect(self.validate)
        
        
    def _set_invalid(self, invalid: bool):
        if self.property("invalid") == invalid:
            return                                       # no change, skip the repolish
        self.setProperty("invalid", invalid)
        self.style().unpolish(self)
        self.style().polish(self)
               
    
    def get_values(self):
        def get_bound(widget, default):
            text = widget.text().strip()
            return float(text) if text else default
        
        name = self.name_input.text()
        p0 = float(self.p0_input.text())

        if self.fix_button.isChecked():
            p_lower = p0
            p_upper = p0
        else:
            p_lower = get_bound(self.p_lower_input,-np.inf)
            p_upper = get_bound(self.p_upper_input,np.inf)

        return name, p0, p_lower, p_upper
        
        
    def validate(self):
        try:
            name, p0, p_lower, p_upper = self.get_values()
            if p_lower <= p0 <= p_upper:
                self.setStyleSheet("")
                return True
            else:
                self.setStyleSheet('background-color: #ffe6e6;color: black;')
                return False
        except Exception:
            self.setStyleSheet('background-color: #ffe6e6;color: black;')
            return False

    @property
    def values(self):
        if self.validate():
            return self.get_values()
        else:
            ErrorBox('Check Parameters','Please make sure parameter inputs are valid.')
            raise ValueError('Please make sure parameter inputs are valid.')
        