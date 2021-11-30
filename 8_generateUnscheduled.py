import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path to output files


#print('1.NDLS-MMCT\n2.NDLS-MAS\n3.HWH-MAS\n4.CSMT-HWH\n5.CSMT-MAS\n6.NDLS-HWH\n')
if len(sys.argv) < 2:
    print(' Incorrect usage: give number as an argument:')
    print('   1.NDLS-MMCT \n   2.NDLS-MAS  \n   3.HWH-MAS  \n', \
                     '  4.CSMT-HWH  \n   5.CSMT-MAS  \n   6.NDLS-HWH')
    print(' Give the appropriate integer [1..6] as argument and run again.')
    sys.exit(1)

userInput=int(sys.argv[1])
'''
if userInput == 1:
    infraPath='simulator_input/1_NDLS-MMCT/' # path to infrastructure
elif userInput == 2:
    infraPath='simulator_input/2_NDLS-MAS/' # path to infrastructure
elif userInput == 3:
    infraPath='simulator_input/3_HWH-MAS/' # path to infrastructure
elif userInput == 4:
    infraPath='simulator_input/4_HWH-CSMT/' # path to infrastructure
elif userInput == 5:
    infraPath='simulator_input/5_MASB-CSMT/' # path to infrastructure
elif userInput == 6:
    infraPath='simulator_input/6_NDLS-HWH/' # path to infrastructure
'''

infraPath='simulator_input/'
#####################################################################################################################

loopTxtDF=pd.read_table(infraPath+'loop.txt',sep=' ',skiprows=[0],header=None,index_col=3)
loopTxtDF=loopTxtDF[loopTxtDF.loc[:,2]=='ml']

trainSpeedDF=pd.read_excel(inputPath+'Train-priorities-MPS-accln-decln.xlsx',sheet_name='GQD Trains',skiprows=[0],index_col='TRAIN')

accDecValuesloss_Sid=pd.read_excel(inputPath+'Allowance-Distribution-April2020-Delhi-Mumbai.xlsx',sheet_name='Accln-Time-Values')

cleanedTrainListDF=pd.read_csv(outputPath+'cleaned_train_list4.csv')
cleanedTrainListDF=cleanedTrainListDF.astype({'Train_no':str, 'simTrain_no':str})
cleanedTrainListDF.set_index('simTrain_no',inplace=True)

stationTxtDF=pd.read_csv(infraPath+'station.txt',sep=' ',index_col=0)

#differentAllowanceDF=pd.read_csv(inputPath+'TrainsWithDifferentAllowance.csv')
#differentAllowanceDF=differentAllowanceDF.astype({'TrainNo': str})
#differentAllowanceDF=differentAllowanceDF.set_index('TrainNo')

differentAllowanceDF=pd.read_csv(inputPath+'TrainsWithDifferentAllowance.csv')
differentAllowanceDF['stn1']=None
differentAllowanceDF['stn2']=None

for indx,row in differentAllowanceDF.iterrows():
    if (row['IC-StationsPairs']=='REST') or (row['IC-StationsPairs']=='ALL'):
        continue
    station1=row['IC-StationsPairs'].split('-')[0]
    station2=row['IC-StationsPairs'].split('-')[1]
    differentAllowanceDF.loc[indx,'stn1']=station1
    differentAllowanceDF.loc[indx,'stn2']=station2

deleteAllowanceInfo=[]
for indx,row in differentAllowanceDF.iterrows():
    if (row['IC-StationsPairs']=='REST') or (row['IC-StationsPairs']=='ALL'):
        continue
    stn1=row['stn1']
    stn2=row['stn2']
    if not ((stn1 in stationTxtDF.index) and (stn2 in stationTxtDF.index)):
        deleteAllowanceInfo.append(indx)

differentAllowanceDF=differentAllowanceDF[~differentAllowanceDF.index.isin(deleteAllowanceInfo)]

differentAllowanceDF=differentAllowanceDF.astype({'TrainNo': str})
differentAllowanceDF=differentAllowanceDF.set_index('TrainNo')
del differentAllowanceDF['stn1']
del differentAllowanceDF['stn2']


df2=pd.read_csv(outputPath+'ModifiedAndDailyTrains6.csv')
df2=df2.astype({'Unnamed: 0':str})
df2=df2.set_index('Unnamed: 0')

icstationsDF=pd.read_excel('https://docs.google.com/spreadsheets/d/1pByhSnYrp28WT0X7P_BMaYItBhNDZKbc8x16Oc2yRhE/export?format=xlsx&id=1pByhSnYrp28WT0X7P_BMaYItBhNDZKbc8x16Oc2yRhE',sheet_name='IC-points',index_col='StationCode')

icstationsDF=icstationsDF[icstationsDF['allowanceStation']=='yes']

