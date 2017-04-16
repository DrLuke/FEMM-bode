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

#/home/drluke/.wine/drive_c/femm42/examples/test.ans

class FEMMCanvas(FigureCanvasQTAgg):
    def __init__(self, fig):
        a = FEMM()
        ansr = a.readans("/home/drluke/.wine/drive_c/femm42/examples/test.ans")
        fig = matplotlib.figure.Figure(figsize=(4, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        
        super(FEMMCanvas, self).__init__(fig)
        
        a.plotans(ansr, self.axes)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.updateGeometry()
        self.draw()

    def update(self):
        pass


if __name__ == '__main__':
    class FEMMSolutionManager:
        def __init__(self, canvas: FigureCanvasQTAgg, ui: gui.Ui_MainWindow, femmfile: FEMMfem):
            self.canvas = canvas
            self.ui = ui
            self.femmfile = femmfile

            # initialize some healthy values
            self.minfreq = self.ui.minfreqSpinBox.value()
            self.maxfreq = self.ui.maxfreqSpinBox.value()
            self.decadesteps = self.ui.decadestepsSpinBox.value()

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
            self.solutions = {} # Dump all solutions when the stepsize is changes, otherwise data recycling will become too complicated

        def freqsliderchange(self, value):
            if self.ui.freqSlider.hasFocus():
                self.ui.freqSpinBox.setValue(10**(value/100))

        def freqspinboxchange(self, value):
            if self.ui.freqSpinBox.hasFocus():
                self.ui.freqSlider.setValue(math.log10(value)*100)

        def genlogrange(self):
            start = math.log10(self.minfreq)
            stop = math.log10(self.maxfreq)
            num = int((stop-start)*self.decadesteps)
            if num <= 0:
                num = 1
            return np.logspace(start, stop, num, endpoint=True)

        def gensolutions(self):
            logrange = self.genlogrange()
            for freq in logrange:
                if freq not in self.solutions:
                    pass    # TODO: generate solution


class BodeCanvas(FigureCanvasQTAgg):
    pass

class bodewindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(bodewindow, self).__init__(*args, **kwargs)

        self.ui = gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupView()

        self.currentFEM = None

        # Solutions Manager
        ## Will act whenever you change frequency range and step size to calculate new solutions as required
        self.FEMMSolutionManager = FEMMSolutionManager(self.FEMMCanvas, self.ui, None)

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
            self.loadFEM(fileDialog.selectedFiles()[0]) # selectedFiles returns a list of selected files, but we only take the first

    def loadFEM(self, path):
        if os.path.exists(path):
            with open(path) as f:
                self.currentFEM = f.read()

    def setViewFreq(self, frequency):
        pass


def main():
    app = QApplication(sys.argv)

    mainwindow = bodewindow()


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