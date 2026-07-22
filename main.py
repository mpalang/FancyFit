# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:18:39 2026

@author: moritzpalang
"""
import sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Personal modules
from utils.logger import setup_logger, add_logger
from gui.MainWindow import MainWindow   

if __name__=='__main__':
    QCoreApplication.setOrganizationName("SmoereApps")
    QCoreApplication.setApplicationName("FancyFit")
    setup_logger()   
    logger = add_logger(__name__)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    if Path('utils/theme.qss').exists():
        with open(Path('utils/theme.qss'), "r") as f:
            app.setStyleSheet(f.read())
    
    icon_path = Path(Path(__file__).parent,'icon.ico')
    app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.show()

    sys.exit(app.exec())
