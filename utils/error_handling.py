#coding: utf-8 -*-
"""
Created on Thu Jul 17 15:00:00 2026

@author: moritzpalang
"""
import traceback
from functools import wraps
from PySide6.QtWidgets import QMessageBox


class ErrorBox(QMessageBox):
    def __init__(self, title, message, details=None, InformativeText=None, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setWindowTitle(title)
        self.setText(message)
        if InformativeText:
            self.setInformativeText('informativeText')
        if details:
            self.setDetailedText(details)
        self.exec()


def error_handler(func):
    """Decorator to handle exceptions in GUI Window."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0] if args else None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.exception(f"Exception in {func.__name__}: {e}")
            ErrorBox('error',f'Fatal Error in {func.__name__}:\n {e}',
                     details=traceback.format_exc(),parent=self)
    return wrapper


# def handle_exceptions(exc_type, exc_value, exc_tb):
    # logger