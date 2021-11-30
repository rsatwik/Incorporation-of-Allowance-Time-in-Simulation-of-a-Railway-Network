import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path to output files

########################################################################################################

print('Reading GQD data...')
gqdDF=pd.read_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress-StationCodes.csv',low_memory=False)
gqdDF=gqdDF.astype({'TRAIN': str})
gqdDF=gqdDF.set_index('TRAIN')

train_seq=pd.read_csv(outputPath+'cleaned_train_list2.csv')
train_seq=train_seq.astype({'Train_no': str})
train_seq=train_seq.set_index('Train_no')

trainData=pd.read_csv(outputPath+'ModifiedAndDailyTrains5.csv')
trainData['Direction']=0
trainData=trainData.astype({'Unnamed: 0': str})
trainData=trainData.set_index('Unnamed: 0')

print('Starting Direction Assignment....')

# directionAssignmentFailedTrains=[]
for train in tqdm(trainData.index.drop_duplicates()):
    actualTrain=(str(train)[-5:])
    # try:

    dftemp = gqdDF.loc[(actualTrain)].copy(deep=True)
    dftemp = dftemp[dftemp['SEQ'].isin(list(trainData.loc[train,'SEQ']))]
    dftemp['SerialNo']=list(range(0,dftemp.shape[0]))

    strt_seq=int(dftemp['SerialNo'][0])
    end_seq=int(dftemp['SerialNo'][-1])

    # strt_seq=int(dftemp['SEQ'][0])
    # end_seq=int(dftemp['SEQ'][-1])
    # assert strt_seq < end_seq
    
    i=strt_seq

    while (dftemp[dftemp['SerialNo']==i]['Stn. Code'].values[0])==10001:
        i+=1
    stationCodeStart=dftemp[dftemp['SerialNo']==i]['Stn. Code'].values[0]
    i+=1
    while (dftemp[dftemp['SerialNo']==i]['Stn. Code'].values[0])==10001:
        i+=1
    stationCodeNext=dftemp[dftemp['SerialNo']==i]['Stn. Code'].values[0]
    if stationCodeNext-stationCodeStart > 0:
        trainData.loc[train,'Direction']='up'
    elif stationCodeNext-stationCodeStart < 0:
        trainData.loc[train,'Direction']='down'
    elif stationCodeNext-stationCodeStart == 0:
        print('ERROR',train,'did not move between two stations sequences',stationCodeStart,':',stationCodeNext)
        sys.exit(1)

    # except:
        # directionAssignmentFailedTrains.append(train)
        # continue

# print('Direction Assignment failed for trains:')
# print(directionAssignmentFailedTrains)

trainData.to_csv(outputPath+'ModifiedAndDailyTrains6.csv')
