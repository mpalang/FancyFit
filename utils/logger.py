	# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:24:58 2026

@author: morit
"""
from PySide6.QtCore import QStandardPaths
from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path

class MaxLevelFilter(logging.Filter):
    """Allows only records below a certain level."""
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno < self.max_level

def setup_logger():
    user_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation),'logs')
    user_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    if root.handlers:
        root.handlers.clear()
    
    root.setLevel(logging.DEBUG)
    # -------------------------
    # Full log (everything)
    # -------------------------
    app_handler = RotatingFileHandler(
        Path(user_dir,"app.log"),
        maxBytes=1_000_000,
        backupCount=3
    )
    app_handler.setLevel(logging.INFO)
    app_handler.addFilter(MaxLevelFilter(logging.ERROR))

    # -------------------------
    # Error log (errors only)
    # -------------------------
    error_handler = RotatingFileHandler(
        Path(user_dir,"error.log"),
        maxBytes=1_000_000,
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)

    # -------------------------
    # Formatting
    # -------------------------
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    )

    app_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # -------------------------
    # Attach handlers
    # -------------------------
    root.addHandler(app_handler)
    root.addHandler(error_handler)
    
def add_logger(name):
    # if name not in logging.root.manager.loggerDict.keys():
    return logging.getLogger(name)
