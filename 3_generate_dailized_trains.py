import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

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

cleanedTrainListDF=pd.read_csv(outputPath+'cleaned_train_list2.csv',index_col='Train_no')
gqdDF=pd.read_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress.csv',low_memory=False)
gqdDF=gqdDF.astype({'TRAIN': str})
gqdDF=gqdDF.set_index('TRAIN')

df2=gqdDF.iloc[[0]].copy(deep=True)
df2=df2.drop(gqdDF.iloc[[0]].index[0])     # creates an empty dataframe df2


################################# ---MANUAL METHOD----######################################

print('Cleaning Single Touch trains...')

routesDF=pd.read_excel(inputPath+'All6routesTrainsZBTTJune2020.xlsx',index_col=0)

for userInput in range(1,7):


    if userInput == 1:
        singleTouchTrainsDF=routesDF[routesDF.loc[:,'Route1'] == 'ROUTE-1-NDLS-MMCT'].copy(deep=True)

    if userInput == 2:
        singleTouchTrainsDF=routesDF[routesDF.loc[:,'Route2'] == 'ROUTE-2-NDLS-MAS'].copy(deep=True)

    if userInput == 3:
        singleTouchTrainsDF=routesDF[routesDF.loc[:,'Route3'] == 'ROUTE-3-HWH-MAS'].copy(deep=True)

    if userInput == 4:
        singleTouchTrainsDF=routesDF[routesDF.loc[:,'Route4'] == 'ROUTE-4-HWH-CSMT'].copy(deep=True)

    if userInput == 5:
        singleTouchTrainsDF=routesDF[routesDF.loc[:,'Route5'] == 'ROUTE-5-CSMT-MAS'].copy(deep=True)

    if userInput == 6:
        singleTouchTrainsDF=routesDF[routesDF.loc[:,'Route6'] == 'ROUTE-6-NDLS-HWH'].copy(deep=True)

    singleTouchTrainsDF=singleTouchTrainsDF[singleTouchTrainsDF.loc[:,'Type_Route_basis']=='Single Touching']
    print('Number of single touch trains :',len(singleTouchTrainsDF.index))

    gqdDF=gqdDF[~gqdDF.index.isin(singleTouchTrainsDF.index.tolist())]
    print('Number of non-singletouch trains :',len(gqdDF.index.drop_duplicates()))

    dfRemappingNDLS_MMCT=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=1,sheet_name='R1-NDLS-MMCT')
    dfRemappingNDLS_MMCT=dfRemappingNDLS_MMCT[~dfRemappingNDLS_MMCT['New-Number'].isna()]
    dfRemappingNDLS_MMCT=dfRemappingNDLS_MMCT.astype({'New-Number': int,'Route closest to which train-no.':int})
    dfRemappingNDLS_MMCT=dfRemappingNDLS_MMCT.astype({'New-Number': str,'Route closest to which train-no.':str})
    dfRemappingNDLS_MMCT=dfRemappingNDLS_MMCT.set_index('Route closest to which train-no.')

    dfRemappingNDLS_MAS=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=1,sheet_name='R2-NDLS-MAS')
    dfRemappingNDLS_MAS=dfRemappingNDLS_MAS[~dfRemappingNDLS_MAS['New-Number'].isna()]
    dfRemappingNDLS_MAS=dfRemappingNDLS_MAS.astype({'New-Number': int,'Route closest to which train-no.':int})
    dfRemappingNDLS_MAS=dfRemappingNDLS_MAS.astype({'New-Number': str,'Route closest to which train-no.':str})
    dfRemappingNDLS_MAS=dfRemappingNDLS_MAS.set_index('Route closest to which train-no.')

    dfRemappingHWH_MAS=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=1,sheet_name='R3-HWH-MAS')
    dfRemappingHWH_MAS=dfRemappingHWH_MAS[~dfRemappingHWH_MAS['New-Number'].isna()]
    dfRemappingHWH_MAS=dfRemappingHWH_MAS.astype({'New-Number': int,'Route closest to which train-no.':int})
    dfRemappingHWH_MAS=dfRemappingHWH_MAS.astype({'New-Number': str,'Route closest to which train-no.':str})
    dfRemappingHWH_MAS=dfRemappingHWH_MAS.set_index('Route closest to which train-no.')

    dfRemappingHWH_CSMT=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=1,sheet_name='R4-CSMT-HWH')
    dfRemappingHWH_CSMT=dfRemappingHWH_CSMT[~dfRemappingHWH_CSMT['New-Number'].isna()]
    dfRemappingHWH_CSMT=dfRemappingHWH_CSMT.astype({'New-Number': int,'Route closest to which train-no.':int})
    dfRemappingHWH_CSMT=dfRemappingHWH_CSMT.astype({'New-Number': str,'Route closest to which train-no.':str})
    dfRemappingHWH_CSMT=dfRemappingHWH_CSMT.set_index('Route closest to which train-no.')

    dfRemappingCSMT_MAS=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=1,sheet_name='R5-CSMT-MAS')
    dfRemappingCSMT_MAS=dfRemappingCSMT_MAS[~dfRemappingCSMT_MAS['New-Number'].isna()]
    dfRemappingCSMT_MAS=dfRemappingCSMT_MAS.astype({'New-Number': int,'Route closest to which train-no.':int})
    dfRemappingCSMT_MAS=dfRemappingCSMT_MAS.astype({'New-Number': str,'Route closest to which train-no.':str})
    dfRemappingCSMT_MAS=dfRemappingCSMT_MAS.set_index('Route closest to which train-no.')

    dfRemappingNDLS_HWH=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=1,sheet_name='R6-NDLS-HWH')
    dfRemappingNDLS_HWH=dfRemappingNDLS_HWH[~dfRemappingNDLS_HWH['New-Number'].isna()]
    dfRemappingNDLS_HWH=dfRemappingNDLS_HWH.astype({'New-Number': int,'Route closest to which train-no.':int})
    dfRemappingNDLS_HWH=dfRemappingNDLS_HWH.astype({'New-Number': str,'Route closest to which train-no.':str})
    dfRemappingNDLS_HWH=dfRemappingNDLS_HWH.set_index('Route closest to which train-no.')



    if userInput == 1:
        dfRemapping=dfRemappingNDLS_MMCT

        dfRemappingdel=pd.read_excel(inputPath+'Remapping-non-daily2daily-paths-All-6-Routes.xlsx',header=None,sheet_name='trains to be deleted-too-INFREQ',skiprows=[0,1,2])
        dfRemappingdel=dfRemappingdel[~dfRemappingdel[0].isna()]
        dfRemappingdel=dfRemappingdel.astype({0:int})
        dfRemappingdel=dfRemappingdel.astype({0:str})
        dfRemappingdel=dfRemappingdel.set_index(0)

        dfRemappingdel2=pd.read_excel(inputPath+'MMCT_NDLS_TrainList-updated.xlsx',header=0,sheet_name='Trains touching at a point')
        dfRemappingdel2=dfRemappingdel2.astype({'Train_Number':str})
        dfRemappingdel2=dfRemappingdel2.set_index('Train_Number')

    if userInput == 2:
        dfRemapping=dfRemappingNDLS_MAS

    if userInput == 3:
        dfRemapping=dfRemappingHWH_MAS

    if userInput == 4:
        dfRemapping=dfRemappingHWH_CSMT

    if userInput == 5:
        dfRemapping=dfRemappingCSMT_MAS

    if userInput == 6:
        dfRemapping=dfRemappingNDLS_HWH

    # dfRemapping = pd.concat([dfRemappingNDLS_MMCT,dfRemappingNDLS_MAS,dfRemappingHWH_MAS,dfRemappingHWH_CSMT,dfRemappingCSMT_MAS,dfRemappingNDLS_HWH])

    dfRemapping=dfRemapping[~dfRemapping.isna()]


    # dropped_train=[]
    modifiedNonDailyTrains=[]
    modifiedNonDailyTrains=[]
    for train in tqdm(list(dfRemapping.index)):
        try:
            dftemp=gqdDF.loc[train].copy(deep=True)
            dftemp['Sno']=range(0,dftemp.shape[0])
            dftemp=dftemp.sort_values(by='DPRT')

        except KeyError:
            print('Cannot find train',train,'in GQD data')
            continue
        try:
            start=int(dftemp[dftemp['STATION']==dfRemapping.loc[train]['Start-Stn']]['Sno'].to_list()[0])
        except:
            print('Cannot find start station for',train)
            continue

        try:
            end=int(dftemp[dftemp['STATION']==dfRemapping.loc[train]['End-Stn']]['Sno'].to_list()[0])
        except:
            print('Cannot find end station for',train)
            continue

        selSection=range(start,end+1) if end-start>0 else range(end,start+1)
        selSection=list(selSection)

        var=np.zeros(dftemp.shape[0]).astype(bool)
        var[selSection]=True

        dftemp=dftemp.sort_values(by='Sno')[var]
        dftemp=dftemp.drop(columns=['Sno'])

        newindx=dfRemapping.loc[train]['New-Number']
        indx=dftemp.index.tolist()
        for i,elem in enumerate(indx):
            indx[i]=newindx

        modifiedNonDailyTrains.append(newindx)
        dftemp.index=indx
        df2=pd.concat([df2,dftemp])
        del dftemp
        # except KeyError:

        #     dropped_train.append(train)

        #     try:
        #         dfRemapping.drop([train],inplace=True)
        #     except:
        #         continue
        #     continue
        # except:
        #     dropped_train.append(train)

        #     dfRemapping.drop([train],inplace=True)
        #     continue


    print('Number of modified/dailized trains:{0}'.format(len(modifiedNonDailyTrains)))

    #### Deleting the trains ############

    # trainsToDeleteDF=pd.read_csv(outputPath+'trainsToDelete1.csv',header=None)
    # trainsToDeleteDF=trainsToDeleteDF.astype({0:str})
    # trainsToDeleteDF=trainsToDeleteDF.set_index(0)

    # trainsToDelete = trainsToDeleteDF.index.to_list()

    trainsToDelete=[]

    for i in range(4,len(dfRemapping.columns)):
        for j in range(len(dfRemapping.index)):
            if not math.isnan(dfRemapping.iloc[j,i]):
                trainNumber=int(dfRemapping.iloc[j,i])
                trainsToDelete.extend(map(str,cleanedTrainListDF[(cleanedTrainListDF.index == trainNumber) & (cleanedTrainListDF.Route_no == userInput)].simTrain_no.to_list()))
                # trainsToDelete.extend(str(int(dfRemapping.iloc[j,i])))


    # for train in dfRemapping.index:
    #     trainsToDelete.extend(map(str,cleanedTrainListDF[(cleanedTrainListDF.index == train) & (cleanedTrainListDF.Route_no == userInput)].simTrain_no.to_list()))

