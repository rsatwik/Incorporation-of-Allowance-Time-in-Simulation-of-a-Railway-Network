import pandas as pd
import numpy as np
import sympy as sym
import math
import sys
from collections import Counter
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path for output

#######################################################################################################

gqdDF=pd.read_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress.csv',low_memory=False)
gqdDF=gqdDF.astype({'TRAIN': str})
gqdDF=gqdDF.set_index('TRAIN')

exceptionStations=['BNDM','DBEC','GVN','KCAB','NNCN','STC','UDLE']
trainsToDelete=[]


route1loc='../1_NDLS-MMCT/simulator_input/'
route2loc='../2_NDLS-MAS/simulator_input/'
route3loc='../3_HWH-MAS/simulator_input/'
route4loc='../4_HWH-CSMT/simulator_input/'
route5loc='../5_MASB-CSMT/simulator_input/'
route6loc='../6_NDLS-HWH/simulator_input/'

route1Stations=list(pd.read_csv(route1loc+'station.txt',sep=' ',index_col=0).index)
route1StationsSet=set(route1Stations)

route2Stations=list(pd.read_csv(route2loc+'station.txt',sep=' ',index_col=0).index)
route2StationsSet=set(route2Stations)

route3Stations=list(pd.read_csv(route3loc+'station.txt',sep=' ',index_col=0).index)
route3StationsSet=set(route3Stations)

route4Stations=list(pd.read_csv(route4loc+'station.txt',sep=' ',index_col=0).index)
route4StationsSet=set(route4Stations)

route5Stations=list(pd.read_csv(route5loc+'station.txt',sep=' ',index_col=0).index)
route5StationsSet=set(route5Stations)

route6Stations=list(pd.read_csv(route6loc+'station.txt',sep=' ',index_col=0).index)
route6StationsSet=set(route6Stations)

listOfRoutes=[route1Stations,route2Stations,route3Stations,route4Stations,route5Stations,route6Stations]

trainsWithSequenceData=[]

removedList=[]






