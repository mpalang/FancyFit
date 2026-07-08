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
    QFileDialog,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QTabWidget,
    QMessageBox,
    QTextEdit,
)
from PySide6.QtGui import QFont, QIcon

from PySide6.QtGui import QAction
# from PySide6.QtCore import Qt

# Add personal modules:
from gui.Elements import (Button,Slider,Dropdown,Inputbox,Label,ParmsPanel)

from gui import __version__
from utils.logger import add_logger
from utils.auxiliary import fancyfitSettings, FitFunctions, data_class
from utils.plotting import LineCanvas,ContourCanvas
logger = add_logger(__name__)
import traceback
  
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
        
class MainWindow(QMainWindow):
    def __init__(self):
     try:
        super().__init__()
        self.setWindowTitle(f"Smore's Fancy Fit App v{__version__}")
        self.resize(1200, 500)
        self.load_settings()
        self.initialize_data()
        self.build_gui()
        
        self.results_box.setText('Ready for the first fit! The better the boundaries and initial guesses, the better the fit results might be!')
    
     except Exception as e:
         logger.error(traceback.format_exc())
         QMessageBox.critical(self,'error',f'Fatal Error in {__name__}:\n {e}')

# =============================================================================
# Functions:
# =============================================================================
    
    # =============================================================================
    # GUI Functions:
    # =============================================================================
    def build_gui(self):
        # ---------------------------
        # MENU BAR
        self.build_menu()
        # ---------------------------
        # CENTRAL WIDGET
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout()
        central.setLayout(self.main_layout)
        
        # =============================================================================
        # build panels
        # =============================================================================
        self.build_left_panel()
        self.build_plot_panel()     
        self.build_results_panel()
        
        # # ---------------------------
        # # TOOLBAR
        # # ---------------------------
        # toolbar = self.addToolBar("Main")
        # toolbar.addAction("Run Fit")
        # toolbar.addAction("Save Plot")
       
        # ---------------------------
        # STATUS BAR
        # ---------------------------
        self.status_label1 = QLabel("no data")
        self.status_label2 = QLabel("no fit")
        self.statusBar().addPermanentWidget(self.status_label1)
        self.statusBar().addPermanentWidget(self.status_label2)
        self.statusBar().showMessage('Ready...')
        
    def build_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        load_action = QAction("Load Data", self)
        save_action = QAction("Save Results", self)
        exit_action = QAction("Exit", self)
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        load_action.triggered.connect(self.open_filedialog)
        save_action.triggered.connect(self.save_results)
        exit_action.triggered.connect(self.exit_app)

        settings_menu = menu.addMenu("Settings")        
        preferences_action = QAction("User Settings", self)
        functionbuilder_action = QAction("Function Builder", self)
        reset_user_action = QAction("Reset to User", self)
        reset_action = QAction("Reset to Defaults", self)
        settings_menu.addAction(preferences_action)
        settings_menu.addAction(functionbuilder_action)
        settings_menu.addAction(reset_user_action)
        settings_menu.addAction(reset_action)
        preferences_action.triggered.connect(self.open_settings)
        functionbuilder_action.triggered.connect(self.open_functionbuilder)
        reset_user_action.triggered.connect(self.reset_user_defaults)
        reset_action.triggered.connect(self.restore_defaults)

    
    def build_left_panel(self):
        frame_left_panel = QFrame()
        frame_left_panel.setFrameShape(QFrame.StyledPanel)
        frame_left_panel.setFrameShadow(QFrame.Raised)
        self.left_panel = QVBoxLayout()

        # Data Tweak
        frame_datatweak = QFrame()
        frame_datatweak.setFrameShape(QFrame.StyledPanel)
        frame_datatweak.setFrameShadow(QFrame.Raised)
        layout_datatweak = QGridLayout()
        layout_datatweak.addWidget(QLabel("Set Ranges"), 0, 0)
        Button(layout_datatweak,'cut data',command = self.cut_data, layout_args = (0, 1))
        Button(layout_datatweak,'full data',command = self.full_data, layout_args = (0, 2))
        layout_datatweak.addWidget(QLabel(self.set.x_label), 1, 0)
        self.xcut_low = Inputbox(layout_datatweak,default='',layout_args= (1, 1))#TODO: replace with SpinboxDouble
        self.xcut_high = Inputbox(layout_datatweak,default='',layout_args= (1,2))
        layout_datatweak.addWidget(QLabel(self.set.y_label), 2, 0)
        self.ycut_low = Inputbox(layout_datatweak,default='',layout_args= (2,1))
        self.ycut_high = Inputbox(layout_datatweak,default='',layout_args= (2,2))

        frame_datatweak.setLayout(layout_datatweak)
        self.left_panel.addWidget(frame_datatweak)
        
        # Fit Settings
        frame_fitsettings = QFrame()
        frame_fitsettings.setFrameShape(QFrame.StyledPanel)
        frame_fitsettings.setFrameShadow(QFrame.Raised)
        layout_fitsettings = QGridLayout()
        Label(layout_fitsettings,'Mode',layout_args=(0,0))
        Dropdown(layout_fitsettings,['Global','Simple'],layout_args=(0,1))
        Label(layout_fitsettings,'Method',layout_args=(1,0))
        Dropdown(layout_fitsettings,['iminuit','others...'],layout_args=(1,1))

        frame_fitsettings.setLayout(layout_fitsettings)
        self.left_panel.addWidget(frame_fitsettings)
        
        # Parameters
        self.left_panel.addWidget(QLabel("Parameters"))
        
        layout_common_parms_and_add_comp = QGridLayout()
        # self.left_panel.addWidget(QLabel("Common Param"))
        Label(layout_common_parms_and_add_comp,'Common Parms.',layout_args=(0,0))
        self.common_parms_input = Inputbox(layout_common_parms_and_add_comp,layout_args=(1,0,1,1))
        Button(layout_common_parms_and_add_comp,'add component',command=lambda :self.build_parm_panel(),layout_args=(0,1))
        Button(layout_common_parms_and_add_comp,'remove component',command=lambda :self.remove_parm_panel(),layout_args=(1,1))
        self.left_panel.addLayout(layout_common_parms_and_add_comp)
        
        self.layout_functions = QVBoxLayout()
        self.parm_tabs = QTabWidget()
        self.parm_tabs.setFixedSize(250, 300)

        for f in self.set.default_funs:
            self.build_parm_panel(fun_name=f)     
        if self.set.use_irf:
            self.build_parm_panel(fun_name='gauss',tab_name='IRF')
        self.layout_functions.addWidget(self.parm_tabs)
        self.left_panel.addLayout(self.layout_functions)   
        
        #Execute Layout:
        layout_execute = QHBoxLayout()
        Button(layout_execute,'Start Fit',command = self.execute_global_fit)
        Button(layout_execute,'Stop')
        self.left_panel.addLayout(layout_execute)
        
        # add to main layout
        frame_left_panel.setLayout(self.left_panel)
        self.main_layout.addWidget(frame_left_panel,1)
        
        
    def build_parm_panel(self,fun_name='exp_decay',tab_name=None):  
            if not tab_name:
                tab_name = 'fun'+str(self.parm_tabs.count()+1)
            self.FitFuns = FitFunctions()          
            tab = ParmsPanel(self.FitFuns,fun_name=fun_name)
            self.parm_tabs.addTab(tab,tab_name)
            self.relabel_tabs()
            self.update_common_parms(self.FitFuns.funs[fun_name].common_parms)
    
    def remove_parm_panel(self):
        if self.parm_tabs.count()>1:
            widget = self.parm_tabs.currentWidget()
            index = self.parm_tabs.indexOf(widget)
        
            if index != -1:#-1 is returned if widget not found.
                self.parm_tabs.removeTab(index)
                widget.deleteLater()
                self.relabel_tabs()
        else:
            QMessageBox.warning(self,'Not so fast!',"Can't remove all components")
    
    def relabel_tabs(self):
        for i in range(self.parm_tabs.count()):
            if not 'IRF' in self.parm_tabs.tabText(i):
                self.parm_tabs.setTabText(i, f"fun{i+1}")
        
    def build_plot_panel(self):
        plot_tabs = QTabWidget()
        
        tab_2D = QWidget()
        
        layout_2D = QVBoxLayout()

        layout_2D.setContentsMargins(0, 0, 0, 0)
        layout_2D.setSpacing(5)
        
        figsize_2D = (18,9)
        
        self.plot_kin = LineCanvas(figsize=figsize_2D)
        layout_2D.addWidget(self.plot_kin)
        
        slider_layout1 = QHBoxLayout()
        self.slider1 = Slider(slider_layout1,command=self.make_plot_kin,label_format='plain')
        self.rescale_button1 = Button(slider_layout1,'rescale',command = self.rescale_plot_kin)
        layout_2D.addLayout(slider_layout1)

        self.plot_spec = LineCanvas(figsize=figsize_2D)
        layout_2D.addWidget(self.plot_spec)
        
        slider_layout2 = QHBoxLayout()
        self.slider2 = Slider(slider_layout2,command=self.make_plot_spec,label_format='sci')
        self.rescale_button2 = Button(slider_layout2,'rescale',command = self.rescale_plot_spec)
        layout_2D.addLayout(slider_layout2)
        
        tab_2D.setLayout(layout_2D)
        plot_tabs.addTab(tab_2D,'2D plots')
        
        tab_3D = QWidget()
        layout_3D = QGridLayout()
        figsize_3D=(9,9)

        self.plot3D_Z = ContourCanvas(figsize=figsize_3D,layout='split')
        layout_3D.addWidget(self.plot3D_Z,0,0)
        
        self.plot3D_Zfit = ContourCanvas(figsize=figsize_3D,layout='split')
        layout_3D.addWidget(self.plot3D_Zfit,0,1)
        
        self.plot3D_res = ContourCanvas(figsize=figsize_3D,layout='split')
        layout_3D.addWidget(self.plot3D_res,1,0)
        
        self.plot3D_DADS = LineCanvas(figsize=figsize_3D)
        layout_3D.addWidget(self.plot3D_DADS,1,1)
        
        layout_3D.setRowStretch(0, 1)
        layout_3D.setRowStretch(1, 1)
        layout_3D.setColumnStretch(0, 1)
        layout_3D.setColumnStretch(1, 1)
        tab_3D.setLayout(layout_3D)
        plot_tabs.addTab(tab_3D,'3D plots')
        
        self.main_layout.addWidget(plot_tabs, 3)
        
        self.set_labels()


    def build_results_panel(self):
        
        results_panel = QVBoxLayout()
        Label(results_panel,'Results')
        self.results_box = QTextEdit(self)
        self.results_box.setFixedWidth(300)
        self.results_box.setReadOnly(True)
        self.results_box.setFont(QFont("Courier New"))
        results_panel.addWidget(self.results_box)

        Button(results_panel,'Copy Results to p0')
        
        self.main_layout.addLayout(results_panel,1)
        

    # =============================================================================
    # aux gui functions        

    def update_common_parms(self,new_common_parms=['']):
        common_parms = self.common_parms_input.text().split(',')
        for new_common_parm in new_common_parms:
            if new_common_parm not in common_parms:
                common_parms.append(new_common_parm)
                common_parms = [v for v in common_parms if v!='' and v!=' ']
        self.common_parms_input.setText((','.join(common_parms)))
       
    def remove_component(self):
        if self.parm_tabs.count()>1:
            index = self.parm_tabs.currentIndex()
            widget = self.parm_tabs.widget(index)
            self.parm_tabs.removeTab(index)
            self.funs_input.pop(index)
            widget.deleteLater()
            
            for n in range(self.parm_tabs.count()):
                self.parm_tabs.setTabText(n,'fun'+str(n+1))
                
        else:
            QMessageBox.warning(self,"Cannot close tab","Can't remove last component...")
            

    def update_results(self):
            p_dict = self.gf.p_dict
            errors = self.gf.m.errors
            scf = self.gf.scaling_factors
            m = self.gf.m
            
            fun_names = [self.parm_tabs.widget(n).fun_input.currentText() for n in range(self.parm_tabs.count())]
            funs_text = '; '.join([f'fun{n+1}: '+i for n,i in enumerate(fun_names)])
            params_text = "\n".join(
                f"{parm:<8s} = {p_dict[parm]:>12.2g} ± {errors[parm]*scf[parm]:>12.2g}"
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
            
            self.results_box.append(report)
            self.results_box.verticalScrollBar().setValue(
            self.results_box.verticalScrollBar().maximum()
            )
            
            
    def exit_app(self):
        logger.info('Closing Main Window')
        self.close()
        
        

    #%% =============================================================================
    # Data and Settings Functions:
    # =============================================================================
    def initialize_data(self):
        self.data = data_class(Empty=True)
        self.funs_input = []
        self.parms_input = []
        self.p0_input = []
        self.p_lower_input = []
        self.p_upper_input = []

    def load_settings(self):
        self.set = fancyfitSettings()
        plt.rcParams.update({'font.size':12})  

        self.FitFuns = FitFunctions()#Replace old FitFuns with new sympy method
            
    def load_data(self, data: data_class=None ,use_test_data=False):
        self.statusBar().showMessage('Loading Data...')
        try:
            if self.set.use_testdata or use_test_data:
                self.data = data_class(TestData=True,
                               scaling_factors=(self.set.scaling_factor_x,
                                                self.set.scaling_factor_y,
                                                self.set.scaling_factor_z,))
            elif type(data) == data_class:
                self.data = data
            else:
                self.data = data_class(Empty = True)
                
            self.data.DADS = np.full((self.parm_tabs.count(),len(self.data.y)),np.nan)
            
            self.refresh_sliders()
            
            self.make_plot_kin()
            self.make_plot_spec()
            self.make_plot3D()
            
            self.rescale_plot_kin()
            self.rescale_plot_spec()
            
            self.xcut_low.setText(str(np.floor(min(self.data.x))))
            self.xcut_high.setText(str(np.ceil(max(self.data.x))))
            self.ycut_low.setText(str(np.floor(min(self.data.y))))
            self.ycut_high.setText(str(np.ceil(max(self.data.y))))

            self.status_label1.setText(f'Data Loaded: {len(self.data.x)} x points, {len(self.data.y)} y points and {str(len(self.data.y)).replace(',','x')} z points')
        
        except Exception as e:
            logger.exception('Error Loading Data')
            QMessageBox.warning(self,'Error Loading Data:',f'{e}')
            
            self.data = data_class(Empty = True)
            self.data.DADS = np.full((self.parm_tabs.count(),len(self.data.y)),np.nan)
    
    def refresh_sliders(self):
        self.slider1.slider.setRange(np.min(self.data.y),np.max(self.data.y)) #make sure slider values are inside ranges
        self.slider1.slider.setValue((np.min(self.data.y)+np.max(self.data.y))/2)
        # self.slider1.slider.setSingleStep(1)
        
        self.slider2.slider.setRange(np.min(self.data.x),np.max(self.data.x))
        self.slider2.slider.setValue((np.min(self.data.x)+np.max(self.data.x))/2)
        # self.slider2.slider.setSingleStep(1)
    
    def cut_data(self):
        self.statusBar().showMessage('cutting data...')
        x_low = float(self.xcut_low.text())
        x_high = float(self.xcut_high.text())
        y_low = float(self.ycut_low.text())
        y_high = float(self.ycut_high.text())
        
        self.data = self.data.cut_data(x_low=x_low,x_high=x_high,y_low=y_low,y_high=y_high)
        
        self.refresh_sliders()
        
        self.make_plot_kin()
        self.make_plot_spec()
        self.make_plot3D()

        self.rescale_plot_kin()
        self.rescale_plot_spec()
        self.rescale_plot3D()
        self.statusBar().showMessage('Ready...')
        
    def full_data(self):
        self.xcut_low.setText(str(np.floor(min(self.data.x_full))))
        self.xcut_high.setText(str(np.ceil(max(self.data.x_full))))
        self.ycut_low.setText(str(np.floor(min(self.data.y_full))))
        self.ycut_high.setText(str(np.ceil(max(self.data.y_full))))
        
        self.cut_data()
    
    def reset_user_defaults(self):
        self.set = fancyfitSettings()
    
    def restore_defaults(self):#TODO reset to default settings
        reply = QMessageBox.question(
                self,
                "Confirm",
                "Do you want to delete all data?",
                QMessageBox.Yes | QMessageBox.No
            )
            
        if reply == QMessageBox.Yes:
            self.statusBar().showMessage('restoring standard settings')
            self.set.default()
            self.set.save()
            self.statusBar().showMessage('Ready...')
    
    def open_filedialog(self):
        from gui.LoadDataWindow import LoadDataWindow
        ldw = LoadDataWindow()
        if ldw.exec():
            self.load_data(data = ldw.data)

    def open_settings(self):
        from gui.SettingsWindow import SettingsWindow
        sw = SettingsWindow()
        if sw.exec():
            self.set = sw.settings
        self.statusBar().showMessage('settings updated')
    
    def open_functionbuilder(self):
      try:
        from gui.FunctionBuilder import FunctionBuilder
        fbw = FunctionBuilder()
        if fbw.exec():
            self.statusBar().showMessage('Function added',2000)             

      except Exception as e:
          QMessageBox.critical(self,'Error',e)
    
    def save_results(self):
        self.statusBar().showMessage('saving results')
        folder = Path(self.set.z_data_path).parent
        filename = Path(self.set.z_data_path).stem+'_fit_results.txt'
        filepath = folder/filename
        with open(filepath,'w') as f:
            f.write(self.results_box.toPlainText())
    
    #%% =============================================================================
    # Plot Functions:
    # =============================================================================        
    def set_labels(self):
        self.plot_kin.fig.suptitle(self.set.x_name)
        self.plot_kin.set_labels(self.set.x_label+'/'+self.set.x_unit,
                                 self.set.z_label+'/'+self.set.z_unit)
        self.plot_spec.fig.suptitle(self.set.y_name)
        self.plot_spec.set_labels(self.set.y_label+'/'+self.set.y_unit,
                                  self.set.z_label+'/'+self.set.z_unit)
    
    def make_plot_kin(self):   
        kwargs_raw ={'linestyle': 'None',
                    'marker': 'o',
                    'markerfacecolor': 'None',
                    'markeredgecolor': 'k',
                    'markeredgewidth': 0.5,
                    'markersize': 6}
        kwargs_raw_inner ={'linestyle': 'None',
                    'marker': 'o',
                    'markerfacecolor': 'k',
                    'markeredgecolor': 'k',
                    'markeredgewidth': 0.1,
                    'markersize': 0.4}
        
        iy0 = np.argmax(self.data.y>=self.slider1.slider.value())
        self.plot_kin.set_line('raw',self.data.x,self.data.z[:,iy0],**kwargs_raw)
        self.plot_kin.set_line('raw_inner',self.data.x,self.data.z[:,iy0],**kwargs_raw_inner)
        self.plot_kin.set_line('fit',self.data.x_fit,self.data.z_fit[:,iy0],color='red')
        self.plot_kin.draw_idle()
   
    def rescale_plot_kin(self):
        for ax in self.plot_kin.axes:
            self.plot_kin.axes[ax].relim()
            self.plot_kin.axes[ax].autoscale_view()

        self.plot_kin.draw_idle()  

    def make_plot_spec(self):
        kwargs_raw ={'linestyle': 'None',
                    'marker': 'o',
                    'markerfacecolor': 'None',
                    'markeredgecolor': 'k',
                    'markeredgewidth': 0.5,
                    'markersize': 6}
        kwargs_raw_inner ={'linestyle': 'None',
                    'marker': 'o',
                    'markerfacecolor': 'k',
                    'markeredgecolor': 'k',
                    'markeredgewidth': 0.1,
                    'markersize': 0.4}
        ix0 = np.argmax(self.data.x>=self.slider2.slider.value())   
        self.plot_spec.set_line('raw',self.data.y,self.data.z[ix0,:],**kwargs_raw)
        self.plot_spec.set_line('raw_inner',self.data.y,self.data.z[ix0,:],**kwargs_raw_inner)
        self.plot_spec.set_line('fit',self.data.y_fit,self.data.z_fit[ix0,:],color='red')
        self.plot_spec.draw_idle()
        
    def rescale_plot_spec(self):
        for ax in self.plot_spec.axes:
            self.plot_spec.axes[ax].relim()
            self.plot_spec.axes[ax].autoscale_view()

        self.plot_spec.draw_idle()  
        
    def make_plot3D(self):
        sc = float(self.set.z_3Dstretch)
        zrange = np.array([np.median(self.data.z[self.data.z<0]),
                  np.median(self.data.z[self.data.z>0])])
        zrange = list(zrange*5*sc)#5 works well in the datasets I had so far. That's why this is defined as a stretch factor of 1.
        if np.isnan(zrange).any():
            zrange = [0,1]
        
        self.plot3D_Z.set_contour(self.data.y,self.data.x,self.data.z,zrange=zrange)
        self.plot3D_Zfit.set_contour(self.data.y_fit,self.data.x_fit,self.data.z_fit,zrange=zrange)
        self.plot3D_res.set_contour(self.data.y_fit,self.data.x_fit,self.data.residuum,zrange=zrange)
        
        self.plot3D_DADS.clear_lines()
        for n in range(self.parm_tabs.count()):
            self.plot3D_DADS.set_line(f'f{n+1}',self.data.y_fit,self.data.DADS[n,:])
        
        self.plot3D_Z.draw_idle()
        self.plot3D_Zfit.draw_idle()
        self.plot3D_res.draw_idle()
        self.plot3D_DADS.draw_idle()

    def rescale_plot3D(self):
        for ax in self.plot3D_Z.axes:
            self.plot3D_Z.axes[ax].relim()
            self.plot3D_Z.axes[ax].autoscale_view()
        for ax in self.plot3D_Zfit.axes:
            self.plot3D_Zfit.axes[ax].relim()
            self.plot3D_Zfit.axes[ax].autoscale_view()
        for ax in self.plot3D_res.axes.values():
            ax.relim()
            ax.autoscale_view
        for ax in self.plot3D_DADS.axes:
            self.plot3D_DADS.axes[ax].relim()
            self.plot3D_DADS.axes[ax].autoscale_view()

        self.plot3D_Z.draw_idle() 
        self.plot3D_Zfit.draw_idle() 
        self.plot3D_res.draw_idle() 
        self.plot3D_DADS.draw_idle() 

    # =============================================================================
    # Fit Functions and Classes:
    # =============================================================================
   
    def get_funs(self):
        funs=[]
        for n in range(self.parm_tabs.count()):
            funs.append(self.FitFuns[self.funs_input[n].currentText()]['fun'])
        return funs
        
    def get_parms(self):
        Parms=[]
        P0=[]
        P_lower=[]
        P_upper=[]
        
        for n in range(self.parm_tabs.count()):
            parms=[]
            p0=[]
            p_lower=[]
            p_upper=[]
            for m in range(len(self.parms_input[n])):
                parms.append(self.parms_input[n][m].text())
                p0.append(float(self.p0_input[n][m].text()))
                p_lower.append(float(self.p_lower_input[n][m].text()))
                p_upper.append(float(self.p_upper_input[n][m].text()))
            Parms.append(parms)
            P0.append(p0)
            P_lower.append(p_lower)
            P_upper.append(p_upper)
        
        return Parms,P0,P_lower,P_upper
        
        
    def execute_global_fit(self):
            self.statusBar().showMessage('Executing Global Fit...')

            # if str(Path(__file__).parent.parent) not in sys.path:
            #        sys.path.append(str(Path(__file__).parent.parent))
            from fittoolkit import GlobalFit # This is in my private FitToolkit package
            #TODO: add option to use demo fit function if FitToolkit not available
            
            data = self.data
            
            irf_index = [n for n in range(self.parm_tabs.count()) if self.parm_tabs.tabText(n)=='IRF']
            Fun_objs = [self.parm_tabs.widget(n).values() for n in range(self.parm_tabs.count()) if n not in irf_index] # get all functions except IRF
           
            funs = [fun_obj.func for fun_obj in Fun_objs]
            parms =[fun_obj.parm_names for fun_obj in Fun_objs]
            p0s = [fun_obj.p0 for fun_obj in Fun_objs]
            p_lowers = [fun_obj.p_lower for fun_obj in Fun_objs]
            p_uppers = [fun_obj.p_upper for fun_obj in Fun_objs]
            common_parms = [fun_obj.common_parms for fun_obj in Fun_objs]
            if irf_index:
                IRF = self.parm_tabs.widget(irf_index[0]).values()
                for n,fun in enumerate(funs):
                    pass #Convolute each function with IRF!
                
            settings={
                    'funs': funs,
                    'parms': parms,
                    'p0': p0s,
                    'p_lower': p_lowers,
                    'p_upper': p_uppers,
                    'common_parms': common_parms,
                     }
            
            try:
                self.gf = GlobalFit(data.x,data.y,data.z.T,settings=settings)       
                self.data.x_fit = self.gf.x
                self.data.y_fit = self.gf.y
                self.data.z_fit = self.gf.Z_fit.T
                self.data.DADS = self.gf.DADS.T
                self.data.residuum = self.gf.residuum.T
                
                self.make_plot_kin()
                self.make_plot_spec()
                self.make_plot3D()

                self.update_results()
                self.statusBar().showMessage('Fit finished successfully',1000)
                self.status_label2.setText('global fit')
                self.statusBar().showMessage('Ready...',0)

            except Exception as e:
                report= ("========================================\n"
                         f"=========== Critical Error {datetime.now().strftime('%H:%M')} ==========\n"
                         "========================================\n\n"
                         f"Error in global fit: {type(e).__name__}: {e}")
                self.results_box.append(report)
                logger.error(traceback.format_exc())
            
    
# ---------------------------
# ENTRY POINT (Spyder-safe)
# ---------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = Path(r"C:\Users\morit\OneDrive\Anwendungen\FancyFit\icon.ico")
    app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    
    sys.exit(app.exec())
        