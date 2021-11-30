import numpy as np
import matplotlib
# import matplotlib.axes._subplots.AxesSubplot as AP
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from tqdm import tqdm
# from sys import argv
import sys,os
import streamlit as st
from io import StringIO

fig, ax = plt.subplots()
def readfile(fl):
    with fl as f:
        return fl.read()

filename = st.sidebar.file_uploader("TraversalDetails" ,type=("txt"))
stationList = st.sidebar.file_uploader("Stations" ,type=("txt"))

@st.cache(hash_funcs={StringIO:StringIO.getvalue},allow_output_mutation=True)
# @st.cache
def readTD(filename):
    with filename as t:
        TD = t.readlines()
    patchList = {}
    count = 0
    for indx,row in enumerate(TD):
        if 'Printing' in row:
            presentTrain = row.split()[-1]
            patchList[presentTrain]=[]
        else:
            temp = row.split()
            startKm = float(temp[5])
            endKm = float(temp[8])
            startTime = float(temp[11])
            endTime = float(temp[14])

            ptch=((startTime,startKm),(endTime,endKm))
            patchList[presentTrain].append(ptch)
    return patchList

patchList = readTD(filename)

trainsToPlot = st.sidebar.multiselect('Select Trains:',list(patchList.keys())+['All-Trains'],default=['All-Trains'])
# @st.cache
def updatePlot():
    if 'All-Trains' in trainsToPlot:
        plotPaches = [j for i in patchList.values() for j in i]
    else:
        plotPaches = [j for i in trainsToPlot for j in patchList[i]]
    p=LineCollection(plotPaches,colors='k')
    ax.add_collection(p)
    if stationList==None: return
    yTicks = []
    yLables = []
    for s in stationList.readlines()[1:]:
        if not len(s.split())>1:continue
        # stnDict[s.split()[0]]=s.split()[1]
        yTicks.append(float(s.split()[1]))
        yLables.append(s.split()[0])
    # print(yTicks,yLables)
    plt.yticks(yTicks,yLables)


with st.spinner('adding patches'):
    updatePlot()


plt.xlim(*st.sidebar.slider('x scale',0,4320,(0,4320)))
plt.ylim(*st.sidebar.slider('y scale',0,1400,(0,1400)))
# Show the major grid lines with dark grey lines
plt.grid(b=True, which='major', color='#666666', linestyle='-')

# Show the minor grid lines with very faint and almost transparent grey lines
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

with st.spinner('Attempting to plot'):
    st.pyplot()
