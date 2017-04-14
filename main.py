import subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import math
from scipy.interpolate import griddata

class FEMMans:
    def __init__(self, points, preamble):
        self.points = points
        self.preamble = preamble
        self.x = np.zeros(points)
        self.y = np.zeros(points)
        self.B = np.zeros(points, dtype=np.complex64)

class FEMM:
    def __init__(self):
        pass

    def readans(self, path):
        with open(path, "r") as f:
            firstline = f.readline()
            match = re.search("\[Format\]\s*=\s*([\d\.]+)", firstline)
            if match:
                if match.group(1) == "4.0":
                    return self.readans40(f)


    def readans40(self, f):
        preamble = ""  # Everything before the [Solution] tag
        points = None  # Number of datapoints to expect

        ans = None
        index = 0

        dataregex = re.compile(r"^([\d\.e-]+)\s+([\d\.e-]+)\s+([\d\.e-]+)\s+([\d\.e-]+)\s+([\d\.e-]+)\s+$")

        aftersolution = False
        for line in f:
            if not aftersolution:
                preamble += line
                if line == ("[Solution]\n"):
                    aftersolution = True
            elif points is None:    # First line after [Solution] gives the number of points in the solution
                points = int(line)
                ans = FEMMans(points, preamble)
            else:   # Read data point and add to dataset
                match = dataregex.search(line)
                if match:
                    ans.x[index] = float(match.group(1))
                    ans.y[index] = float(match.group(2))
                    ans.B[index] = float(match.group(3)) + float(match.group(4)) * 1j

                    index += 1
        return ans


    def plotans(self, ans):
        grid_x, grid_y = np.mgrid[math.floor(ans.x.min()):math.ceil(ans.x.max()):1000j, math.floor(ans.y.min()):math.ceil(ans.y.max()):1000j]
        grid = griddata(np.vstack((ans.x, ans.y)).T, np.absolute(ans.B), (grid_x, grid_y), method='cubic')

        plt.imshow(grid.T, extent=(math.floor(ans.x.min()), math.ceil(ans.x.max()), math.floor(ans.y.min()), math.ceil(ans.y.max())), cmap=plt.get_cmap("jet"))
        plt.contour(grid_x, grid_y, grid)
        plt.show()





#/home/drluke/.wine/drive_c/femm42/examples/test.ans

if __name__ == "__main__":
    a = FEMM()
    ansr = a.readans("/home/drluke/.wine/drive_c/femm42/examples/test.ans")
    a.plotans(ansr)