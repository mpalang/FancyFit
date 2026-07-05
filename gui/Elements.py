# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:36:40 2026

@author: moritzpalang
"""
# from curses.textpad import Textbox

from PySide6 import QtWidgets
import numpy as np
from pathlib import Path

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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from utils.logger import add_logger
logger = add_logger(__name__)

# ---------------------------
# SIMPLE PLOT WIDGET WRAPPER
# --------------------------
class Checkbox(QCheckBox):
    def __init__(self,root=None,default=True,grid=()):
        super().__init__()
        self.setChecked(default)
        if root:
            root.addWidget(self,*grid)


class Dropdown(QComboBox):
    def __init__(self,root=None,items=None,standard=None,command=lambda:None,grid=(),layout_args=()):
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
    def __init__(self,root=None,lower=0,upper=100,standard=0,layout_args=(),grid=(),expand=False):
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

class SpinboxDouble(QDoubleSpinBox):
    def __init__(self,root=None,default=0,limits=(-1e9,1e9),grid=()):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        if any(limits):
            self.setRange(*limits)
        if default:
            self.setValue(default)
        if root:
            root.addWidget(self,*grid)

class Button(QPushButton):
    def __init__(self,root=None,name='',command = lambda:None,grid=(),layout_args=(),expand=False):
        super().__init__(name)
        if grid and not layout_args:
            layout_args = grid    
        if root:
            root.addWidget(self,*layout_args)
        self.clicked.connect(command)
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
    def __init__(self, root=None, geometry=None, default='', layout_args=(), grid=()):
        super().__init__()
        if grid and not layout_args:
            layout_args = grid

        # w.setGeometry(*geometry)
        if root:
            root.addWidget(self,*layout_args)
    
class Label(QLabel):
    def __init__(self,root=None,text='', bold=False,grid=(),layout_args=()):
        super().__init__(text)
        if grid and not layout_args:
            layout_args = grid
        if bold:
            self.setStyleSheet('font-weight: bold;')
        if root:
            root.addWidget(self,*layout_args)


class Slider(QWidget):
    def __init__(
                self,
                root=None,
                value_range=(0, 100),
                command=lambda: None,
                label_format="plain",
                ):
        super().__init__()

        self.command = command
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

        if root:
            root.addWidget(self)

    def format_value(self, value):
        if self.label_format == "sci":
            return f"{value:.2e}"
        return str(value)

    def on_slide(self):
        value = self.slider.value()
        self.label.setText(self.format_value(value))
        self.command()
           


# def Slider(root,value_range=(0,100),command=lambda:None,label_format='plain'):
    
#    class slider_with_label:
#        def __init__(self,root,value_range,label_format=label_format):
#            self.command = command
#            self.label_format = label_format
#            if np.nan in value_range:
#                value_range = (0,1)
           
#            slider_layout = QHBoxLayout()
       
#            slider = QSlider(Qt.Horizontal)
#            slider.setRange(*value_range)
#            slider.setValue((value_range[0]+value_range[1])/2)
#            slider.setSingleStep(1)
#            slider_layout.addWidget(slider)
#            slider.valueChanged.connect(self.on_slide)
           
#            slider.setStyleSheet("""
#                                 QSlider::groove:horizontal {
#                                     border: none;
#                                     height: 2px;
#                                     background: gray;
#                                 }
                                
#                                 QSlider::sub-page:horizontal {
#                                     background: gray;
#                                 }
                                
#                                 QSlider::add-page:horizontal {
#                                     background: gray;
#                                 }
                                
#                                 QSlider::handle:horizontal {
#                                     background: black;
#                                     width: 5px;
#                                     margin: -6px 0;
#                                 }
                                
#                                 """)
            
            

#            label = QLabel(self.format_value(slider.value()))
           
#            self.slider = slider
#            self.label = label
           
#            self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
#            self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
           
#            slider_layout.addWidget(self.slider)
#            slider_layout.addWidget(self.label)
    
#            root.addLayout(slider_layout)
           
#        def format_value(self,number):
#          if self.label_format == "sci":
#              return f"{number:.2e}"
#          else:
#              return str(number) 
         
#        def on_slide(self):
#           self.command()
#           self.label.setText(self.format_value(self.slider.value()))
                

           
#    w = slider_with_label(root,value_range)
           
#    return w

class ParmRow(QWidget):
    def __init__(self,name,p0,p_lower,p_upper):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        layout = QHBoxLayout(self)
        self.name_input = Inputbox(layout,default=name)
        self.p0_input = Inputbox(layout,default=p0)
        self.p_lower_input = Inputbox(layout,default=p_lower)
        self.p_upper_input = Inputbox(layout,default=p_upper)
                 
        # self.p0_input.textChanged.connect(self.validate)
        # self.p_lower_input.textChanged.connect(self.validate)
        # self.p_upper_input.textChanged.connect(self.validate)
        
        
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
            self.setStyleSheet("background:#ffcccc;")
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
        
        
class ParmsPanel(QWidget):
    def __init__(self,FitFuns,fun_name=None):
        super().__init__()
        self.FitFuns = FitFuns
        self.fun_name = fun_name
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
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
        Parms_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
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
        