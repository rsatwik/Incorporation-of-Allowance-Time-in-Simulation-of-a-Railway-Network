rom sys import argv
import networkx as nx
import pandas as pd
import numpy as np
import re

from configparser import ConfigParser
parser = ConfigParser()
# parser.read("../../config.ini")
station_txt ='station.txt' #parser["common_files"]["station"]
blockpsr_12951 = '1blockpsr.csv' #parser["GenerateInfra"]["blockpsr_12951"]
blockpsr_12952 = '2blockpsr.csv' #parser["GenerateInfra"]["blockpsr_12952"]
looplist_txt ='loopList.txt' #parser["GenerateInfra"]["looplist"]
stnCode_csv = 'StationCode.csv' #parser["GenerateInfra"]["StationCode"] #pd.read_csv('StationCode.csv')
stnSpeed_csv = 'additionalDetailsStations.csv' #parser["GenerateInfra"]["MPS"] #pd.read_csv('additionalDetailsStationsMMCTNDLS.csv')

class Station():                   # CHANGE CODE :: Add loop lines to the platform along with the original mainlines as well
    def __init__(self,line,loop_line,stnSpeed,stnCode):
        temp = line.split()
        self.name = re.sub(r'^"|"$', '', temp[0])
        self.stnCode = stnCode
        self.startDist = float(temp[1])
        self.endDist = float(temp[2])
        self.maxAllowedSpeed = float(temp[3])
        self.loopList = []
        self.loopCounts = [{True:0,False:0},{True:0,False:0},{True:0,False:0}]
        self.blkSpeed = stnSpeed[stnSpeed['Station']==self.name][['UpMaxSpeed','DownMaxspeed']]
        if 'udLine' in stnSpeed.columns:
            self.blkLines = {'ud':stnSpeed[stnSpeed['Station']==self.name].udLine.value[0],
            'common':stnSpeed[stnSpeed['Station']==self.name].cmLine.value[0]}
        else:
            self.blkLines = {'ud':1,'common':0}
        loopdata=loop_line.split()


        # Hopefully stn code would be correct for loop_line and line files
        # The loop line would be stored in this format:
        # STNCODE || number of up loops || number of down loops || number of loops with both direction
        # Loop count excluding the Main Lines

        self.uploopcount=int(loopdata[1])
        self.downloopcount=int(loopdata[2])
        self.commonloopcount=int(loopdata[3])           # Of course up and down mainlines don't affect the commonloops

        # Add Main Lines By Default
        self.addLoopLine(0,ML=True)
        self.addLoopLine(1,ML=True)

        # Add loop lines; up down and common
        [self.addLoopLine(0,ML=False) for i in range(self.uploopcount)]        # up loop lines
        [self.addLoopLine(1,ML=False) for i in range(self.downloopcount)]      # down loop lines
        [self.addLoopLine(2,ML=False) for i in range(self.commonloopcount)]    # common loop lines

    def addLoopLine(self,UDC,ML=False):
        print("adding a loopline at:",self.stnCode)
        self.loopCounts[UDC][ML] += 1
        self.loopList.append(Loop(self,UDC,ML,self.loopCounts[UDC][ML]))

    def addLink(self,block,direction):    # Block to be linked in known
        print(f"linking a loopline for {self.name} at {block.num} in {direction}")
        if direction == 'up':
            toBeLinkedLoops = [l for l in self.loopList if l.dir != 'down']     # up and common direction loops both!!
            for l in toBeLinkedLoops:
                l.addLink(block,direction)
        elif direction == 'down':
            toBeLinkedLoops = [l for l in self.loopList if l.dir != 'up']        # down and common direction loops both!!
            for l in toBeLinkedLoops:
                l.addLink(block,direction)
        else:
            assert(0)

    def __str__(self):
        return self.name

    def __repr__(self):
        return  ("{} {} {} {}\n").format(self.name,self.startDist,self.endDist,self.maxAllowedSpeed) #"Kanpur" 0.0 1.0 100.0