df2.drop_duplicates(inplace=True)

# deleteTrains=[64076,64074,64902,64062,64908,64078,64012,64052,64014,64016,64904,64492,64082,64906,64910,64053,64905,64903,64071,64077,64055,64491,64901,64057,64013,64015,64017,64569,64073,64019,64051,11841] # deleted because of MTJ-PWL 3rd line
# deleteTrains+=[64101,64111,64109,64103,64105,64151,64160] # deleted because of NDLS-ALJN 3rd line
# deleteTrains+=[63141,63142,63501,63502] # deleted on NDLS-HWH route on Jul 23
# deleteTrains=map(str,deleteTrains)

# # print(list(map(str,cleanedTrainListDF[cleanedTrainListDF.index.isin(deleteTrains)].simTrain_no.to_list())))
# trainsToDelete.extend(map(str,cleanedTrainListDF[cleanedTrainListDF.index.isin(deleteTrains)].simTrain_no.to_list()))

print('Number of trains to be deleted:{0}'.format(len(set(trainsToDelete))))

with open(outputPath+'trainsToDelete3.csv','w') as f:
    for train in trainsToDelete:
        f.write(str(train)+',')
        f.write('\n')

df2.to_csv(outputPath+'dailizedTrains3.csv')

# print('Starting Summation.....')

