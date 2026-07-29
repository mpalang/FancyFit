# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:15:40 2026

@author: morit
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QPushButton,
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit)

path = str(Path(__file__).parent.parent)
if path not in sys.path:
    sys.path.insert(0, path)
from gui.Elements import ParmRow,Button

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        central = QWidget()
        self.setCentralWidget(central)
        central.setLayout(self.layout)
        
        
    def create_widgets(self):
        self.pr = ParmRow('a',0,-1,1)
        
        self.button = QPushButton()
        self.button.setText('click')
        

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)  # Prevent user editing
        
    def create_layout(self):
        self.layout.addWidget(self.pr)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output)
        
    def create_connections(self):
        self.button.clicked.connect(self._output)
        
    def _output(self):
        v = self.pr.values
        self.output.setPlainText(f"""
                                 name:{v[0]} | {type(v[0])}
                                 p0:{v[1]} | {type(v[1])}
                                 lower:{v[2]} | {type(v[2])}
                                 upper:{v[3]} | {type(v[3])}
                                 """)
        
    

        
# ---------------------------
# ENTRY POINT (Spyder-safe)
# ---------------------------
if __name__ == "__main__":
    
    # Create QApplication only once
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = Window()
    window.show()
    
    app.exec()