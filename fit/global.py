# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 13:57:37 2026

@author: morit
"""
try:
    from fittoolkit import global_fit
except:
    raise RuntimeError('fittoolkit not installed')

from PySide6.QtCore import QObject, Signal, Slot

class FitWorker(QObject):

    progress = Signal(object)
    finished = Signal(object)

    def __init__(self, data, params):
        super().__init__()
        self.data = data
        self.params = params

    @Slot()
    def run(self):
        result = global_fit(
            self.data,
            self.params,
            callback=self.progress.emit
        )

        self.finished.emit(result)