# df2['totalDays']=None
# df2['daily']=None
# allTrainsList=df2.index.to_list()
# for train in tqdm(allTrainsList):
#     # try:
#     totalNumberOfDaysOfRun=sum(map(int,(list(str(list(df2.loc[train,'DAYS'].values)[0]).split(',')))))
#     df2.loc[train,'totalDays']=totalNumberOfDaysOfRun
#     # except:
#     #     print('**Not found**',train)
#     #     continue

#     # try:
#     if (df2.loc[train,'totalDays'].values)[0]<3:
#         dailyOrNot=0
#     else:
#         dailyOrNot=1  # daily trains
#     df2.loc[train,'daily']=dailyOrNot
#     # except:
#     #     print('**Not found**',train)
#     #     continue

# print('Completed Summation.....')


# ## modify all modifiedNonDailyTrains to daily trains
# for train in tqdm(modifiedNonDailyTrains):
#     df2.loc[train,'daily']=1

# # df2.index=df2.index.astype(int)
# dailyTrains=(list(df2[df2['daily']==1].index.drop_duplicates()))
# print('Total Number of daily and dailized trains:{0}'.format(len(dailyTrains)))

# df2 = df2[df2['daily']==1]
# df2.to_csv(outputPath+'ModifiedAndDailyTrains.csv')

