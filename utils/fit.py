# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 13:57:37 2026

@author: morit
"""
try:
    from fittoolkit import GlobalFit
except:
    raise RuntimeError('fittoolkit not installed')

from PySide6.QtCore import QObject, Signal, Slot

class GlobalFitWorker(QObject):

    progress = Signal(object)
    finished = Signal(object)

    def __init__(self, x,y,z, settings):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.settings = settings

    @Slot()
    def run(self):
        result = GlobalFit(
            self.x, self.y, self.z, 
            settings = self.settings,
            callback=self.progress.emit
        )

        self.finished.emit(result)