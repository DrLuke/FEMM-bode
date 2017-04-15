import subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import math
from scipy.interpolate import griddata
import os


#/home/drluke/.wine/drive_c/femm42/examples/test.ans

if __name__ == "__main__":
    a = FEMM()
    #ansr = a.readans("/home/drluke/.wine/drive_c/femm42/examples/test.ans")
    #a.plotans(ansr)
    #a.saveans(ansr, "foo.png")
    a.plotlogrange("/home/drluke/.wine/drive_c/femm42/examples/test.FEM", -1, 12)