class Loop():
    def __init__(self,station,UDC,ML=False,count=1):
        #assert UDC in [0,1,2]
        #assert count<=9

        self.num = str(station.stnCode)+str(UDC)+str(0 if ML else 1)+'0'+str(count)
        self.dir = 'up' if UDC == 0 else 'down' if UDC == 1 else 'common'
        self.type = 'ml' if ML else 'loop'
        self.station = station
        self.allowedVehicles = '\"all\"'
        self.maxAllowedSpeed = 100.0 if ML else 15.0       # so no need to specify max allowed speed in file
        self.upLinks = []
        self.dnLinks = []
        self.speedRestrictions = []

    def addLink(self,linkBlock,direction):   # Block to be linked is known
        #assert if up then first digit of blockNum == stationCode
        #assert if down then first digit of blockNum == stationCode - 1
        print(f"linking a loopline: {self.num} at {linkBlock.num} in {direction}")
        if direction == 'up':
            self.upLinks.append({'link':linkBlock.num,'linkLength':0.0,'priority':len(self.upLinks)+1,'cross-over':'#'})
        elif direction == 'down':
            self.dnLinks.append({'link':linkBlock.num,'linkLength':0.0,'priority':len(self.dnLinks)+1,'cross-over':'#'})
        else:
            assert(0)

    def __str__(self):
        return str(self.num)


    def __repr__(self):
        # return str(self.num)
        #10001 up ml "Kanpur" all 100 "10010" "0.0" "1" "#" "" "" "" "" "" "" ""

        uplinkText = '"{}"'.format(','.join(list(map(str,[i['link'] for i in self.upLinks]))))
        uplinkLengthText = '"{}"'.format(','.join(list(map(str,[i['linkLength'] for i in self.upLinks]))))
        uplinkPriorityText = '"{}"'.format(','.join(list(map(str,[i['priority'] for i in self.upLinks]))))
        uplinkcrossoverText = '"{}"'.format(','.join(list(map(str,[i['cross-over'] for i in self.upLinks]))))

        dnlinkText = '"{}"'.format(','.join(list(map(str,[i['link'] for i in self.dnLinks]))))
        dnlinkLengthText = '"{}"'.format(','.join(list(map(str,[i['linkLength'] for i in self.dnLinks]))))
        dnlinkPriorityText = '"{}"'.format(','.join(list(map(str,[i['priority'] for i in self.dnLinks]))))
        dnlinkcrossoverText = '"{}"'.format(','.join(list(map(str,[i['cross-over'] for i in self.dnLinks]))))
        speedRestrictionText = '"" "" ""'

        return  ("{} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n").format(self.num,self.dir,self.type,self.station.name,
        self.allowedVehicles,int(self.maxAllowedSpeed),uplinkText,uplinkLengthText,uplinkPriorityText,uplinkcrossoverText,
        dnlinkText,dnlinkLengthText,dnlinkPriorityText,dnlinkcrossoverText,speedRestrictionText) #"Kanpur" 0.0 1.0 100.0

