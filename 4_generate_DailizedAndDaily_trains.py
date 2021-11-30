import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to common files
outputPath='temporary_files/' # path to output files
infraPath='simulator_input/' # path to infra files

#print('1.NDLS-MMCT\n2.NDLS-MAS\n3.HWH-MAS\n4.CSMT-HWH\n5.CSMT-MAS\n6.NDLS-HWH\n')
if len(sys.argv) < 2:
    print(' Incorrect usage: give number as an argument:')
    print('   1.NDLS-MMCT \n   2.NDLS-MAS  \n   3.HWH-MAS  \n', \
                     '  4.CSMT-HWH  \n   5.CSMT-MAS  \n   6.NDLS-HWH')
    print(' Give the appropriate integer [1..6] as argument and run again.')
    sys.exit(1)

userInput=int(sys.argv[1])

########################################################################################################

stationTxtDF=pd.read_csv(infraPath+'station.txt',sep=' ',index_col=0)

cleanedTrainListDF=pd.read_csv(outputPath+'cleaned_train_list2.csv')
cleanedTrainListDF=cleanedTrainListDF.astype({'Train_no':str, 'simTrain_no':str})
cleanedTrainListDF.set_index(['Train_no','simTrain_no'],inplace=True)

gqdDF=pd.read_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress.csv',low_memory=False)
gqdDF=gqdDF.astype({'TRAIN': str})
gqdDF=gqdDF.set_index('TRAIN')

trainsToDeleteDF=pd.read_csv(outputPath+'trainsToDelete3.csv',header=None)
trainsToDeleteDF=trainsToDeleteDF.astype({0:str})
trainsToDeleteDF=trainsToDeleteDF.set_index(0)
trainsToDelete = trainsToDeleteDF.index.to_list()

df2=gqdDF.iloc[[0]].copy(deep=True)
df2=df2.drop(gqdDF.iloc[[0]].index[0])     # creates an empty dataframe df2

print("Reading cleaned train list")

# cleanedTrainListDF=cleanedTrainListDF[cleanedTrainListDF['Start_Sequence']!=0]

############ Creates longest sequence for the all non representative trains

print("Total Iterations : ",cleanedTrainListDF.shape[0])
for (train,simTrainNumber),row in tqdm(cleanedTrainListDF.iterrows()):
    # try:
        # actualTrainNo=str(row['Train_no'])
    startSeq=int(row['Start_Sequence'])
    endSeq=int(row['End_Sequence'])
    sequenceRange=list(range(startSeq,endSeq+1))
    dftemp=gqdDF.loc[train][gqdDF.loc[train]['SEQ'].isin(sequenceRange)].copy(deep=True)
    dftemp['NewTrain_no']=simTrainNumber
    dftemp.set_index('NewTrain_no',inplace=True)
    # print(dftemp.columns)
    df2 = pd.concat([df2,dftemp])
    del dftemp
    # except:
        # print("KeyError : ",train)
        # sys.exit(1)
        # continue

########### Creates the longest sequence for representative trains ####


## dailizedTrainsDF has data of representator train only
## All representated trains (including actual train number of representator train) go into trains to be deleted which will be removed

dailizedTrainsDF=pd.read_csv(outputPath+'dailizedTrains3.csv',index_col=[0])

for train in dailizedTrainsDF.index.drop_duplicates():
    actualTrainNo=str(train)[-5:]
    sequenceRange=[]

    for (index,simTrainNumber),row in cleanedTrainListDF[cleanedTrainListDF.index.to_frame()['Train_no']==actualTrainNo][['Start_Sequence','End_Sequence']].iterrows():
        startSeq=int(row['Start_Sequence'])
        endSeq=int(row['End_Sequence'])
        sequenceRange=list(range(startSeq,endSeq+1))
        dftemp=dailizedTrainsDF.loc[train][dailizedTrainsDF.loc[train]['SEQ'].isin(sequenceRange)].copy(deep=True)
        if dftemp.shape[0]!=0:
            newTrain_no=str(simTrainNumber)[0]+'9'+str(simTrainNumber)[2:]
            dftemp['NewTrain_no']=newTrain_no
            dftemp.set_index('NewTrain_no',inplace=True)
            cleanedTrainListDF.rename(index={simTrainNumber:newTrain_no},inplace=True)
            # cleanedTrainListDF.loc[index,'simTrain_no']=newTrain_no
            df2 = pd.concat([df2,dftemp])
            trainsToDelete.append(simTrainNumber)
        del dftemp

df2 = df2[~df2.index.isin(trainsToDelete)]

df2 = df2[df2.loc[:,'STATION'].isin(stationTxtDF.index.to_list())]

if userInput==2:
    for train in df2.index.drop_duplicates():
        exceptionStationsSet={'KCC','BZA'}
        df2StationSet=set(list(df2.loc[[train]]['STATION']))
        if df2StationSet.issubset(exceptionStationsSet):
            print(train,'runs only between BZA-KCC')
            trainsToDelete.append(train)
            continue

if userInput == 6 or userInput == 1 or userInput == 2:
    for train in df2.index.drop_duplicates():
        exceptionStationsSet1={'NDLS','CSB','TKJ'}
        df2StationSet=set(list(df2.loc[[train]]['STATION']))
        if df2StationSet.issubset(exceptionStationsSet1):
            print(train,'runs only between NDLS-CSB-TKJ')
            trainsToDelete.append(train)
            continue

if userInput == 5:
    for train in df2.index.drop_duplicates():
        exceptionStationsSet1={'MASB','BBQB'}
        df2StationSet=set(list(df2.loc[[train]]['STATION']))
        if df2StationSet.issubset(exceptionStationsSet1):
            print(train,'runs only between MASB-BBQB')
            trainsToDelete.append(train)
            continue

df2 = df2[~df2.index.isin(trainsToDelete)]

with open(outputPath+'trainsToDelete4.csv','w') as f:
    for train in trainsToDelete:
        f.write(str(train)+',')
        f.write('\n')

df2.to_csv(outputPath+'ModifiedAndDailyTrains4.csv')
cleanedTrainListDF.to_csv(outputPath+'cleaned_train_list4.csv')