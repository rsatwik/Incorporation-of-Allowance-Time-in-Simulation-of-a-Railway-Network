import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path to output files


########################################################################################################

df2=pd.read_csv(outputPath+'ModifiedAndDailyTrains4.csv',index_col=[0])
dailizedTrainsDF=pd.read_csv(outputPath+'dailizedTrains3.csv',index_col=[0])


print('Starting Summation.....')

df2['totalDays']=None
df2['daily']=None
allTrainsList=df2.index.drop_duplicates().to_list()
print('Total iterations :',len(allTrainsList))
for train in tqdm(allTrainsList):
    try:
        totalNumberOfDaysOfRun=sum(map(int,(list(str(list(df2.loc[train,'WEEKDAYS'].values)[0]).split(',')))))
        df2.loc[train,'totalDays']=totalNumberOfDaysOfRun
    except AttributeError:
        if not len(df2.loc[[train]]) == 1:
            sys.exit(1)
        print(train,'has only single station on this route**')
        continue
    try:
        if (df2.loc[train,'totalDays'].values)[0]<3:
            dailyOrNot=0
            ## modify all modifiedNonDailyTrains to daily trains
            if int(str(train)[1:]) in dailizedTrainsDF.index.drop_duplicates():
                dailyOrNot=1
        else:
            dailyOrNot=1  # daily trains
        df2.loc[train,'daily']=dailyOrNot
    except ValueError:
        print('cannot int',train)
        continue

print('Completed Summation.....')

dailyTrains=(list(df2[df2['daily']==1].index.drop_duplicates()))
print('Total Number of daily and dailized trains:{0}'.format(len(dailyTrains)))

df2 = df2[df2['daily']==1]
df2.to_csv(outputPath+'ModifiedAndDailyTrains5.csv')