class Block():
    def __init__(self,prevStation,nextStation,UDC,startDist,endDist,maxAllowedSpeed=160,count=1):
        ML = True
        self.num = str(prevStation.stnCode)+str(UDC)+str(0 if ML else 1)+str(count)+'0'
        self.dir = 'up' if UDC == 0 else 'down' if UDC == 1 else 'common'
        self.prevStation = prevStation
        self.nextStation = nextStation
        self.startDist = startDist
        self.endDist = endDist
        self.maxAllowedSpeed = maxAllowedSpeed
        self.upLinks = []
        self.dnLinks = []
        self.speedRestrictions = []


        # CHANGE CODE:: up is converted to ! down to link all the loops of the nextlink

    def addLink(self,nextlink,direction):       # Next link may be a block or a station
        print(f"linking the block for {self.num} in {direction}")
        if isinstance(nextlink,Station):
            if direction == 'up':
                toBeLinkedLoops = [l for l in nextlink.loopList if l.dir != 'down'] # link common and up loops
                for l in toBeLinkedLoops:
                    self.upLinks.append({'link':l.num,'linkLength':0.0,'priority':len(self.upLinks)+1,'cross-over':'#'})
            elif direction == 'down':
                toBeLinkedLoops = [l for l in nextlink.loopList if l.dir != 'up']   # link common and down loops
                for l in toBeLinkedLoops:
                    self.dnLinks.append({'link':l.num,'linkLength':0.0,'priority':len(self.dnLinks)+1,'cross-over':'#'})
            else:
                assert(0)
        elif isinstance(nextlink,Block):
            if direction == 'up':
                self.upLinks.append({'link':nextlink.num,'linkLength':0.0,'priority':len(self.upLinks)+1,'cross-over':'#'})
            elif direction == 'down':
                self.dnLinks.append({'link':nextlink.num,'linkLength':0.0,'priority':len(self.dnLinks)+1,'cross-over':'#'})
            else:
                assert(0)
        else:
            assert(0)
    def __str__(self):
        return str(self.num)

    def __repr__(self):
        # return str(self.num)
        # 10010 up 1.0 3.37 100 "20001,20101" "0.0,0.0" "1,2" "#,#" "" "" "" "" "" "" ""
        uplinkText = '"{}"'.format(','.join(list(map(str,[i['link'] for i in self.upLinks]))))
        uplinkLengthText = '"{}"'.format(','.join(list(map(str,[i['linkLength'] for i in self.upLinks]))))
        uplinkPriorityText = '"{}"'.format(','.join(list(map(str,[i['priority'] for i in self.upLinks]))))
        uplinkcrossoverText = '"{}"'.format(','.join(list(map(str,[i['cross-over'] for i in self.upLinks]))))

        dnlinkText = '"{}"'.format(','.join(list(map(str,[i['link'] for i in self.dnLinks]))))
        dnlinkLengthText = '"{}"'.format(','.join(list(map(str,[i['linkLength'] for i in self.dnLinks]))))
        dnlinkPriorityText = '"{}"'.format(','.join(list(map(str,[i['priority'] for i in self.dnLinks]))))
        dnlinkcrossoverText = '"{}"'.format(','.join(list(map(str,[i['cross-over'] for i in self.dnLinks]))))
        SrSpeedText = '"{}"'.format(','.join(list(map(str,[i['speed'] for i in self.speedRestrictions]))))
        SrStartText = '"{}"'.format(','.join(list(map(str,[i['startkm'] for i in self.speedRestrictions]))))
        SrEndText = '"{}"'.format(','.join(list(map(str,[i['endkm'] for i in self.speedRestrictions]))))
        speedRestrictionText = '{} {} {}'.format(SrSpeedText,SrStartText,SrEndText)

        return  ("{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n").format(self.num,self.dir,self.startDist,self.endDist,
        int(self.maxAllowedSpeed),uplinkText,uplinkLengthText,uplinkPriorityText,uplinkcrossoverText,
        dnlinkText,dnlinkLengthText,dnlinkPriorityText,dnlinkcrossoverText,speedRestrictionText) #"Kanpur" 0.0 1.0 100.0
        # return  ("{} {} {} {} {} {} {} {}\n").format(self.num,self.dir,self.startDist,self.endDist,
        # int(self.maxAllowedSpeed),uplinkText,dnlinkText,speedRestrictionText) #"Kanpur" 0.0 1.0 100.0


