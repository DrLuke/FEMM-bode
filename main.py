import subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import math
from scipy.interpolate import griddata

import os
from femm import FEMM

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import sys
import gui

#/home/drluke/.wine/drive_c/femm42/examples/test.ans

class bodewindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(bodewindow, self).__init__(*args, **kwargs)

        self.ui = gui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.currentFEM = None

        # Settings
        self.minfreq = 1
        self.maxfreq = 100

        # Menubar signals
        self.ui.actionLoad_FEM_File.triggered.connect(self.selectFEM)   # Open *.FEM file
        self.ui.actionExit.triggered.connect(self.close)                # Exit Action

        # Frequency slider dock
        self.ui.freqSlider.sliderMoved.connect(lambda x: self.ui.freqSpinBox.setValue((x/10000)*(self.maxfreq-self.minfreq) + self.minfreq))

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