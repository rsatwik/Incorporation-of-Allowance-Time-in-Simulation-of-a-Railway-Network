#changing here

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from sys import argv
import pdb

stationCode = pd.read_csv('StationCodes.csv')
removeQuotes = lambda x:re.sub(r'^"|"$', '',x)
def findStnCode(x):
    try:
        x= removeQuotes(x)
        code = stationCode[stationCode['stations']==x]['stncode'].tolist()[0]
        # print(x,code)
        return code
    except:
        print(x)
        assert 0,'Station Code Not Found'

printAll = False

# Sfiles = [
# 'stationNDLS-MAS.txt',
# 'stationNDLS-MMCT.txt'
# ]

# Bfiles = [
# 'blockCD.txt',
# 'blockDM.txt'
# ]

# Lfiles = [
# 'loopCD.txt',
# 'loopDM.txt'
# ]

Sfiles = []
Bfiles = []
Lfiles = []

for a in argv[1:]:
    Sfiles.append(a+'/station.txt')
    Bfiles.append(a+'/block.txt')
    Lfiles.append(a+'/loop.txt')

stationFiles = []
for s in Sfiles:
    with open(s) as o:
        stationFiles.append(o.readlines())

blockFiles = []
for s in Bfiles:
    with open(s) as o:
        blockFiles.append(o.readlines())

loopFiles = []
for s in Lfiles:
    with open(s) as o:
        loopFiles.append(o.readlines())


# NodeStations = ['NDLS','TKJ','MTJ','MMCT','HWH','KGP','NGP','SEGM','BZA','KYN','CSTM','BBQ','MAS']
###############################################################################################################

for fl in stationFiles:
    for indx,row in enumerate(fl):
        if not row[0]=='"':continue
        # print('change Station')
        temp = fl[indx].split()
        temp[0]=removeQuotes(temp[0])
        fl[indx] = ' '.join(temp)

for fl in loopFiles:
    for indx,row in enumerate(fl):
        temp = fl[indx].split()
        if len(temp)<3:continue
        if temp[3][0]=='"':
            # print('change loop')
            temp[3]=removeQuotes(temp[3])
            fl[indx] = ' '.join(temp)

        if temp[4][0]=='"':
            temp[4]=removeQuotes(temp[4])
            fl[indx] = ' '.join(temp)


##############################################################################################################
#combine station
##############################################################################################################
allStations = {}
G = nx.Graph()

allRouteDict = {}
allRoutesChange = {i:[] for i in range(len(stationFiles))}

R=nx.Graph()
for r in range(len(stationFiles)):
    R.add_node(r)

for route,fl in enumerate(stationFiles):
    allRouteDict[route] = []
    prev = None
    for row in fl[2:]:
        temp = [i.strip() for i in row.split(' ')]
        stn = temp[0]
        startkm = float(temp[1])
        endkm = float(temp[2])
        speed = float(temp[3])

        allRouteDict[route].append(stn)

        if stn in allStations:
            allStations[stn][route] = [startkm,endkm,speed]
        else:
            allStations[stn]={route:[startkm,endkm,speed]}
            G.add_node(stn,mileposts = allStations[stn])

        if prev:
            if (prev[0],stn) in G.edges():
                distance = round(startkm-prev[1],3)
                print(distance,G.edges[prev[0],stn]['dist'])
                try:
                    assert (G.edges[prev[0],stn]['dist']==distance)
                except AssertionError as a:
                    print('Distance Mismatch',prev[0],stn,'prevDistance:',G.edges[prev[0],stn]['dist'],'distance Now',distance)
                    assert 0,a

            else:
                distance = round(startkm-prev[1],3)
                G.add_edge(prev[0],stn,dist = distance)
        prev = (stn,endkm)


while True:
    stationsWithMultipleRoutes = [(i,j) for i,j in allStations.items() if len(set([k[0] for k in j.values()]))>1]
    if len(stationsWithMultipleRoutes) == 0: break
    for stn,val in stationsWithMultipleRoutes:
        if len(set([i[0] for i in val.values()]))==1: continue
        maxRoute,maxKm = max([(r,km) for r,km in val.items()],key = lambda x:x[1])

        for route,km in val.items():
            if route == maxRoute:continue
            # lenAdded = round(maxKm[0] - km[0],3)
            lenAdded = maxKm[0] - km[0]
            stnIndx = allRouteDict[route].index(stn)
            allRoutesChange[route].append({'station':stn,'stationIndex':stnIndx,'lengthChange':lenAdded})

            for s in allRouteDict[route][stnIndx:]:
                allStations[s][route][0]+=lenAdded
                allStations[s][route][1]+=lenAdded

print('done')
newStationList = []
for i in allStations:
    allStations[i] = list(allStations[i].values())[0]
print('Total number of stations',len(allStations))