class Network():
    def __init__(self):
        self.graph = nx.Graph()
        self.stationList = []
        self.blockList = []

    @property
    def loopList(self):
        return [l for s in self.stationList for l in s.loopList]

    def blockLength(self,blk):
        p,n=blk.split('-')
        start = [i.endDist for i in self.stationList if i.name==p][0]
        end = [i.startDist for i in self.stationList if i.name==n][0]
        return end-start

    def addStation(self,line,line_loops,stnSpeed,stnCode = None):     # CHANGE_CODE:: Add station with more loops than just ML
        if stnCode == None:
            stnCode = len(self.stationList)+1
            self.stationList.append(Station(line,line_loops,stnSpeed,stnCode))  # Add the basic station information as well as the loops(platforms) at a particular station
            self.graph.add_node(self.stationList[-1].name,station=self.stationList[-1])
        else:
            self.stationList.append(Station(line,line_loops,stnSpeed,stnCode))  # Add the basic station information as well as the loops(platforms) at a particular station
            self.graph.add_node(self.stationList[-1].name,station=self.stationList[-1])

    def addBlockPsr(self):
        allPSR = [(i,self.graph.edges[i]) for i in self.graph.edges if len(self.graph.edges[i]['PSR'])>0]
        for stns,edgeAll in allPSR:
            stnObjs = [i for i in self.stationList if i.name in stns]
            possibleStart = min([i.endDist for i in stnObjs])
            possibleEnds = max([i.startDist for i in stnObjs])

            for dir in ['up','down']:
                edge = [i for i in edgeAll['PSR'] if i.direction == dir]
                if len(edge)==0: continue
                if edge[0].distance > self.blockLength('-'.join(stns)):
                    if edge[0].direction == 'up':
                        for b in edgeAll['upBlocks']:
                            b.speedRestrictions.append({'speed':edge[0].maxSpeed,'startkm':0.0,'endkm':b.endDist-b.startDist})

                    elif edge[0].direction == 'down':
                        for b in edgeAll['dnBlocks']:
                            b.speedRestrictions.append({'speed':edge[0].maxSpeed,'startkm':0.0,'endkm':b.endDist-b.startDist})

                elif len(edge)==1:

                    srStart = (possibleStart + possibleEnds - edge[0].distance)/2.0
                    srEnd = (possibleStart + possibleEnds + edge[0].distance)/2.0

                    if edge[0].direction == 'up':
                        affectedBlocks = [b for b in edgeAll['upBlocks'] if (b.startDist > srStart and b.startDist < srEnd) or
                        (b.endDist > srStart and b.endDist < srEnd) or (b.startDist < srStart and b.endDist > srEnd)]

                        for b in affectedBlocks:
                            b.speedRestrictions.append({'speed':edge[0].maxSpeed,'startkm':max(0.0, srStart - b.startDist),
                            'endkm':min(b.endDist - b.startDist,srEnd - b.startDist)})

                    elif edge[0].direction == 'down':
                        affectedBlocks = [b for b in edgeAll['dnBlocks'] if (b.startDist > srStart and b.startDist < srEnd) or
                        (b.endDist > srStart and b.endDist < srEnd) or (b.startDist < srStart and b.endDist > srEnd)]

                        for b in affectedBlocks:
                            b.speedRestrictions.append({'speed':edge[0].maxSpeed,'startkm':max(0.0, srStart - b.startDist),
                            'endkm':min(b.endDist - b.startDist,srEnd - b.startDist)})

                else:
                    if sum([i.distance for i in edge]) >= self.blockLength('-'.join(stns)):
                        assert(0)
                        pass
                    else:
                        interimDistance = (self.blockLength('-'.join(stns)) - sum([i.distance for i in edge]))/(len(edge)+1)
                        srStart = possibleStart + interimDistance
                        for sr in edge:
                            srEnd = srStart+sr.distance

                            if sr.direction == 'up':
                                blkDir = 'upBlocks'
                            else:
                                blkDir = 'dnBlocks'

                            affectedBlocks = [b for b in edgeAll[blkDir] if (b.startDist > srStart and b.startDist < srEnd) or
                            (b.endDist > srStart and b.endDist < srEnd) or (b.startDist < srStart and b.endDist > srEnd)]

                            for b in affectedBlocks:
                                b.speedRestrictions.append({'speed':edge[0].maxSpeed,'startkm':max(0.0, srStart - b.startDist),
                                'endkm':min(b.endDist - b.startDist,srEnd - b.startDist)})

                            srStart = srEnd + interimDistance

    @property
    def stationDistance(self):
        df= pd.DataFrame(columns=['station','startFromNDLS','endFromNDLS','startFromMMCT','endFromMMCT'])
        df['station'] = [i.name for i in self.stationList]
        df['startFromNDLS'] = [i.startDist for i in self.stationList]
        df['endFromNDLS'] = [i.endDist for i in self.stationList]
        lastVal = df['endFromNDLS'].values[-1]
        df['startFromMMCT'] = lastVal - df['startFromNDLS']
        df['endFromMMCT'] = lastVal - df['endFromNDLS']
        return df

    def fillBlocks(self,DYheadWayDistance =1.2,minLength = 1.2,maxLength = 1.8,absoluteBlocks = [],singleLineBlocks=[]):
        for p,n in zip(self.stationList[:-1],self.stationList[1:]):
            if p.name+'-'+n.name in singleLineBlocks or n.name+'-'+p.name in singleLineBlocks:
                singleLine = True
            else:
                singleLine = False 


            dist = self.blockLength(p.name+'-'+n.name)
            if True:
                print('absoluteBlock!!',p.name+'-'+n.name,dist)
                DYheadWayDistance = dist
            else:
                blkLngt=list(range(np.ceil(dist/maxLength).astype(int),1+np.floor(dist/minLength).astype(int)))
                # print('automaticSignaling',p.name+'-'+n.name,blkLngt[0])
                if len(blkLngt)!=0:
                    print('automaticSignaling',p.name+'-'+n.name,blkLngt)
                    DYheadWayDistance = dist/blkLngt[0]
                else:
                    print('autoNosignal',p.name+'-'+n.name,dist)
                    DYheadWayDistance = dist
            print("dist:",dist,'blkLen:',DYheadWayDistance)
            maxAllowedUpSpeed = p.blkSpeed.UpMaxSpeed.values[0]
            maxAllowedDnSpeed = p.blkSpeed.DownMaxspeed.values[0]

            self.graph.add_edge(p.name,n.name,upBlocks=[],dnBlocks=[],PSR=[])
            startDist = p.endDist
            endDist = startDist+DYheadWayDistance
            prevLinkUp = p
            prevLinkDn = p
            count = 1

            while endDist < n.startDist-1:
                if not singleLine:
                    upBlock = Block(p,n,0,startDist,endDist,maxAllowedSpeed=maxAllowedUpSpeed,count = count)
                    dnBlock = Block(p,n,1,startDist,endDist,maxAllowedSpeed=maxAllowedDnSpeed,count = count)

                    self.blockList.append(upBlock)
                    self.blockList.append(dnBlock)

                    self.graph.edges[p.name,n.name]['upBlocks'].append(upBlock)
                    self.graph.edges[p.name,n.name]['dnBlocks'].append(dnBlock)
                else:
                    upBlock = Block(p,n,2,startDist,endDist,maxAllowedSpeed=maxAllowedUpSpeed,count = count)
                    dnBlock = upBlock

                    self.blockList.append(upBlock)

                    self.graph.edges[p.name,n.name]['upBlocks'].append(upBlock)


                prevLinkUp.addLink(upBlock,'up')         # org_stn->block1;...;blocki->blocki+1;terminalblock->next_stn
                dnBlock.addLink(prevLinkDn,'down')       # block1->org_stn;...;blocki+1->blocki;next_stn->terminalblock

                prevLinkUp = upBlock
                prevLinkDn = dnBlock

                startDist +=DYheadWayDistance
                endDist +=DYheadWayDistance
                count +=1

            if endDist >= n.startDist-1:
                if not singleLine:
                    upBlock = Block(p,n,0,startDist,n.startDist,maxAllowedSpeed=maxAllowedUpSpeed,count = count)
                    dnBlock = Block(p,n,1,startDist,n.startDist,maxAllowedSpeed=maxAllowedDnSpeed,count = count)

                    self.blockList.append(upBlock)
                    self.blockList.append(dnBlock)

                    self.graph.edges[p.name,n.name]['upBlocks'].append(upBlock)
                    self.graph.edges[p.name,n.name]['dnBlocks'].append(dnBlock)
                else:
                    upBlock = Block(p,n,2,startDist,n.startDist,maxAllowedSpeed=maxAllowedUpSpeed,count = count)
                    dnBlock = upBlock

                    self.blockList.append(upBlock)

                    self.graph.edges[p.name,n.name]['upBlocks'].append(upBlock)
                    
                prevLinkUp.addLink(upBlock,'up')
                dnBlock.addLink(prevLinkDn,'down')

                prevLinkUp = upBlock
                prevLinkDn = dnBlock

            prevLinkUp.addLink(n,'up')
            n.addLink(prevLinkDn,'down')