icstations=[]
for station in icstationsDF.index.to_list():
    if type(station)==str:
        station=station.upper()
        icstations.append(station)

icstations = list(set(icstations))

print('Total number of IC stations :',len(icstations))

df2=df2[df2['STATION'].isin(stationTxtDF.index)]

maxHeader=0
unscheduled=[]
allwnDetails=[]
cleantraindata=df2.index.drop_duplicates()
trainsWithDifferentAllowance=differentAllowanceDF.index.drop_duplicates().to_list()

for runningDay in range(1,4):
    print('Running Day {0}...'.format(runningDay))
    for train in cleantraindata:

        length=str(0.5) # length of train

        try:
            actualTrainNo=int(str(train)[-5:])# if (str(train)[0]=='9')&(len(str(train))==6) else int(train)
        except ValueError:
            print('cannot find actual train number for:',train)
            continue

        try:
            direction=df2.loc[[train]]['Direction'].values[0]
        except KeyError:
            print('\n**Could not find direction for',train)
            sys.exit(1)

        try:
            maxSpeed=str(trainSpeedDF.loc[actualTrainNo]['MPS'])
            if maxSpeed=='130':
                maxSpeed='128'
            if maxSpeed=='110':
                maxSpeed='108'
            typeOfTrain=str(trainSpeedDF.loc[actualTrainNo]['Train-type'])
            acc=str(trainSpeedDF.loc[actualTrainNo]['Acceleration'])
            dec=str(trainSpeedDF.loc[actualTrainNo]['Deceleration'])
            priority=str(int(trainSpeedDF.loc[actualTrainNo]['priority']))
        except Exception as e:
            print(e.__class__,'occurred for',actualTrainNo)
            # print('\n**Missing all details in MPS file for',actualTrainNo)
            sys.exit(1)
            # continue

        try:
            #dftemp=(df2.loc[[train]].sort_values(by='DPRT')).copy(deep=True)
            dftemp=(df2.loc[[train]].sort_values(by='SEQ')).copy(deep=True)
        except Exception as e:
            print(e.__class__,'**Could not make dftemp**',train)
            sys.exit(1)


        if dftemp['STPG'].values[0]!=0:  # initial halt is made zero
            dftemp.loc[:,'STPG'].values[0]=0

        dftemp['SerialNo']=list(range(0,dftemp.shape[0]))
        icindx=list(dftemp[dftemp['STATION'].isin(icstations)]['SerialNo'].values)
        icindxStations=dftemp[dftemp['STATION'].isin(icstations)]['STATION'].values
        allwnStation=[]
        allwnStation.append(train)
       #### allowance calculations
        ## try:
        scalingFactorTimesub=0.7
        if str(actualTrainNo) not in trainsWithDifferentAllowance:
            dftemp=dftemp.set_index('SerialNo')
            previndx=0
            prevdist=stationTxtDF.loc[dftemp.iloc[0]['STATION']]['startKM']

            lastStationNotIC=0

            # if not dftemp['STATION'].to_list()[-1] in icindxStations:
                # lastStationNotIC=1
                # icindx+=[dftemp.shape[0]-1]

            for num,i in enumerate(icindx):
                icStationCode=dftemp.loc[i]['STATION']
                i=i+1
                var=np.zeros(dftemp.shape[0]).astype(bool)
                var[previndx:i]=True
                engAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((cleanedTrainListDF.loc[str(train)]['EAminsPer100km'])*60)/100)
                trafficAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((cleanedTrainListDF.loc[str(train)]['TAminsPer100km'])*60)/100)
                allowance = engAllowance+trafficAllowance  # 8 mins per 100km logic

                accDecTemp=accDecValuesloss_Sid[accDecValuesloss_Sid['train_speed(kmph)']==int(maxSpeed)].copy(deep=True)
                timesub=accDecTemp[accDecTemp['acc(m/s2)']==float(acc)]['NetTimeIncreaseDueToHaltInsteadOfConstantSpeed'].values[0]
                timesub=timesub*scalingFactorTimesub

                numberOfStations=0 if allowance==0 else 1 if allowance <= 8*60 else 2 if allowance<=12*60 else 3 if allowance<=16*60 else 4
                if not(allowance):
                    previndx=i
                    continue
                ichaltflag=(dftemp.iloc[i-1]['STPG'])!=0
    ##             if ichaltflag:
    ##                 var1=0
    ##             else:
                var1=1
                if num == len(icindx)-1 and lastStationNotIC:
                    var1=0

                if i-var1-previndx<numberOfStations:
                    numberOfStations=i-var1-previndx
                var=np.zeros(dftemp.shape[0]).astype(bool)
                var[i-var1-numberOfStations:i-var1]=True
                zeroHalts=dftemp[var][dftemp[var]['STPG']==0].shape[0]
                allowance=max(0,allowance-(zeroHalts)*timesub)
                for k in range(i-var1-numberOfStations,i-var1):
                    dftemp.loc[k,'STPG']=dftemp.loc[k,'STPG']+allowance/numberOfStations
                    # allwnStation.append(dftemp.loc[k,'STATION'])
                    allwnStation.append(allowance/numberOfStations)
                previndx=i
                prevdist=stationTxtDF.loc[dftemp.iloc[i-1]['STATION']]['startKM']

        else:
            print('assigning different allowance to',train)
            dftemp=dftemp.set_index('SerialNo')
            previndx=0
            prevdist=stationTxtDF.loc[dftemp.iloc[0]['STATION']]['startKM']

            trainAllowanceDF=differentAllowanceDF.loc[[str(actualTrainNo)]].copy(deep=True)
            isALL=0
            isREST=0
            if trainAllowanceDF['IC-StationsPairs'].values[0]=='ALL':
                isALL=1
            if not isALL:
                trainAllowanceDF['AllowanceSerialNo']=list(range(0,trainAllowanceDF.shape[0]))
                trainAllowanceDF['icIndex']=None
                trainAllowanceDF['TrainNo']=trainAllowanceDF.index
                trainAllowanceDF=trainAllowanceDF.set_index('AllowanceSerialNo')
                trainAllowanceDF['icIndex1']=None
                trainAllowanceDF['icIndex2']=None
                for indx,row in trainAllowanceDF.iterrows():
                    if row['IC-StationsPairs']!='REST':
                        startIC=row['IC-StationsPairs'].split('-')[0]
                        endIC=row['IC-StationsPairs'].split('-')[1]
                        startICindx=dftemp[dftemp['STATION']==startIC].index[0]
                        trainAllowanceDF.loc[indx,'icIndex1']=startICindx
                        endICindx=dftemp[dftemp['STATION']==endIC].index[0]
                        trainAllowanceDF.loc[indx,'icIndex2']=endICindx
                        trainAllowanceDF.loc[indx,'icIndex']=max(startICindx,endICindx)
                    elif row['IC-StationsPairs']=='REST':
                        isREST=1
                        trainAllowanceDF.loc[indx,'icIndex']=100000


                trainAllowanceDF=trainAllowanceDF.set_index('icIndex')
                if isREST:
                    modifiedAllowanceStations=[]
                    for indx in trainAllowanceDF.index.to_list():
                        if indx != 100000:
                            modifiedAllowanceStations.append(indx)

            # if isREST or isALL:
                # if not dftemp['STATION'].to_list()[-1] in icindxStations:
                    # lastStationNotIC=1
                    # icindx+=[dftemp.shape[0]-1]

            for num,i in enumerate(icindx):
                icStationCode=dftemp.loc[i]['STATION']
                i=i+1
                var=np.zeros(dftemp.shape[0]).astype(bool)
                var[previndx:i]=True
                if not isALL:
                    if dftemp.index[0]==i-1:  ## if starting station is an ic point, this if check is added because trainAllowanceDF has no index at starting ic point
                        engAllowance=0
                        trafficAllowance=0
                    elif not isREST:                     ## if starting station is not an ic point
                        engAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((trainAllowanceDF.loc[i-1]['EAper100km'])*60)/100)
                        trafficAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((trainAllowanceDF.loc[i-1]['TAper100km'])*60)/100)
                    else: ## if REST is one of the entry in the data fram
                        if i-1 in modifiedAllowanceStations:
                            engAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((trainAllowanceDF.loc[i-1]['EAper100km'])*60)/100)
                            trafficAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((trainAllowanceDF.loc[i-1]['TAper100km'])*60)/100)
                        else:
                            # print('isREST',isREST)
                            engAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((trainAllowanceDF.loc[100000]['EAper100km'])*60)/100)
                            trafficAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((trainAllowanceDF.loc[100000]['TAper100km'])*60)/100)


                if isALL:
                    # print('isALL',isALL)
                    engAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((differentAllowanceDF.loc[str(actualTrainNo)]['EAper100km'])*60)/100)
                    trafficAllowance=abs(stationTxtDF.loc[dftemp[var].iloc[-1]['STATION']]['startKM']-prevdist)*(((differentAllowanceDF.loc[str(actualTrainNo)]['TAper100km'])*60)/100)


                allowance = engAllowance+trafficAllowance  # 8 mins per 100km logic

                accDecTemp=accDecValuesloss_Sid[accDecValuesloss_Sid['train_speed(kmph)']==int(maxSpeed)].copy(deep=True)
                timesub=accDecTemp[accDecTemp['acc(m/s2)']==float(acc)]['NetTimeIncreaseDueToHaltInsteadOfConstantSpeed'].values[0]
                timesub=timesub*scalingFactorTimesub

                numberOfStations=0 if allowance==0 else 1 if allowance <= 8*60 else 2 if allowance<=12*60 else 3 if allowance<=16*60 else 4
                if not(allowance):
                    previndx=i
                    continue
                ichaltflag=(dftemp.iloc[i-1]['STPG'])!=0
    ##             if ichaltflag:
    ##                 var1=0
    ##             else:
                var1=1
                if num == len(icindx)-1 and lastStationNotIC:
                    var1=0

                if i-var1-previndx<numberOfStations:
                    numberOfStations=i-var1-previndx
                var=np.zeros(dftemp.shape[0]).astype(bool)
                var[i-var1-numberOfStations:i-var1]=True
                zeroHalts=dftemp[var][dftemp[var]['STPG']==0].shape[0]
                allowance=max(0,allowance-(zeroHalts)*timesub)
                for k in range(i-var1-numberOfStations,i-var1):
                    dftemp.loc[k,'STPG']=dftemp.loc[k,'STPG']+allowance/numberOfStations
                    # allwnStation.append(dftemp.loc[k,'STATION'])
                    allwnStation.append(allowance/numberOfStations)
                previndx=i
                prevdist=stationTxtDF.loc[dftemp.iloc[i-1]['STATION']]['startKM']

        ## except:
            ## print('\n**Could not calculate allowance for',train)
            ## continue

        ####>>>>>>>>>>>>>>>> extract Last station and last ic station and find the allowance deficit and add 

        allwnDetails.append(allwnStation)

        startTime=list(dftemp['DPRT'])[0]

        temp=int(startTime)
        temp = temp%86400
        assert(temp < 86400)

        startTime=temp+(24*60*60*(runningDay-1))

        startStation=list(dftemp['STATION'])[0]

        endStation=list(dftemp['STATION'])[-1]

        try:
            startLoop=str(loopTxtDF.loc[startStation][loopTxtDF.loc[startStation,1]==direction][0].values[0])
        except KeyError:
            print('\n**Loop not found for {0} for {1}'.format(startStation,train))
            continue
        try:
            endLoop=str(loopTxtDF.loc[endStation][loopTxtDF.loc[endStation,1]==direction][0].values[0])
        except KeyError:
            print('\n**Loop not found for {0} for {1}'.format(endStation,train))
            continue


        dftemp=dftemp[dftemp['STPG']!=0]  # keeping data of stations with only halts

        NoOfHalts=str(dftemp.shape[0])

        if int(NoOfHalts)>maxHeader:
            maxHeader=int(NoOfHalts)


        trainNo=str(runningDay)+str(train) #if (str(train)[1]=='9') else str(runningDay)+'0'+str(train)
        string=str(trainNo)
        string=string+' '+direction+' '+str(int(startTime/60))+' '+length+' '+str(acc)+' '+str(dec)+' '+priority+' '+maxSpeed+' '+startLoop+' '+endLoop+' '+NoOfHalts

        for sno,row in dftemp.iterrows():
            string+=' '
            string+=str(row['STATION'])
            string+=' '
            string+=str(float(round(Decimal(min(row['STPG']/60,30)),2)))

        unscheduled.append(string)
