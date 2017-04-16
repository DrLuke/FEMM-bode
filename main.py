import subprocess
import matplotlib as mpl
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import numpy as np
import re
import math
from scipy.interpolate import griddata

import os
from femm import FEMM, FEMMfem, FEMMans

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QFileDialog, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import sys
import gui

import math
import appdirs
import json


def customexcepthook(type, value, traceback):
    print(traceback.print_exc())
    raise(Exception())
sys.excepthook = customexcepthook


class FEMMCanvas(FigureCanvasQTAgg):
    def __init__(self, fig):

        fig = matplotlib.figure.Figure(figsize=(4, 4), dpi=100)
        self.axes = fig.add_subplot(111)

        super(FEMMCanvas, self).__init__(fig)

        self.lastdrawnfreq = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #self.updateGeometry()
        self.draw_idle()

    def updateFEMM(self, freq: float, solutions: dict):
        keys = list(solutions.keys())
        freqdist = [abs(x - freq) for x in keys]
        idx = freqdist.index(min(freqdist))
        if not self.lastdrawnfreq == keys[idx]:
            solution = solutions[keys[idx]]
            self.lastdrawnfreq = keys[idx]
            self.axes.clear()
            self.axes.imshow(solution["imdata"], extent=(math.floor(solution["ans"].x.min()), math.ceil(solution["ans"].x.max()), math.floor(solution["ans"].y.min()), math.ceil(solution["ans"].y.max())))
            self.draw()
            self.repaint()


class FEMMSolutionManager:
    def __init__(self, canvas: FigureCanvasQTAgg, ui: gui.Ui_MainWindow, femmfile: FEMMfem, config: dict):
        self.canvas = canvas
        self.ui = ui
        self.femmfile = femmfile
        self.config = config

        # Initialize UI
        self.ui.generateButton.setEnabled(True)
        self.ui.freqSlider.setEnabled(False)
        self.ui.freqSpinBox.setEnabled(False)

        # initialize some healthy values
        self.minfreq = self.ui.minfreqSpinBox.value()
        self.maxfreq = self.ui.maxfreqSpinBox.value()
        self.decadesteps = self.ui.decadestepsSpinBox.value()
        self.viewfreq = self.minfreq

        self.ui.freqSlider.setMinimum(math.floor(math.log10(self.minfreq) * 100))
        self.ui.freqSlider.setMaximum(math.ceil(math.log10(self.maxfreq) * 100))

        # Signals
        self.ui.minfreqSpinBox.valueChanged.connect(self.minmaxchange)
        self.ui.maxfreqSpinBox.valueChanged.connect(self.minmaxchange)
        self.ui.decadestepsSpinBox.valueChanged.connect(self.stepchange)
        self.ui.freqSlider.valueChanged.connect(self.freqsliderchange)
        self.ui.freqSpinBox.valueChanged.connect(self.freqspinboxchange)
        self.ui.generateButton.pressed.connect(self.gensolutions)

        self.solutions = {}

    def minmaxchange(self, value):
        self.minfreq = self.ui.minfreqSpinBox.value()
        self.maxfreq = self.ui.maxfreqSpinBox.value()

        self.ui.freqSlider.setMinimum(math.floor(math.log10(self.minfreq)*100))
        self.ui.freqSlider.setMaximum(math.ceil(math.log10(self.maxfreq)*100))

    def stepchange(self, value):
        # This is a bit more complicated. When the step size changes, all previous solutions have to be discarded.
        self.decadesteps = self.ui.decadestepsSpinBox.value()
        self.solutions = {}     # Dump all solutions when the stepsize is changes, otherwise data recycling will become too complicated
        self.ui.generateButton.setEnabled(True)
        self.ui.freqSlider.setEnabled(False)
        self.ui.freqSpinBox.setEnabled(False)

    def freqsliderchange(self, value):
        if self.ui.freqSlider.hasFocus():
            self.ui.freqSpinBox.setValue(10**(value/100))
            self.canvas.updateFEMM(10**(value/100), self.solutions)

    def freqspinboxchange(self, value):
        if self.ui.freqSpinBox.hasFocus():
            self.ui.freqSlider.setValue(math.log10(value)*100)
            self.canvas.updateFEMM(value, self.solutions)

    def genlogrange(self):
        start = math.log10(self.minfreq)
        stop = math.log10(self.maxfreq)
        num = int((stop-start)*self.decadesteps)
        if num <= 0:
            num = 1
        return np.logspace(start, stop, num, endpoint=True)

    def gensolutions(self):
        logrange = self.genlogrange()
        with open(os.path.join(self.config["cdrivepath"], "TEMP.lua"), "w") as f:
            f.write("open(\"C:\\TEMP.FEM\"); mi_setfocus(\"TEMP.FEM\"); mi_analyze(); quit(1)")
        for freq in logrange:
            if freq not in self.solutions:
                with open(os.path.join(self.config["cdrivepath"], "TEMP.FEM"), "w") as f:
                    f.write(self.femmfile.setfreq(freq))
                # TODO: Let wine (optionally) run in fake screenbuffer for maximum efficiency
                subprocess.call(["wine", self.config["femmexe"], "C:\\TEMP.FEM", "-lua-script=C:\\TEMP.lua"])

                ans = FEMMans.readans(os.path.join(self.config["cdrivepath"], "TEMP.ans"))
                self.solutions[freq] = {"ans": ans, "imdata": ans.generateimdata(100)}

        os.remove(os.path.join(self.config["cdrivepath"], "TEMP.lua"))
        os.remove(os.path.join(self.config["cdrivepath"], "TEMP.FEM"))
        os.remove(os.path.join(self.config["cdrivepath"], "TEMP.ans"))

        self.ui.generateButton.setEnabled(False)
        self.ui.freqSlider.setEnabled(True)
        self.ui.freqSpinBox.setEnabled(True)

