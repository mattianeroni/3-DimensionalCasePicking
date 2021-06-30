import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.colors as pltc
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from orderline import OrderLine
from case import Case

import warnings
warnings.filterwarnings("ignore")


def readfile (filename, delimiter=";"):
    file = pd.read_csv(filename, delimiter=delimiter)
    orderlines = []
    for _, line in file.iterrows():
        orderline = OrderLine(code=line['Code'], location=line['Location'])
        cases = tuple(Case(orderline, line['Code'], line['SizeX'], line['SizeY'], line['SizeZ'], line['Weight'], line['Strength'])
                     for i in range(line["#Cases"]))
        orderline.cases = cases
        orderlines.append(orderline)

    return tuple(orderlines)




def cuboid_data2(o, size=(1,1,1)):
    X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
         [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
         [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
         [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
         [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
         [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
    X = np.array(X).astype("float")
    for i in range(3):
        X[:,:,i] *= size[i]
    X += np.array(o)
    return X

def plotCubeAt2(positions,sizes=None,colors=None, **kwargs):
    if not isinstance(colors,(list,np.ndarray)):
        colors=["C0"]*len(positions)
    if not isinstance(sizes,(list,np.ndarray)):
        sizes=[(1,1,1)]*len(positions)

    g = []
    for p,s,c in zip(positions,sizes,colors):
        g.append( cuboid_data2(p, size=s) )
    return Poly3DCollection(np.concatenate(g), facecolors=np.repeat(colors,6), **kwargs)


def plot (pallet):
    all_colors = [k for k,v in pltc.cnames.items()]

    positions = []
    sizes = []

    for case in pallet.cases:
        positions.append(case.position)
        sizes.append((case.sizex, case.sizey, case.sizez))


    colors = random.sample(all_colors, len(positions))

    fig = plt.figure(figsize=(15,15))
    ax = fig.gca(projection='3d')
    ax.add_collection3d(plotCubeAt2(positions, sizes, colors=colors, edgecolor="k", alpha=0.5))

    X, Y, Z = pallet.size
    ax.set_xlim([0,X])
    ax.set_ylim([0,Y])
    ax.set_zlim([0,Z])

    plt.show()
