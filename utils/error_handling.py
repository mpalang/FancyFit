#coding: utf-8 -*-
"""
Created on Thu Jul 17 15:00:00 2026

@author: moritzpalang
"""
import traceback
import sys
from functools import wraps
from PySide6.QtWidgets import QMessageBox

import sys, logging, traceback
from PySide6.QtWidgets import QApplication, QWidget


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


def find_owner(exc_tb, attr="logger"):
    """Walk the traceback innermost-first; return the nearest `self` carrying `attr`."""
    frames = []
    tb = exc_tb
    while tb is not None:
        frames.append(tb.tb_frame)
        tb = tb.tb_next
    try:
        for frame in reversed(frames):
            obj = frame.f_locals.get("self")
            if isinstance(obj, QWidget) and hasattr(obj, attr):
                return obj
    finally:
        del frames                                   # avoid reference cycles
    return None


def excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    owner = find_owner(exc_tb)
    logger = getattr(owner, "logger", None) or logging.getLogger(__name__)
    frame = traceback.extract_tb(exc_tb)[-1]
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    logger.error("Exception in %s: %s", frame.name, exc_value,
                 exc_info=(exc_type, exc_value, exc_tb))

    ErrorBox("error", f"Error in {frame.name}:\n {exc_value}",
             details=text, parent=owner)



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