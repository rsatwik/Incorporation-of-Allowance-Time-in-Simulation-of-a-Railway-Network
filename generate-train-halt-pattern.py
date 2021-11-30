import pandas as pd
import json
from tqdm import tqdm
import sys
import os


# config variables - yet to be moved to config.ini

train_no='TRAIN_NO' 
arr='ARRIVAL'
dep='DEPARTURE'
stn='STTN_CODE'

train_no='TRAIN' 
arr='ARVL'
dep='DPRT'
stn='STATION'

# this is the train schedule sheet saved as csv
# tsd=pd.read_csv('/home/sid/railways/Files recieved from cris/Delhi_Mumbai_TimeTable.csv')
print('Reading timetable ...')

######## added by Soham #########
inputPath = "../common/"
outputPath = "postprocessed_files/"
##################################

tsd=pd.read_csv(inputPath + 'GQD_Schedule_04thJuly20_WorkInProgress.csv') # Read the latest GQD file 
train_dict={}
print('Generating halt pattern ...')
for tno in tqdm(tsd[train_no].unique()):
    tn_stn_data=tsd[(tsd[train_no]==tno) & (tsd[arr]!=tsd[dep])].copy()[[stn,arr,dep]]
    if len(tn_stn_data)>0:
        tn_stn_data['halt']=(tn_stn_data[dep]-tn_stn_data[arr])/60
        tdict=tn_stn_data[[stn,'halt']].to_dict(orient='records')
        train_dict[str(tno)]=[str(stn[data]) for stn in tdict for data in stn]
    # else:
    #     print(str(tno)+' does not have any scheduled stops')
    
print(str(len(train_dict.keys()))+' have atleast one halt')
with open(outputPath +'/GQD-halt-pattern.txt', 'w') as file:
     file.write(json.dumps(train_dict).replace('"','\''))
