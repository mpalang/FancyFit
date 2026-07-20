coding: utf-8 -*-
"""
Created on Thu Jul 17 15:00:00 2026

@author: moritzpalang
"""
import traceback
from PySyde6.QtWidgets import QMessageBox

class ErrorBox(QMessageBox):
    def __init__(self, title, message, details=None,parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setWindowTitle(title)
        self.setText(message)
        self.setInformativeText('informativeText')
        if details:
            self.setDetailedText(details)
        self.exec()


def error_handler(func):
    """Decorator to handle exceptions in GUI Window."""
    @wraps
    def wrapper(*args, **kwargs):
        try:
            return func(self,*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            QMessageBox.critical(self,'error',f'Fatal Error in {func.__name__}:\n {e}',traceback.format_exc())