##############################################################################################################################
#update block mileposts
##############################################################################################################################
for rt,C in allRoutesChange.items():
    for change in C:
        # print(type(rt),type(change['stationIndex']))
        allStationCodes = [findStnCode(s) for s in allRouteDict[rt][change['stationIndex']:]]
        for indx,row in enumerate(blockFiles[rt]):
            if any([row.startswith(str(s)) for s in allStationCodes]):
                    temp = row.split(' ')
                    temp[2] = str(float(temp[2])+change['lengthChange'])
                    temp[3] = str(float(temp[3])+change['lengthChange'])
                    blockFiles[rt][indx] = ' '.join(temp)
                    if printAll:
                        print('original:',row)
                        print('changed:',' '.join(temp))


##############################################################################################################################
#update Links
##############################################################################################################################

allBlocks = {}
allRouteBlocks = {}
allRouteLoops = {}
for route,fl in enumerate(blockFiles):
    allRouteBlocks[route] = []
    for row in fl[2:]:
        temp = row.split(' ')
        blkNum = temp[0]
        upLink = (removeQuotes(temp[5])).split(',')
        dnLink = (removeQuotes(temp[9])).split(',')
        allRouteBlocks[route].append(blkNum)

        if blkNum not in allBlocks: allBlocks[blkNum] = {'upLinks':{},'dnLinks':{},'type':'block'}
        if upLink[0]:
            allBlocks[blkNum]['upLinks'][route] = upLink

        if dnLink[0]:
            allBlocks[blkNum]['dnLinks'][route] = dnLink

for route,fl in enumerate(loopFiles):
    allRouteLoops[route] = []
    for row in fl[2:]:
        temp = row.split(' ')
        blkNum = temp[0]
        allRouteLoops[route].append(blkNum)
        upLink = (removeQuotes(temp[6])).split(',')
        dnLink = (removeQuotes(temp[10])).split(',')
        if blkNum not in allBlocks: allBlocks[blkNum] = {'upLinks':{},'dnLinks':{},'type':'loop'}

        if upLink[0]:
            allBlocks[blkNum]['upLinks'][route] = upLink

        if dnLink[0]:
            allBlocks[blkNum]['dnLinks'][route] = dnLink

stationsWith3Links = ['NDLS']+[n for n in G.nodes() if len(G[n])==3]
print('allStations at Y',stationsWith3Links)
assert(len([n for n in G.nodes() if len(G[n])>3])==0)