#################################----AUTOMATED METHOD---#########################################

# finalTrains=gqdDF.iloc[[0]].copy(deep=True)
# finalTrains=finalTrains.drop(gqdDF.iloc[[0]].index[0])

# dailyTrainsDn=pd.read_csv(inputPath+'daily_trainsdown_NDLS_HWH.txt',index_col=[0])
# dailyTrainsUp=pd.read_csv(inputPath+'daily_trainsup_NDLS_HWH.txt',index_col=[0])

# ## if userInput == 1:
# ##     print('Adding exception trains in NDLS-HWH:')
# ##     exceptionTrains=['12273','12274']
# ##     print(exceptionTrains)
# ##     for train in exceptionTrains:
# ##         dftemp=df2.loc[train].copy(deep=True)
# ##         finalTrains=pd.concat([finalTrains,dftemp])
# ##         del dftemp

# cleanedTrainListDF=pd.read_csv(inputPath+'cleaned_train_list.csv',index_col='Train_no') # again for assertion statements

# for train in dailyTrainsDn.index:
#     try:
#         dftemp=df2.loc[train].copy(deep=True)
#         finalTrains=pd.concat([finalTrains,dftemp])
#         del dftemp
#     except KeyError:
#         assert cleanedTrainListDF.loc[str(train)]['Start_Sequence']==0
#         print('Daily Down train',train,'has 0 sequence in clean train list')

# for train in dailyTrainsUp.index:
#     try:
#         dftemp=df2.loc[train].copy(deep=True)
#         finalTrains=pd.concat([finalTrains,dftemp])
#         del dftemp
#     except KeyError:
#         if not cleanedTrainListDF.loc[str(train)]['Start_Sequence']==0:
#             print('ERROR :',train,'not found and has non zero sequence')
#             sys.exit(1)
#         # assert cleanedTrainListDF.loc[str(train)]['Start_Sequence']==0
#         print('Daily Up train',train,'has 0 sequence in clean train list')

# repTrainsDn=pd.read_csv(inputPath+'rep_trainsdown_NDLS_HWH.txt',sep=' ',index_col=[0])
# repTrainsUp=pd.read_csv(inputPath+'rep_trainsup_NDLS_HWH.txt',sep=' ',index_col=[0])

