import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path for output

########################################################################################################

cleanedTrainListDF=pd.read_csv(outputPath+'cleaned_train_list1.csv')
cleanedTrainListDF=cleanedTrainListDF.astype({'Train_no':str})

cleanedTrainListDF['MPS']=None
cleanedTrainListDF['EAminsPer100km']=None
cleanedTrainListDF['TAminsPer100km']=None

trainSpeedDF=pd.read_excel(inputPath+'Train-priorities-MPS-accln-decln.xlsx',sheet_name='GQD Trains',skiprows=[0])
trainSpeedDF=trainSpeedDF.astype({'TRAIN': str})
trainSpeedDF=trainSpeedDF.set_index('TRAIN')

for train in cleanedTrainListDF.loc[:,'Train_no'].values:
    try:
        indx=cleanedTrainListDF[cleanedTrainListDF.loc[:,'Train_no']==train].index
        trainSpeed=trainSpeedDF.loc[train]['MPS']
        cleanedTrainListDF.loc[indx,'MPS']=trainSpeed
        if trainSpeed > 110:
            cleanedTrainListDF.loc[indx,'EAminsPer100km']= 8.0
            cleanedTrainListDF.loc[indx,'TAminsPer100km']= 7.0
        elif trainSpeed <= 110:
            cleanedTrainListDF.loc[indx,'EAminsPer100km']= 6.0
            cleanedTrainListDF.loc[indx,'TAminsPer100km']= 5.0
    except KeyError:
        print('****',train,'not found in the 12june2020-Train_MPS.xlsx File ****')

print('Re-printing cleaned_train_list1.csv to cleaned_train_list_2.csv')
cleanedTrainListDF.to_csv(outputPath+'cleaned_train_list2.csv',index=False)
