import pandas as pd

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path to output files

# if len(sys.argv) < 2:
#     print(' Incorrect usage: give number as an argument:')
#     print('   1.NDLS-MMCT \n   2.NDLS-MAS  \n   3.HWH-MAS  \n', \
#                      '  4.CSMT-HWH  \n   5.CSMT-MAS  \n   6.NDLS-HWH')
#     print(' Give the appropriate integer [1..6] as argument and run again.')
#     sys.exit(1)

#print('1.NDLS-MMCT\n2.NDLS-MAS\n3.HWH-MAS\n4.CSMT-HWH\n5.CSMT-MAS\n6.NDLS-HWH\n')

# userInput=int(sys.argv[1])


infraPath='simulator_input'

########################################################################################################

gqdDF=pd.read_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress-StationCodes.csv',low_memory=False)

print('Reading cleaned_train_list4.csv')
cleanTrainDF=pd.read_csv(outputPath+'cleaned_train_list4.csv')
cleanTrainDF=cleanTrainDF[cleanTrainDF['simTrain_no'].apply(lambda x: str(x)[1]=='0')]
cleanTrainDF.set_index('Train_no',inplace=True)

jumpingTrains=[indx for indx in cleanTrainDF.index.drop_duplicates() if len(cleanTrainDF.loc[indx][['simTrain_no']])>1]
jumpingTrainsDF=cleanTrainDF[cleanTrainDF.index.isin(jumpingTrains)]

data=[]
for train in jumpingTrains:
    dftemp=jumpingTrainsDF.loc[[train]].sort_values(by='Start_Sequence')
    dftemp.set_index('simTrain_no',inplace=True)
    dftempGqd=gqdDF[gqdDF['TRAIN']==str(train)]
    for i,j in zip(dftemp.index[:-1],dftemp.index[1:]):
        temp={'TrainA':i,'StartA':dftempGqd[(dftempGqd['SEQ']==dftemp.loc[i,'Start_Sequence']) & (dftempGqd['TRAIN']==str(train))]['STATION'].values[0],
                      'EndA':dftempGqd[(dftempGqd['SEQ']==dftemp.loc[i,'End_Sequence']) & (dftempGqd['TRAIN']==str(train))]['STATION'].values[0],
                      'TrainB':j,'StartB':dftempGqd[(dftempGqd['SEQ']==dftemp.loc[j,'Start_Sequence']) & (dftempGqd['TRAIN']==str(train))]['STATION'].values[0],
                      'EndB':dftempGqd[(dftempGqd['SEQ']==dftemp.loc[j,'End_Sequence']) & (dftempGqd['TRAIN']==str(train))]['STATION'].values[0],
                      'repTrain':train,
                      'timeDifference(mins)':((dftempGqd[(dftempGqd['SEQ']==dftemp.loc[j,'Start_Sequence']) & (dftempGqd['TRAIN']==str(train))]['ARVL'].values[0])-(dftempGqd[(dftempGqd['SEQ']==dftemp.loc[i,'End_Sequence']) & (dftempGqd['TRAIN']==str(train))]['ARVL'].values[0]))/60}
        data.append(temp)

linkedTrainsDF=pd.DataFrame(data)

print('Writing trainLinking.csv')
linkedTrainsDF.to_csv(inputPath+'trainLinking.csv',index=False)
