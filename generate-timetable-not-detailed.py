# usage : python3 generate-timetable-not-detailed.py

import pandas as pd
import sys
import os


#### Added by Soham
infraPath = "simulator_input/"
simulator_out = "simulator_output/"
postprocessed_path = "postprocessed_files/"
####


print('\nReading loop.txt')
with open(infraPath +'loop.txt') as loop_file:
    loop=loop_file.readlines()[2:]
loopDict={}
for l in loop:
    row=l.split()
    loopDict[row[0]]=row[3].replace('"','')

print('\nReading unscheduled.txt')
unsched={}
dir_dict={}
with open(infraPath +'unscheduled.txt') as unsch:
    unscheduled_list = unsch.readlines()
unscheduled_list = unscheduled_list[2:]
for line in unscheduled_list:
    row=line.split()
    unsched[row[0]] = row[2]
    dir_dict[row[0]] = row[1]

print('\nReading Traversal Details')
with open(simulator_out +'TraversalDetails.txt') as TD_file:
    TD=TD_file.readlines()
currentTrain = 0
output_file=open(postprocessed_path +'timetable-not-detailed.csv','w')
output_file.write('trainno,dir,stn,arr,dep,halt\n')
for row in TD:
    if 'Printing' in row:
        currentTrain = row.split()[-1]
        # try:
        train_dir=dir_dict[currentTrain]
        # except KeyError: # please revisit this.
        #   continue
    else:
        temp = row.split()
        if temp[2] in loopDict.keys():
            output_file.write(currentTrain+','+train_dir+','+loopDict[temp[2]]+','+temp[11]+','+temp[14]+','+str(float(temp[14])-float(temp[11]))+'\n')