print('finding node stations')
for s in stationsWith3Links:
    stnCode = findStnCode(s)
    neighbouringStations = list(G[s])
    neighbouringCodes = [findStnCode(k) for k in list(G[s])]
    linkedCheckloops = list(set([(rt,[ns for ns in neighbouringCodes if str(i).startswith(str(ns))][0]) for b,l in allBlocks.items() if b.startswith(str(stnCode)) and (len(l['upLinks'])>1 or
        len(l['dnLinks'])>1) and l['type']=='block' for rt,j in list(l['upLinks'].items())+list(l['dnLinks'].items()) for i in j if not str(i).startswith(str(stnCode))]))

    linkedLoops = list(set([(rt,[ns for ns in neighbouringCodes if str(i).startswith(str(ns))][0]) for b,l in allBlocks.items() if b.startswith(str(stnCode)) for rt,j in list(l['upLinks'].items()) for i in j if not str(i).startswith(str(stnCode))]))
    # pdb.set_trace()
    print('___________________________')
    print(s,stnCode)
    # print('StationDistance:',G.node()[s])
    print('NeighbouringCodes:',neighbouringCodes)
    print('linkedLoops',linkedLoops)
    print('linkedLoopscheck:',linkedCheckloops)
    # Y converge
    if len(set([l[1] for l in linkedLoops]))==1:
        downLinksofLoops = set([j for b,l in allBlocks.items() if b.startswith(str(stnCode)) and l['type']=='loop' for i in l['dnLinks'].values() for j in i])
        downLoops = set([b for b,l in allBlocks.items() if b.startswith(str(stnCode)) and l['type']=='loop' and len(l['dnLinks'])>0])
        # print('allDownLinks',downLinksofLoops,'allDownLoops',downLoops)
        for flNum,fl in [(i[0],loopFiles[i[0]]) for i in linkedLoops]:
            for lp in downLoops:
                for indx,row in enumerate(fl):
                    if row.startswith(str(lp)):
                        temp = row.split(' ')
                        temp[10] = '"'+','.join(downLinksofLoops)+'"'
                        temp[11] = '"'+','.join([str(0.0) for i in range(len(downLinksofLoops))])+'"'
                        temp[12] = '"'+','.join([str(i) for i in range(1,len(downLinksofLoops)+1)])+'"'
                        temp[13] = '"'+','.join(['#' for i in range(len(downLinksofLoops))])+'"'
                        loopFiles[flNum][indx] = ' '.join(temp)
                        if printAll:
                            print('original:',row)
                            print('changed:',' '.join(temp))


    # Y diverge
    elif len(set([l[1] for l in linkedLoops]))==2:
        upLoops = [(b,l['upLinks']) for b,l in allBlocks.items() if b.startswith(str(stnCode)) and l['type']=='loop' and len(l['upLinks'])>0]
        secondRouteStnBlocks = [b for b,l in allBlocks.items() if b.startswith(str(stnCode)) and l['type']=='block' and (linkedLoops[1][0] in l['upLinks'] or linkedLoops[1][0] in l['dnLinks'])]
        # print('allBlocks',secondRouteStnBlocks,'allupLoops',upLoops)
        changeName= {str(i):str(linkedLoops[1][0]+1)+i for i in secondRouteStnBlocks}
        print('changeName',changeName)

        #changing Block Names
        for lp in secondRouteStnBlocks:
            for indx,row in enumerate(blockFiles[linkedLoops[1][0]]):
                if row.startswith(str(lp)):
                    temp = row.split(' ')
                    temp[0] = changeName[str(lp)]
                    if len(allBlocks[lp]['upLinks'])>0:
                        if any([(i in secondRouteStnBlocks)  for i in allBlocks[lp]['upLinks'][linkedLoops[1][0]]]):
                            temp[5] = '"'+','.join([changeName[i] for i in removeQuotes(temp[5]).split(',')])+'"'
                    if len(allBlocks[lp]['dnLinks'])>0:
                        if any([(i in secondRouteStnBlocks)  for i in allBlocks[lp]['dnLinks'][linkedLoops[1][0]]]):
                            temp[9] = '"'+','.join([changeName[i] for i in removeQuotes(temp[9]).split(',')])+'"'
                    blockFiles[linkedLoops[1][0]][indx] = ' '.join(temp)
                    if printAll:
                        print('original:',row)
                        print('changed:',' '.join(temp))




        #changing up links of stn Loops
        for flNum,fl in [(i[0],loopFiles[i[0]]) for i in linkedLoops]:
            for lp,link in upLoops:
                for indx,row in enumerate(fl):
                    if row.startswith(str(lp)):
                        # print(lp,link.keys())
                        previousLink = link[linkedLoops[0][0]][0]
                        newLink = changeName[str(previousLink)]
                        temp = row.split(' ')
                        temp[6] = '"'+','.join([previousLink,newLink])+'"'
                        temp[7] = '"'+','.join([str(0.0) for i in range(2)])+'"'
                        temp[8] = '"'+','.join([str(i) for i in range(1,3)])+'"'
                        temp[9] = '"'+','.join(['#' for i in range(2)])+'"'
                        loopFiles[flNum][indx] = ' '.join(temp)
                        if printAll:
                            print('original:',row)
                            print('changed:',' '.join(temp))


        #changing dn links of next station loops
        nextStation = linkedLoops[1][1]
        downLoops = set([(b,l['dnLinks'][linkedLoops[1][0]][0]) for b,l in allBlocks.items() if b.startswith(str(nextStation)) and l['type']=='loop' and len(l['dnLinks'])>0])
        for lp in downLoops:
            for indx,row in enumerate(loopFiles[linkedLoops[1][0]]):
                if row.startswith(str(lp[0])):
                    temp = row.split(' ')
                    if temp[0]!=str(lp[0]):continue
                    # previousLink = link[linkedLoops[1][0]][0]
                    previousLink = removeQuotes(temp[10])
                    newLink = changeName[previousLink]
                    # print(previousLink,newLink)
                    temp[10] = '"'+newLink+'"'
                    loopFiles[linkedLoops[1][0]][indx] = ' '.join(temp)
                    if printAll:
                        print('original:',row)
                        print('changed:',' '.join(temp))
    else:
        print(s,linkedLoops)
        assert 0,'neither Y or inverted Y'


###################################################################################################################################
#printing to files
###################################################################################################################################
newStationList = sorted(allStations.items(),key=lambda x:x[1][0])
with open('station.txt','w') as o:
    o.write(stationFiles[0][0]+'\n')

    for i,j in newStationList:
        o.write(' '.join([str(i)]+[str(k) for k in j])+'\n')

with open('block.txt','w') as o:
    o.write(blockFiles[0][0]+'\n')

    tempblkFile = []
    addedBlks = {}
    for blk in blockFiles:
        for row in blk[2:]:
            if row not in tempblkFile:
                if row.split()[0] in addedBlks.keys():
                    # print('similar',addedBlks[row.split()[0]]==row,' block prev',addedBlks[row.split()[0]],'\nsimilar',addedBlks[row.split()[0]]==row,'new',row)
                    continue
                addedBlks[row.split()[0]]=row
                o.write(row)


with open('loop.txt','w') as o:
    o.write(loopFiles[0][0]+'\n')

    templpFile = []
    addedLps = {}
    for lp in loopFiles:
        for row in lp[2:]:
            # print(row)
            if row not in templpFile:
                if row.split()[0] in addedLps.keys():
                    # print('similar',addedLps[row.split()[0]]==row,' loop prev',addedLps[row.split()[0]],'\nsimilar',addedLps[row.split()[0]]==row,'new',row)
                    continue
                addedLps[row.split()[0]]=row
                o.write(row+'\n')