class BlockPsr():
    def __init__(self,values,direction='up'):
        assert(not pd.isna(values['MAVBLCKSCTN']))
        self.direction = direction
        self.section = str(values['MAVBLCKSCTN'])
        self._startKm = str(values['MANFROMKM'])
        self._endKm = str(values['MANTOKM'])
        self._startSubKm = str(values['MAVFROMSUBKM'])
        self._endSubKm = str(values['MAVTOSUBKM'])
        self.maxSpeed = str(values['MANPASSPEED'])
        self.dFlag = values['MACKMOHEFLAG']
        self.distance = abs(self.startkm-self.endkm)

        #self.updateSTNS(df)

    @property
    def startkm(self):
        if self._startKm.isnumeric():
            if self.dFlag == 'K':
                # return 1381.73 - (int(self._startKm)+(int(self._startSubKm)/100))
                return (float(self._startKm)+(float(self._startSubKm)/100))
            elif self.dFlag == 'O':
                # return 1381.73 - (float(self._startKm)+(float(float(self._startSubKm)/2.0)/18))
                return (float(self._startKm)+(float(float(self._startSubKm)/2.0)/18))
            else:
                assert(0)

        elif '/' in self._startKm:
            assert(float(self._startSubKm)==0.0)
            val = self._startKm.split('/')
            if not val[1].isnumeric(): val[1]=val[1][:-1]
            if self.dFlag == 'K':
                # return 1381.73 - (float(val[0])+(float(val[1])/100))
                return (float(val[0])+(float(val[1])/100))
            elif self.dFlag == 'O':
                # return 1381.73 - (float(val[0])+(float(float(val[1])/2.0)/18))
                return (float(val[0])+(float(float(val[1])/2.0)/18))
            else:
                assert(0)
        else:
            #assert(0)
            return 0

    @property
    def endkm(self):
        if self._endKm.isnumeric():
            # assert(self._startSubKm.isnumeric())
            if self.dFlag == 'K':
                # return 1381.73 - float(self._endKm)+(float(self._endSubKm)/100)
                return float(self._endKm)+(float(self._endSubKm)/100)
            elif self.dFlag == 'O':
                # return 1381.73 - float(self._endKm)+(float(float(self._endSubKm)/2.0)/18)
                return float(self._endKm)+(float(float(self._endSubKm)/2.0)/18)
            else:
                assert(0)

        elif '/' in self._endKm:
            assert(float(self._endSubKm)==0.0)
            val = self._endKm.split('/')
            if not val[1].isnumeric(): val[1]=val[1][:-1]
            if self.dFlag == 'K':
                # return 1381.73 - (float(val[0])+(float(val[1])/100))
                return (float(val[0])+(float(val[1])/100))
            elif self.dFlag == 'O':
                # return 1381.73 - (float(val[0])+(float(float(val[1])/2.0)/18))
                return (float(val[0])+(float(float(val[1])/2.0)/18))
            else:
                assert(0)
        else:
            #assert(0)
            return 0

    def updateSTNS(self,network):
        self.network = network
        stns = self.section.split('-')
        self.startStn = [i for i in self.network.stationList if i.name==stns[0]][0]
        self.endStn = [i for i in self.network.stationList if i.name==stns[1]][0]
        self.network.graph.edges[self.startStn.name,self.endStn.name]['PSR'].append(self)


    def __repr__(self):
        return str(self.section)


