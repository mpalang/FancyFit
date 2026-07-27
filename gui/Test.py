# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:15:40 2026

@author: morit
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit)

# Add personal modules:
if str(Path(__file__).parent.parent) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent))
from widgets.main_window_widgets import DataTweakPanel


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
        self.dtw = DataTweakPanel()
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)  # Prevent user editing
        
    def create_layout(self):
        self.layout.addWidget(self.dtw)
        self.layout.addWidget(self.output)
        
    def create_connections(self):
        self.dtw.cut_requested.connect(self.cut_data)
        self.dtw.uncut_requested.connect(self.uncut_data)
        
    def cut_data(self):
        self.output.setPlainText(f'xlim:{self.dtw.x_limits}\n ylim: {self.dtw.y_limits}')
        
    def uncut_data(self):
        self.output.setPlainText(f'Reinstating full dataset.')
    

        
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