for train in gqdDF.index.drop_duplicates():
    if not train.isnumeric():
        continue
    if len(gqdDF.loc[[train]].index) < 3:
        trainsToDelete.append(train)
        print(train,'has less than 3 station in GQD data')
        continue
    trainStationsAll=list(gqdDF.loc[train,'STATION'])        
    # print(train)
    # print(trainStationsAll)
    # if len(trainStationsAll)-len(set(trainStationsAll))!=0:
        # print(train,'Stations repeated on same Route, possible Geoloops')
        # freqTable=Counter(trainStationsAll).most_common()
        # for station,freq in freqTable:
            # if freq>1: print(station,'Geoloops') 

        # sys.exit(1)
    trainStationsAllSet=set(trainStationsAll)

    exceptionStationsSet={'NDLS','CSB','TKJ','MWC','ANVR','CNJ','DSBP','SBB','GZB'}
    if trainStationsAllSet.issubset(exceptionStationsSet):
        print(train,'runs only between NDLS-GZB')
        trainsToDelete.append(train)
        continue
  
    exceptionStationsSet1={'SKG', 'GRP', 'BWN', 'TIT', 'KAN', 'GLI', 'PAJ', 'MNAE', 'PAN', 'RBH', 'DGR', 'DCOP', 'OYR', 'UDLE', 'UDL', 'BQT', 'RNG', 'NMC', 'KPK', 'ASNE', 'ASN', 'BCQ', 'STN'}
    if trainStationsAllSet.issubset(exceptionStationsSet1):
        print(train,'runs only between SKG-STN')
        trainsToDelete.append(train)
        continue

    exceptionStationsSet2={'JTHT', 'XCBN', 'ICBN', 'DDU', 'NEWC'}
    if trainStationsAllSet.issubset(exceptionStationsSet2):
        print(train,'runs only between JTHT-NEWC')
        trainsToDelete.append(train)
        continue

    exceptionStationsSet3={'AJJ','PLMG','MSU','TO','MAF','SPAM','KBT','EGT','TRL','PTLR','SVR','VEU','TI','NEC','PRWS','PAB','PRES','HC','AVD','ANNR','TMVL','ABU','PVM','KOTR','VLK','PEW','PCW','PER','VJM','VPY','BBQB'}
    if trainStationsAllSet.issubset(exceptionStationsSet3):
        print(train,'runs only between AJJ-BBQB')
        trainsToDelete.append(train)
        continue

    exceptionStationsSet4={'TNA','DIVA'}
    if trainStationsAllSet.issubset(exceptionStationsSet4):
        print(train,'runs only between TNA-DIVA')
        trainsToDelete.append(train)
        continue

    deleteTrains=[64076,64074,64902,64062,64908,64078,64012,64052,64014,64016,64904,64492,64082,64906,64910,64053,64905,64903,64071,64077,64055,64491,64901,64057,64013,64015,64017,64569,64073,64019,64051,11841] # deleted because of MTJ-PWL 3rd line
    deleteTrains+=[64101,64111,64109,64103,64105,64151,64160] # deleted because of NDLS-ALJN 3rd line
    deleteTrains+=[63141,63142,63501,63502] # deleted on NDLS-HWH route
    deleteTrains=map(str,deleteTrains)
    if train in deleteTrains:
        print(train, 'are deleted 3rd line trains')
        continue


    routeList=[]
    routeList.append(len(trainStationsAllSet.intersection(route1StationsSet)))
    routeList.append(len(trainStationsAllSet.intersection(route2StationsSet)))
    routeList.append(len(trainStationsAllSet.intersection(route3StationsSet)))
    routeList.append(len(trainStationsAllSet.intersection(route4StationsSet)))
    routeList.append(len(trainStationsAllSet.intersection(route5StationsSet)))
    routeList.append(len(trainStationsAllSet.intersection(route6StationsSet)))

    stationList=[]
    stationList.append(trainStationsAllSet.intersection(route1StationsSet))
    stationList.append(trainStationsAllSet.intersection(route2StationsSet))
    stationList.append(trainStationsAllSet.intersection(route3StationsSet))
    stationList.append(trainStationsAllSet.intersection(route4StationsSet))
    stationList.append(trainStationsAllSet.intersection(route5StationsSet))
    stationList.append(trainStationsAllSet.intersection(route6StationsSet))

    routeStationList=[]
    routeStationList.append(route1Stations)
    routeStationList.append(route2Stations)
    routeStationList.append(route3Stations)
    routeStationList.append(route4Stations)
    routeStationList.append(route5Stations)
    routeStationList.append(route6Stations)

    # possible=[[i,j] for i in range(len(routeList)) for j in range(len(routeList)) if i!=j]
    # for i,j in possible:
    #     print(train,i,stationList[i])
    #     if (stationList[i]).issubset(stationList[j]):
    #         routeList[i]=0
        
    selectedRoutes=sorted([[list(j),i[0]+1,k] for i,j,k in zip(enumerate(routeList),stationList,routeStationList) if i[1]!=0],key=lambda x:len(x[0]),reverse=True)
    
    for i in range(len(selectedRoutes)):
        for j in range(i+1,len(selectedRoutes)):
            selectedRoutes[j][0]=list(set(selectedRoutes[j][0])-set(selectedRoutes[i][0]))

    selectedRoutes = [i for i in selectedRoutes if len(i[0]) != 0]

    for pickedRoute, routeNumber, StationList  in selectedRoutes: 

        if len(pickedRoute)<5:
            print(train,'runs for less than 5 stations in route',routeNumber)
            continue
        
        dftemp=gqdDF.loc[train].copy(deep=True)

        dftemp=dftemp[dftemp['STATION'].isin(pickedRoute)]#+exceptionStations)]


        ##########################################################################################################

        # 1 arrange acc to SEQ
        # 2 find the start or end station SEQ
        # 3 truncated above or below accordingly

        dftemp=dftemp.sort_values(by='SEQ')

        if str(train) in ['19019','14211','12919'] and 'PWL' in dftemp['STATION'].to_list():
            endPoint=int(dftemp[dftemp['STATION']=='PWL']['SEQ'][0]) # find where  endstation
            # endPoint is integer and sequence number for that train, for PWL -Madhu
            print(train,'truncated')
            dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
            # getting rid of latter stations -Madhu
        if str(train) in ['12903','22209'] and 'MTJ' in dftemp['STATION'].to_list(): # end point change to PWL
            endPoint=int(dftemp[dftemp['STATION']=='MTJ']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
            print(train,'truncated')
        if str(train) in ['12926','11058','12904'] and 'MTJ' in dftemp['STATION'].to_list(): # starting point change to MTJ
            startPoint=int(dftemp[dftemp['STATION']=='MTJ']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
            print(train,'truncated')
            # overwrite

        #GZB-NZM
        if str(train) in ['19020','14318','14320','12172','12912','22918'] and 'NZM' in dftemp['STATION'].to_list(): # starting point change to MTJ
            startPoint=int(dftemp[dftemp['STATION']=='NZM']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
            print(train,'truncated')
        if str(train) in ['18237','14317','14319','12171','12911','22917']and 'NZM' in dftemp['STATION'].to_list():
            endPoint=int(dftemp[dftemp['STATION']=='NZM']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
            print(train,'truncated')

        # NDLS-ALJN
        if str(train) in ['14163','64581','64583','64168']and 'ALJN' in dftemp['STATION'].to_list():
            endPoint=int(dftemp[dftemp['STATION']=='ALJN']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
            print(train,'truncated')

        #HWH-CSMT
        if str(train) in ['66047'] and 'AJJ' in dftemp['STATION'].to_list():
            endPoint=int(dftemp[dftemp['STATION']=='AJJ']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
            print(train,'truncated')
        if str(train) in ['66048'] and 'AJJ' in dftemp['STATION'].to_list():
            startPoint=int(dftemp[dftemp['STATION']=='AJJ']['SEQ'][0])
            dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
            print(train,'truncated') 
        

        truncationDisabled=True

        if not truncationDisabled:
            #STN-SKG
            if str(train) in ['22387'] and 'STN' in dftemp['STATION'].to_list():
                startPoint=int(dftemp[dftemp['STATION']=='STN']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
                print(train,'truncated')
            if str(train) in ['919607'] and 'STN' in dftemp['STATION'].to_list():
                startPoint=int(dftemp[dftemp['STATION']=='STN']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
                print(train,'truncated')
            if str(train) in ['22388'] and 'ALJN' in dftemp['STATION'].to_list():
                endPoint=int(dftemp[dftemp['STATION']=='ALJN']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
                print(train,'truncated')
            if str(train) in ['13009'] and 'STN' in dftemp['STATION'].to_list() and 'JTHT' in dftemp['STATION'].to_list():
                startPoint=int(dftemp[dftemp['STATION']=='STN']['SEQ'][0])
                endPoint=int(dftemp[dftemp['STATION']=='JTHT']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,endPoint+1))]
                print(train,'truncated')
            if str(train) in ['13010'] and 'STN' in dftemp['STATION'].to_list() and 'JTHT' in dftemp['STATION'].to_list():
                startPoint=int(dftemp[dftemp['STATION']=='JTHT']['SEQ'][0])
                endPoint=int(dftemp[dftemp['STATION']=='STN']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,endPoint+1))]
                print(train,'truncated')

        
        #### Train removed due to exceptions
        #### 13239
        ####13239
        ####13240
        ####13240
        ####22971
        #### 18238
        #### 18477
        #### 18478
        ####12141
        ####12142
        ####12519
        ####16359
        ####16360
        ####12335
        ####12336
        ####15547
        ####15548
        
            #NEWC-JTHT
            if str(train) in ['12149','12947','15631','25631','13008','12424','12310','12436','22406','12236','12318','12316','12326','12368','19421','12394','12392','13258','12304','63264','22352','14006','12578','15635','11106','15667','15125','20802','63234','12741','13424','19063','14004','14008','14016','22947','13134','13120','13430','15564','15956','22450','14038','14020','12546','82356','12362','19313','19321','12328','12370','63228','22356','13414','13484','63226','13238','19669','12356','13006','12506','54272','22913','12334','12396','12488','13050','15484','17610','12332','12274','22466','20504','20506','15623'] and 'NEWC' in dftemp['STATION'].to_list():
                endPoint=int(dftemp[dftemp['STATION']=='NEWC']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
                print(train,'truncated')
            if str(train) in ['12150','12948','15632','25632','13007','12423','12309','12435','22405','12235','12317','12315','12325','12367','19422','12393','12391','13257','12303','63263','22351','14005','12577','15636','11105','15668','15126','20801','63233','12742','12520','13423','22353','19064','14003','14007','14015','22948','13133','13119','13429','15563','15955','22449','14037','14019','12545','82355','12361','19314','19322','12327','12369','63227','22355','13413','13483','63225','13237','19670','12355','13005','12505','54271','22914','12333','12395','12487','13049','15483','17609','22972','12331','12273','22465','20503','20505','15624'] and 'NEWC' in dftemp['STATION'].to_list():
                startPoint=int(dftemp[dftemp['STATION']=='NEWC']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
                print(train,'truncated')
            if str(train) in ['13307','18609','12875','18103','14223','18631','18611','18311','15021','63557','12371','12353','12381','63553','11046','12357','13167','13151'] and 'JTHT' in dftemp['STATION'].to_list():
                endPoint=int(dftemp[dftemp['STATION']=='JTHT']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
                print(train,'truncated')
            if str(train) in ['13308','18610','12876','18104','14224','18632','18612','18312','15022','63558','12372','12354','12382','63554','11045','12358','13152'] and 'JTHT' in dftemp['STATION'].to_list():
                startPoint=int(dftemp[dftemp['STATION']=='JTHT']['SEQ'][0])
                dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
                print(train,'truncated')

        ##########################################################################################################

        dftemp['SerialNo']=list(range(0,dftemp.shape[0]))

        freqTable=Counter(list(dftemp['STATION'])).most_common()
        for station,freq in freqTable:
            if freq>1:
                print('Resolving',train,'for Geoloops') 
                if station not in pickedRoute:
                    continue
                start = dftemp[dftemp['STATION']==station]['SerialNo'].to_list()[0]
                end = dftemp[dftemp['STATION']==station]['SerialNo'].to_list()[1]
                if abs(end-start)<=2:
                    if (start+end)/2 < dftemp.shape[0]/2:
                        dftemp=dftemp[dftemp['SerialNo'] >= (start+end)/2]
                    elif (start+end)/2 > dftemp.shape[0]/2:
                        dftemp=dftemp[dftemp['SerialNo'] <= (start+end)/2]
                    else:
                        assert 0, 'U turn detected'
                    del dftemp['SerialNo']
        
        freqTable=Counter(list(dftemp['STATION'])).most_common()
        for station,freq in freqTable:
            if freq>1: 
                print('Deleting',train,'****')
                # print(train,station,'Geoloops',dftemp[dftemp['STATION']==station]['SerialNo'].to_list(),any(dftemp[dftemp['STATION']==station]['SerialNo'].isin([0,1,dftemp.shape[0]-1,dftemp.shape[0]-2])),dftemp.shape[0])
                trainsToDelete.append(train)


        dftemp['SerialNo']=list(range(0,dftemp.shape[0]))

        trainStations=[(StationList.index(i),j) for i,j in dftemp[dftemp['STATION'].isin(pickedRoute)][['STATION','SerialNo']].values]

        stationJumps = [(i[1],abs(j[0]-i[0])) for i,j in zip(trainStations[:-1],trainStations[1:]) if not abs(j[0]-i[0])<5]

        gqdJumps = [(indI,j-i) for (indI,i),j in zip(enumerate(dftemp['SEQ'].to_list()[:-1]),dftemp['SEQ'].to_list()[1:]) if not abs(j-i)<5]

        sequenceJumps=sorted([-1]+list(set([i[0] for i in gqdJumps]).union([i[0] for i in stationJumps]))+[dftemp.shape[0]-1])

        if len(sequenceJumps)>2:
            for start,end in [(i+1,j+1) for i,j in zip(sequenceJumps[:-1],sequenceJumps[1:])]:
                dftemp2=dftemp[dftemp['SerialNo'].isin(range(start,end))]
                startSeq=list(dftemp2['SEQ'])[0]
                endSeq=list(dftemp2['SEQ'])[-1]
                temp={'Train_no':train,'Start_Sequence':startSeq,'End_Sequence':endSeq,'Route_no':int(routeNumber)}
                if (dftemp2.shape[0])<5:
                    print(train,'sequence stretch is less than 5 between sequence',startSeq,endSeq)
                    continue
                trainsWithSequenceData.append(temp)
        else:
            startSeq=list(dftemp['SEQ'])[0]
            endSeq=list(dftemp['SEQ'])[-1]
            temp={'Train_no':train,'Start_Sequence':startSeq,'End_Sequence':endSeq,'Route_no':int(routeNumber)}
            trainsWithSequenceData.append(temp)

sequence_df = pd.DataFrame(trainsWithSequenceData)
print(sequence_df,'sequence_df')
# sequence_df.reset_index(level=sequence_df.index.names, inplace=True)
# sequence_df.rename(columns={'index':'Train_no'},inplace=True)

sequence_df['simTrain_no'] = None

for train in sequence_df.Train_no.unique():
    dftemp=sequence_df[sequence_df.loc[:,'Train_no']==train].copy(deep=True)
    dftemp.sort_values('Start_Sequence',inplace=True)
    for i,(indx,row) in enumerate(dftemp.iterrows()):
        sequence_df.loc[indx,'simTrain_no']=str(i+1)+'0'+str(train)


sequence_df.to_csv(outputPath+'cleaned_train_list1.csv',index=False)

with open(outputPath+'trainsToDelete1.csv','w') as f:
    for train in trainsToDelete:
        f.write(str(train)+',')
        f.write('\n')



# if len(dftemp['STATION'].to_list())<4: # the longest sequence has 5 stations 
#         print(train,'has less than 5 stations in the GQD data')
#         trainsToDelete.append(train)
#         continue
#     # if len(dftemp['STATION'].to_list())<10:

    # exceptionStationsSet={'NDLS','CSB','TKJ','MWC','ANVR','CNJ','DSBP','SBB','GZB'}
    # dftempStationSet=set(dftemp['STATION'].to_list())
    # if dftempStationSet.issubset(exceptionStationsSet):
    #     print(train,'runs only between NDLS-GZB')
    #     trainsToDelete.append(train)
    #     continue
  
    # exceptionStationsSet1={'SKG', 'GRP', 'BWN', 'TIT', 'KAN', 'GLI', 'PAJ', 'MNAE', 'PAN', 'RBH', 'DGR', 'DCOP', 'OYR', 'UDLE', 'UDL', 'BQT', 'RNG', 'NMC', 'KPK', 'ASNE', 'ASN', 'BCQ', 'STN'}
    # dftempStationSet=set(dftemp['STATION'].to_list())
    # if dftempStationSet.issubset(exceptionStationsSet1):
    #     print(train,'runs only between SKG-STN')
    #     trainsToDelete.append(train)
    #     continue

    # exceptionStationsSet2={'JTHT', 'XCBN', 'ICBN', 'DDU', 'NEWC'}
    # dftempStationSet=set(dftemp['STATION'].to_list())
    # if dftempStationSet.issubset(exceptionStationsSet2):
    #     print(train,'runs only between JTHT-NEWC')
    #     trainsToDelete.append(train)
    #     continue

    # exceptionStationsSet3={'AJJ','PLMG','MSU','TO','MAF','SPAM','KBT','EGT','TRL','PTLR','SVR','VEU','TI','NEC','PRWS','PAB','PRES','HC','AVD','ANNR','TMVL','ABU','PVM','KOTR','VLK','PEW','PCW','PER','VJM','VPY','BBQB'}
    # dftempStationSet=set(dftemp['STATION'].to_list())
    # if dftempStationSet.issubset(exceptionStationsSet3):
    #     print(train,'runs only between AJJ-BBQB')
    #     trainsToDelete.append(train)
    #     continue
