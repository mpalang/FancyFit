# -*- coding: utf-8 -*-
"""
Created on Sun 7 June 14:27:42 2026

@author: moritzpalang
"""
        
import sys
from pathlib import Path
import numpy as np
from time import perf_counter as pc
from datetime import datetime
from matplotlib import pyplot as plt

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    # QGridLayout,
    QLabel,
    QFrame,
    # QTabWidget,
    # QMessageBox,
    # QTextEdit,
)
from PySide6.QtGui import QFont, QIcon

from PySide6.QtGui import QAction
from PySide6.QtCore import QThread

if __name__ == "__main__":
    if str(Path(__file__).parent.parent) not in sys.path:
        sys.path.append(str(Path(__file__).parent.parent))

# Add personal modules:
from gui.Elements import Button

from gui import __version__
from utils.logger import add_logger
from utils.auxiliary import fancyfitSettings, FitFunctions, data_class

from utils.fit import GlobalFitWorker
from utils.error_handling import error_handler,ErrorBox

from gui.panels.main_window_panels import (DataTweakPanel,FitSettingsPanel,
                                        FunctionsInputPanel, PlotPanel,ResultsPanel)

  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
        
class MainWindow(QMainWindow):
    """This is the main Window for FancyFit."""
    
    use_test_data = True
    
    @error_handler
    def __init__(self):
        super().__init__()
        self.logger = add_logger(__name__)
        self.setWindowTitle(f"Smore's Fancy Fit App v{__version__}")
        icon_path = Path(Path(__file__).parent,'MainIcon.ico')
        self.setWindowIcon(QIcon(str(icon_path)))
        
        #Geometrics
        self.resize(1300, 500)
        # screen = QApplication.primaryScreen().availableGeometry()
        # window = self.frameGeometry()
        # window.moveCenter(screen.center())
        self.move(100,50)
        
        #Load and initialize
        self.load_settings()
        self.initialize_data()
        
        self.create_ui()
        
        if self.use_test_data:
            self.dtp.set_limits((min(self.data.x),max(self.data.x)),
                                (min(self.data.y),max(self.data.y)))
            self.make_plots()
        
        #Welcome Text
        self.rsp.setText('Ready for the first fit! The better the boundaries and initial guesses, the better the fit results might be!')

    
    # =============================================================================
    # Assemble UI:
    # =============================================================================
    @error_handler
    def create_ui(self):
        self.main_layout = QHBoxLayout()
        
        self.create_menu()

        self.create_left_panel()
        self.create_plot_panel()     
        self.create_results_panel()

        self.create_status_bar()
        
        # ---------------------------
        # CENTRAL WIDGET
        central = QWidget()
        self.setCentralWidget(central)
        central.setLayout(self.main_layout)

    
    # =============================================================================
    # create UI elements: 
    # =============================================================================
    def create_menu(self):
        menu = self.menuBar()
        
        #Fiel Menu
        file_menu = menu.addMenu("File")
        
        load_action = QAction("Load Data", self)
        save_action = QAction("Save Results", self)
        exit_action = QAction("Exit", self)
        
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        load_action.triggered.connect(self.open_load_data)
        save_action.triggered.connect(self.save_results)
        exit_action.triggered.connect(self.exit_app)
        
        #Settings Menu
        settings_menu = menu.addMenu("Settings")      
        
        preferences_action = QAction("User Settings", self)
        functionbuilder_action = QAction("Function Builder", self)
        
        settings_menu.addAction(preferences_action)
        settings_menu.addAction(functionbuilder_action)
        
        preferences_action.triggered.connect(self.open_settings)
        functionbuilder_action.triggered.connect(self.open_functionbuilder)


    def create_status_bar(self):
        self.status_label1 = QLabel("no data")
        self.status_label2 = QLabel("no fit")
        
        self.statusBar().addPermanentWidget(self.status_label1)
        self.statusBar().addPermanentWidget(self.status_label2)
        
        self.statusBar().showMessage('Ready...')
      
        
    def create_left_panel(self):
        frame = QFrame()
        # frame_left_panel.setFrameShape(QFrame.StyledPanel)
        # frame_left_panel.setFrameShadow(QFrame.Raised)
        
        layout = QVBoxLayout(frame)

        self.dtp = DataTweakPanel()
        self.fsp = FitSettingsPanel(defaults={'method':self.set.default_method})
        self.fip = FunctionsInputPanel(defaults=self.set.default_funs)
        
        layout.addWidget(self.dtp)
        layout.addWidget(self.fsp)
        layout.addWidget(self.fip)

        #Execute Layout:
        layout_execute = QHBoxLayout()
        Button(layout_execute,'Start Fit', connect=self.execute_global_fit)
        Button(layout_execute,'Stop')
        layout.addLayout(layout_execute)
        
        # add to main layout
        self.main_layout.addWidget(frame,1)
        
        # connect
        self.dtp.cut_requested.connect(self.cut_data)
        self.dtp.uncut_requested.connect(self.uncut_data)
        
        
    def create_plot_panel(self):
        self.plp = PlotPanel(plot_style=self.set.plot_style)
        self.main_layout.addWidget(self.plp)
        
        
    def create_results_panel(self):
        self.rsp = ResultsPanel()
        self.main_layout.addWidget(self.rsp,1)
        

    def exit_app(self):
        self.logger.info('Closing Main Window')
        self.close()
        
        
    # =============================================================================
    # Methods:
    # =============================================================================
    def load_settings(self):
        self.set = fancyfitSettings()
        plt.rcParams.update({'font.size':12})  

        self.FitFuns = FitFunctions()#Replace old FitFuns with new sympy method

    
    @error_handler
    def initialize_data(self):
        if self.use_test_data:
            self.data = data_class(TestData=True)
        else:
            self.data = data_class()


    @error_handler
    def open_load_data(self):
        self.statusBar().showMessage('Loading Data...')
        from gui.LoadDataWindow import LoadDataWindow
        ldw = LoadDataWindow(no_comps=self.fip.no_comps)
        if not ldw.exec():
            raise RuntimeError('Error loading Data.')
        
        self.data = ldw.data   
        self.dtp.set_limits((min(self.data.x),max(self.data.x)),
                            (min(self.data.y),max(self.data.y)))
        self.make_plots()

    
    @error_handler
    def cut_data(self):
        self.data.cut_data(*self.dtp.x_limits,*self.dtp.y_limits)
        self.plp.make_plots(self.data)
    
    
    @error_handler
    def uncut_data(self):
        pass
    
    
    # @error_handler
    def make_plots(self):        
        self.plp.make_plots(self.data)
        self.plp.rescale()
        self.plp.set_labels(self.set.x_name,self.set.x_label,self.set.x_unit,
                            self.set.y_name,self.set.y_label,self.set.y_unit,
                            self.set.z_label,self.set.z_unit)
        
        self.status_label1.setText(f'Data Loaded: {len(self.data.x)} x points, {len(self.data.y)} y points and {str(self.data.z.shape).replace(',','x')} z points')
        

    def open_settings(self):
        from gui.SettingsWindow import SettingsWindow
        sw = SettingsWindow(settings=self.set)
        if sw.exec():
            self.set = sw.settings
            self.set.save()

        self.statusBar().showMessage('settings updated')
        
    
    @error_handler
    def open_functionbuilder(self):
        from gui.FunctionBuilder import FunctionBuilder
        fbw = FunctionBuilder()
        if fbw.exec():
            self.statusBar().showMessage('Function added',2000)             
          
    
    def save_results(self):
        self.statusBar().showMessage('saving results')
        folder = Path(self.set.z_data_path).parent
        filename = Path(self.set.z_data_path).stem+'_fit_results.txt'
        filepath = folder/filename
        with open(filepath,'w') as f:
            f.write(self.results_box.toPlainText())
        
    
    # =============================================================================
    # Fit Functions and Classes:
    # =============================================================================
    @error_handler   
    def prepare_fit(self):
        # Prepare data and settings for global fit
        data = self.data
        irf_index = self.fip.irf_index
        Fun_Objs = self.fip.Fit_Funs
        IRF = self.fip.IRF

        funs = [fun_obj.func for fun_obj in Fun_Objs]
        parms =[fun_obj.parm_names for fun_obj in Fun_Objs]
        p0 = [fun_obj.p0 for fun_obj in Fun_Objs]
        pl = [fun_obj.p_lower for fun_obj in Fun_Objs]
        pu = [fun_obj.p_upper for fun_obj in Fun_Objs]
        cp = self.fip.common_parms

        # Prepare settings for global fit
        settings={
                'funs': funs,
                'parms': parms,
                'p0': p0,
                'p_lower': pl,
                'p_upper': pu,
                'common_parms': cp,
                'method': self.fsp.method,
                'iterations': self.set.fit_iterations,
                 }
        
        return data.x, data.y, data.z.T, settings
    
    
    @error_handler
    def execute_global_fit(self):
            self.statusBar().showMessage('Executing Global Fit...')
            
            x,y,z,settings = self.prepare_fit()

            self.thread = QThread()
            self.worker = GlobalFitWorker(
                x,y,z,settings=settings)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.progress.connect(
                self.update_fit_progress
            )
            self.worker.finished.connect(
                self.fit_finished
            )
            
            self.thread.start()
            
            
    @error_handler
    def update_fit_progress(self,progress):
        if isinstance(progress,str):
            self.statusBar().showMessage(f'Executing Global Fit: {progress}')
            
        elif type(progress).__name__=='FitProgress':
            #progress is in type of fitpgrogress class with attributes chi2, parameters, iteration, total_iterations
            report = f'Iter.{progress.iteration+1}/{progress.total_iterations} with chi2={progress.chi2:.3g}'
            self.statusBar().showMessage(f'Executing Global Fit: {report}')
    
    
    @error_handler
    def update_results(self):
            p_dict = self.gf.p_dict
            errors = np.array(self.gf.m.errors)/np.array(self.gf.scaling_factors)
            m = self.gf.m
            
            fun_names = [self.fip.parm_tabs.widget(n).fun_input.currentText() for n in range(self.fip.parm_tabs.count())]
            funs_text = '; '.join([f'fun{n+1}: '+i for n,i in enumerate(fun_names)])
            params_text = "\n".join(
                f"{parm:<8s} = {p_dict[parm]:>12.2g}"#± {errors[parm]*scf[parm]:>12.2g } #TODO include errors in the report
                for parm in p_dict.keys())

            fmin_text = (
                    f"FCN (min value): {m.fval:.6g}\n"
                    f"EDM: {m.fmin.edm:.3e}\n"
                    f"Valid minimum: {m.fmin.is_valid}\n"
                    f"Converged: {m.valid}\n"
                )
            report = (
                "====================\n"
                f"|| FIT RESULTS {datetime.now().strftime('%H:%M')} ||\n"
                "====================\n\n"
                f"{funs_text}\n"
                "Parameters:\n"
                f"{params_text}\n\n"
                "=== FMIN INFO ===\n"
                f"{fmin_text}"
                )
            
            self.rsp.appendText(report)
    
    
    @error_handler
    def fit_finished(self,result):
        self.gf = result
        self.thread.quit()
        self.thread.wait()
    
        # Unpack results. gf is added in self.fit_finished after thread is done.
        self.data.x_fit = self.gf.x
        self.data.y_fit = self.gf.y
        self.data.z_fit = self.gf.Z_fit.T
        self.data.DADS = self.gf.DADS.T
        self.data.residuum = self.gf.residuum.T
        
        # Make Plots
        self.make_plots()

        # Print Results in Prompt Box
        self.update_results()
        self.statusBar().showMessage('Fit finished',5000)
        self.status_label2.setText('global fit')
        self.statusBar().showMessage('Ready...',0)
    
    
# ---------------------------
# ENTRY POINT (Spyder-safe)
# ---------------------------
if __name__ == "__main__":
    
    # Create QApplication only once
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    
    app.exec()