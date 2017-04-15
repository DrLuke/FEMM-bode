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

import sys
import gui

#/home/drluke/.wine/drive_c/femm42/examples/test.ans
def main():
    app = QApplication(sys.argv)

    mainwindow = QMainWindow()
    ui = gui.Ui_MainWindow()
    ui.setupUi(mainwindow)

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