#         del dftemp

header='/*TrainNo. direction startTime(minutes) length(km) acceleration(m/s^2) deceleration(m/s^2) priority maximumSpeed(kmph) startLoop endLoop NumberOfHalts'
for i in range(0,maxHeader):
    header+=' '
    header+='Station'
    header+=' '
    header+='Halt(minutes)'

header+='*/'

from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%m-%d-%HH%MM")

print('Writing unscheduled...')

if userInput == 1:
    routename='NDLS-MMCT'
elif userInput == 2:
    routename='NDLS-MAS'
elif userInput == 3:
    routename='HWH-MAS'
elif userInput == 4:
    routename='HWH-CSMT'
elif userInput == 5:
    routename='CSMT-MASB'
elif userInput == 6:
    routename='NDLS-HWH'

name=infraPath+'unscheduled1' #+'-'+dt_string+'-'+routename

print('--> writing '+name+'.txt')

with open(name+'.txt','w') as n:
    n.write(header)
    n.write('\n')
    for u in unscheduled:
        n.write('\n')
        n.write(u)

with open(outputPath + 'Allowance8'+'.txt','w') as n:
    for u in allwnDetails:
        n.write('\n')
        for i in u:
            n.write(str(i))
            n.write(',')

# print('--> writing '+name+'.csv')
# temp=pd.read_table(name+'.txt',sep=' ')
# temp.to_csv(name+'.csv',index=False)
