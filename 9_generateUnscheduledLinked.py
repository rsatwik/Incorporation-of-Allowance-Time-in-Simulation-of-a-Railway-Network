import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='' # path to output files


#print('1.NDLS-MMCT\n2.NDLS-MAS\n3.HWH-MAS\n4.CSMT-HWH\n5.CSMT-MAS\n6.NDLS-HWH\n')

#userInput=int(sys.argv[1])
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

import pandas as pd
linkedTrainsDF=pd.read_csv(inputPath+'trainLinking.csv')
linkedTrainsDF=linkedTrainsDF.astype({'TrainA':str,'TrainB':str})
linkedTrainsDF.set_index('TrainB', inplace=True)

if len(sys.argv) > 1:
    infraPath=sys.argv[1]
    with open(infraPath+'unscheduled.txt') as u:
        unscheduled=u.readlines()
else:
    with open(infraPath+'unscheduled1.txt') as u:
        unscheduled=u.readlines()

startTimes={}
for row in unscheduled:
    if len(row.split())<1: continue
    if row[0]=='/': continue
    temp=row.split()
    startTimes[temp[0]]=float(temp[2])

for index in range(len(unscheduled)):
    row=unscheduled[index]
    if len(row.split())<1: continue
    if row[0]=='/': continue
    temp=row.split()
    day=temp[0][0]
    if temp[0][1:] in linkedTrainsDF.index:
        if day+str(linkedTrainsDF.loc[temp[0][1:]][['TrainA']].values[0]) in startTimes.keys():
            temp.insert(2,day+str(linkedTrainsDF.loc[temp[0][1:]][['TrainA']].values[0]))
            temp.insert(3,str(linkedTrainsDF.loc[temp[0][1:]][['timeDifference(mins)']].values[0]))
            temp[4]=str(startTimes[day+str(linkedTrainsDF.loc[temp[0][1:]][['TrainA']].values[0])]+0.1)
            startTimes[temp[0]]=startTimes[day+str(linkedTrainsDF.loc[temp[0][1:]][['TrainA']].values[0])]+0.1
        else:
            temp.insert(2,'0')
            temp.insert(3,'0')
    else:
        temp.insert(2,'0')
        temp.insert(3,'0')
    unscheduled[index]=' '.join(temp)

print('Writing unscheduledLinked.txt')
with open(infraPath+'unscheduledLinked.txt','w') as w:
    w.write('\n')
    w.write('\n'.join(unscheduled))