# dailyTrainsInRep=[]                                    # Daily trains that do not merge with anyother trains

# for train in repTrainsDn.index:
#     count=0
#     for value in repTrainsDn.loc[train].values:
#         if not math.isnan(value):
#             count+=1
#     if count < 3:
#         dailyTrainsInRep.append(train)
# repTrainsDn=repTrainsDn[~repTrainsDn.index.isin(dailyTrainsInRep)]

# for train in repTrainsUp.index:
#     count=0
#     for value in repTrainsUp.loc[train].values:
#         if not math.isnan(value):
#             count+=1
#     if count < 3:
#         dailyTrainsInRep.append(train)
# repTrainsUp=repTrainsUp[~repTrainsUp.index.isin(dailyTrainsInRep)]

# for train in dailyTrainsInRep:
#     try:
#         dftemp=df2.loc[str(train)].copy(deep=True)
#         finalTrains=pd.concat([finalTrains,dftemp])
#         del dftemp
#     except KeyError:
#         assert cleanedTrainListDF.loc[str(train)]['Start_Sequence']==0
#         print('Daily train',train,'in representative list has 0 sequence in clean train list')

# modifiedUpTrains=0
# modifiedNonDailyTrains=[]
# for train in list(repTrainsUp.index):
#     try:
#         train=str(train)
#         dftemp=df2.loc[train].copy(deep=True)

#         newindx=int('9'+str(train))
#         indx=dftemp.index.tolist()
#         for i,elem in enumerate(indx):
#             indx[i]=newindx

#         modifiedNonDailyTrains.append(newindx)
#         dftemp.index=indx
#         finalTrains=pd.concat([finalTrains,dftemp])
#         del dftemp
#     except KeyError:
#         assert cleanedTrainListDF.loc[str(train)]['Start_Sequence']==0
#         print('Representative Up train',train,'has 0 sequence in clean train list')

# modifiedUpTrains=len(modifiedNonDailyTrains)
# print('Number of modified/dailized Up trains : {0}'.format(modifiedUpTrains))

# for train in list(repTrainsDn.index):
#     try:
#         train=str(train)
#         dftemp=df2.loc[train].copy(deep=True)

#         newindx=int('9'+str(train))
#         indx=dftemp.index.tolist()
#         for i,elem in enumerate(indx):
#             indx[i]=newindx

#         modifiedNonDailyTrains.append(newindx)
#         dftemp.index=indx
#         finalTrains=pd.concat([finalTrains,dftemp])
#         del dftemp
#     except KeyError:
#         assert cleanedTrainListDF.loc[str(train)]['Start_Sequence']==0
#         print('Representative Down train',train,'has 0 sequence in clean train list')

# print('Number of modified/dailized Down trains : {0}'.format(len(modifiedNonDailyTrains)-modifiedUpTrains))
# print('Total Number of modified/dailized trains : {0}'.format(len(modifiedNonDailyTrains)))

# trainsToDelete=[]

# for i in range(len(repTrainsUp.index)):
#     for j in range(0,len(repTrainsUp.columns)):
#         if not math.isnan(repTrainsUp.iloc[i,j]):
#             if int(repTrainsUp.iloc[i,j]) > 10:
#                 trainsToDelete.append(int(repTrainsUp.iloc[i,j]))

# for i in range(len(repTrainsDn.index)):
#     for j in range(0,len(repTrainsDn.columns)):
#         if not math.isnan(repTrainsDn.iloc[i,j]):
#             if int(repTrainsDn.iloc[i,j]) > 10:
#                 trainsToDelete.append(int(repTrainsDn.iloc[i,j]))


# print('Number of trains to be deleted : {0}'.format(len(set(trainsToDelete))))

# finalTrains = finalTrains[~finalTrains.index.isin(trainsToDelete)]

# print('Total Number of Trains :',len(list(finalTrains.index.drop_duplicates())))

# finalTrains.to_csv(outputPath+'ModifiedAndDailyTrains.csv')
