# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 13:57:37 2026

@author: moritzpalang
"""
try:
    from fittoolkit import GlobalFit
except:
    raise RuntimeError('fittoolkit not installed')

import traceback
from unittest import result

from PySide6.QtCore import QObject, Signal, Slot

class GlobalFitWorker(QObject):

    error = Signal(tuple)
    progress = Signal(object)
    result = Signal(object)
    finished = Signal()

    def __init__(self,data,funs,parms,bounds,settings):
        super().__init__()
        self.x = data.x
        self.y = data.y
        self.z = data.z.T
        self.funs = funs
        self.parms = parms
        self.bounds = bounds
        self.settings = settings

    @Slot()
    def run(self):
        try:
            result = GlobalFit(
                    self.x, self.y, self.z, 
                    self.funs, self.parms, self.bounds,
                    settings = self.settings,
                    callback=self.progress.emit)
            self.result.emit(result)
        except Exception as e:
            error_msg = str(traceback.format_exc())
            self.error.emit((e,error_msg))
        finally:
            self.finished.emit()     