if __name__ == '__main__':
    with open(station_txt) as f:       # station file
        stationFile = f.readlines()

    # CHANGE_CODE; Read file generated by SID which is the station_loop file
    with open(looplist_txt) as g:
        station_loop_File = g.readlines()

    stnCodeDF = pd.read_csv(stnCode_csv)
    stnSpeed = pd.read_csv(stnSpeed_csv)
    # CHANGE CODE:: Note that the entries of the station file and the station_loop file must have
    # station codes in the same order so that loop lines are added accordingly

    stationList = [s.split()[0] for s in stationFile[2:]]
    # absoluteBlocksBetween = sorted(['NDLS','MMCT'],key = lambda x:stationList.index(x))
    # absoluteBlockStations = stationList[stationList.index(absoluteBlocksBetween[0]):stationList.index(absoluteBlocksBetween[1])]
    # allStationsPairsForAbsoluteBlock = [i+'-'+j for i,j in zip(absoluteBlockStations[:-1],absoluteBlockStations[1:])]
    allStationsPairsForAbsoluteBlock = []

    #singleLineBlocks = ['PDI-JBC','JBC-TKW','BGVN-JNTR','JNTR-PRWD','PRWD-WSB','WSB-PPJ','PPJ-JEUR','JEUR-BLNI','KUI-GDGN','GDGN-GUR','GUR-HHD','HHD-SVG','PUDI-SVF','SVF-TDK']
    singleLineBlocks = ['TDK-SVF','SVF-PUDI','SVG-HHD','HHD-GUR','GUR-GDGN','GDGN-KUI','BLNI-JEUR','JEUR-PPJ','PPJ-WSB','WSB-PRWD','PRWD-JNTR','JNTR-BGVN','TKW-JBC','JBC-PDI']
    N = Network()
    for line,line_loop in zip(stationFile[2:],station_loop_File[2:]):
        stnName = line.split(' ')[0]
        stnCode = stnCodeDF[stnCodeDF['Stations']==stnName].values[0][1]
        print('Station',stnName,'StnCode',stnCode)
        N.addStation(line,line_loop,stnSpeed,stnCode=stnCode)   # Add station to your network, default the UP and DOWN MAINLINES are added
    # Append station objects with given names to the network
    # Here loops of the station need to be added as well


    print("\n")
    print("Done adding Stations ")
    print("\n")

    N.fillBlocks(DYheadWayDistance = 1.2,absoluteBlocks=allStationsPairsForAbsoluteBlock,singleLineBlocks=singleLineBlocks)               # Fills blocks between the stations at a given headway distance

    stationDF = pd.read_csv(station_txt,sep=' ')
    # stnPsr = pd.read_csv('12951STATIONPSR.csv')
    blkPsr = pd.read_csv(blockpsr_12951)[['MAVBLCKSCTN','MANFROMKM','MANTOKM','MACKMOHEFLAG','MAVFROMSUBKM','MAVTOSUBKM','MANPASSPEED']].dropna().drop_duplicates()
    # stnPsr2 = pd.read_csv('12952STATIONPSR.csv')
    blkPsr2 = pd.read_csv(blockpsr_12952)[['MAVBLCKSCTN','MANFROMKM','MANTOKM','MACKMOHEFLAG','MAVFROMSUBKM','MAVTOSUBKM','MANPASSPEED']].dropna().drop_duplicates()

    print('adding speed restrictions')
    blockList = []
    # blockList2= []
    for i in range(blkPsr.shape[0]):
        blockList.append(BlockPsr(blkPsr.iloc[i],direction = 'down'))

    for i in range(blkPsr2.shape[0]):
        blockList.append(BlockPsr(blkPsr2.iloc[i],direction = 'up'))

    for b in blockList:
        print()
        b.updateSTNS(N)

    N.addBlockPsr()

    for p,n in zip(N.stationList[:-1],N.stationList[1:]):
        dist= N.blockLength(p.name+'-'+n.name)
        if dist>15:
            print('over 15')

    print("\nDone Filling Blocks\n")
    print('###################################################################')
    for n in N.stationList:
        print(n)
    print('###################################################################')
    with open('loop.txt','w') as l:
        l.write('/*Loop-Number	Direction	Type	Station-Code   	Type-of-Trains-allowed	Loop-Velocity(kmph)	Uplinks	Uplink-lengths(km)    Priority	Cross-over	Down-links	Downlink-Lengths(kmph)	Priority    Cross-over	Speed-Restriction(kmph)	Start-Mile-Post(km)	End-Mile-Post(km)*/\n\n')
        for n in N.loopList:
            l.write(repr(n))
            print(n)
    print('###################################################################')
    with open('block.txt','w') as b:
        b.write('/*Block-Number	Direction	Starting-Mile-Post(Km)	Ending-Mile-Post(Km)    Block-Velocity(kmph)	Uplinks	Up-Link-Length	Priority	Cross-over	Down-link    Down-Link-Length	Priority	Cross-over	Speed-Restrictions(kmph,kmph)    Starting-Mile-Posts(startkm1,startkm2)	Ending-Mile-Posts(endkm1,endkm2)*/\n\n')
        for n in N.blockList:
            b.write(repr(n))
            print(n)