class BodeCanvas(FigureCanvasQTAgg):
    pass

class bodewindow(QMainWindow):
    def __init__(self, config, *args, **kwargs):
        self.config = config

        super(bodewindow, self).__init__(*args, **kwargs)

        self.ui = gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupView()

        self.currentFEM = None

        # Solutions Manager
        ## Will act whenever you change frequency range and step size to calculate new solutions as required
        self.FEMMSolutionManager = None

        # Menubar signals
        self.ui.actionLoad_FEM_File.triggered.connect(self.selectFEM)   # Open *.FEM file
        self.ui.actionExit.triggered.connect(self.close)                # Exit Action

    def setupView(self):
        self.FEMMFig = matplotlib.figure.Figure(figsize=(100, 100), dpi=300)
        self.FEMMCanvas = FEMMCanvas(self.FEMMFig)
        self.FEMMTab = self.ui.tabWidget.addTab(self.FEMMCanvas, "FEMM Project Display")

        self.bodeFig = matplotlib.figure.Figure(figsize=(100, 100), dpi=300)
        self.bodeCanvas = BodeCanvas(self.bodeFig)
        self.bodeTab = self.ui.tabWidget.addTab(self.bodeCanvas, "Bode Plot")

    def selectFEM(self):
        fileDialog = QFileDialog()
        fileDialog.setDefaultSuffix("FEM")
        fileDialog.setNameFilters(["FEMM Project File (*.FEM *.fem)", "FEMM Solution File (*.ans)", "Any files (*)"])
        if fileDialog.exec():
            path = fileDialog.selectedFiles()[0]    # selectedFiles returns a list of selected files, but we only take the first
            if os.path.exists(path):
                self.currentFEM = FEMMfem(path=path)
                self.FEMMSolutionManager = FEMMSolutionManager(self.FEMMCanvas, self.ui, self.currentFEM, self.config)



def main():
    configdir = appdirs.user_config_dir("FEMMBode")
    if not os.path.isdir(configdir):    # Create configuration dir if it doesn't exist
        os.makedirs(configdir)
    if os.path.exists(os.path.join(configdir, "preferences.json")):     # Check if config file exists, load if true
        with open(os.path.join(configdir, "preferences.json")) as f:
            config = json.load(f)
    else:   # Create blank config file if false
        config = {"cdrivepath": os.path.join(os.path.expanduser("~/.wine/drive_c")),
                  "femmexe": "C:\\\\femm42\\\\bin\\\\femm.exe"}
        with open(os.path.join(configdir, "preferences.json"), "w") as f:
            json.dump(config, f, indent=4, sort_keys=True)

    app = QApplication(sys.argv)

    mainwindow = bodewindow(config)


    mainwindow.show()
    retcode = app.exec_()

    sys.exit(retcode)

if __name__ == "__main__":
    a = FEMM()


    #ansr = a.readans("/home/drluke/.wine/drive_c/femm42/examples/test.ans")
    #a.plotans(ansr)
    #a.saveans(ansr, "foo.png")
    #a.plotlogrange("/home/drluke/.wine/drive_c/femm42/examples/test.FEM", -1, 12)

    main()

