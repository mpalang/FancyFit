#coding: utf-8 -*-
"""
Created on Thu Jul 17 15:00:00 2026

@author: moritzpalang
"""
import traceback
import sys
from functools import wraps
from PySide6.QtWidgets import QMessageBox

import logging
from PySide6.QtWidgets import QWidget

class ErrorBox(QMessageBox):
    def __init__(self, title, message, details=None, InformativeText=None, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setWindowTitle(title)
        self.layout().setColumnMinimumWidth(1, 600)
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


def origin(exc_tb, depth=2):
    """module.function:line for the innermost frame, plus its caller(s)."""
    frames = []
    tb = exc_tb
    while tb is not None:
        frames.append(tb)
        tb = tb.tb_next

    inner = frames[-1]
    module = inner.tb_frame.f_globals.get("__name__", "?")
    chain = " <- ".join(f"{t.tb_frame.f_code.co_name}:{t.tb_lineno}"
                        for t in frames[-depth:])
    return f"{module}.{chain}"


def excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    where = origin(exc_tb)
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    owner = find_owner(exc_tb)                      # the window that raised
    logger = getattr(owner, "logger", None) or logging.getLogger(__name__)
    logger.error("%s in %s: %s", exc_type.__name__, where, exc_value,
                 exc_info=(exc_type, exc_value, exc_tb))

    ErrorBox(f"{exc_type.__name__} in {where}", str(exc_value),
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

