#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from collections import defaultdict
import os
from tqdm import tqdm
from pandas import ExcelWriter
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import multiprocessing as mp
import sys

# cris_input_folder_path = "/home/railwayint/Independant_6_routes_Infrastructure/6.HWH-NDLS-INFRA-30june_mps"          # CRIS data files are present here
# simulator_input_folder_path = "/home/railwayint/Independant_6_routes_Infrastructure/6.HWH-NDLS-INFRA-30june_mps" # Folder path
# simulator_output_folder_path = "/home/railwayint/Independant_6_routes_Infrastructure/6.HWH-NDLS-INFRA-30june_mps"
# output_folder_path = "/home/railwayint/Independant_6_routes_Infrastructure/6.HWH-NDLS-INFRA-30june_mps"      # Output Folder path

#### Added by Soham
infraPath = "simulator_input/"
simulator_out = "simulator_output/"
postprocessed_path = "postprocessed_files/"
####

# Useful Functions go here

def HHMM_to_min(hhmm):
    return (float(hhmm[:hhmm.index(':')])*60+float(hhmm[hhmm.index(':')+1:]))

def min_to_HHMM_mod(minutes):
    hours = (int(float(minutes))//60)%24
    mins = int(float(minutes))%60
    if(len(str(hours))==1):
        hours = '0'+str(hours)
    if(len(str(mins))==1):
        mins = '0'+str(mins)
    return str(hours)+':'+str(mins)



#  Ok only stn_list, train_nos and traversal_dict_list is required

print("\nExtracting station dictionary from loop.txt...")
loop = open(infraPath +'loop.txt').readlines()[2:]
station_dict = {k.split()[0]:k.split()[3] for k in loop }

print("\nGetting station list from station.txt file....")

station = open(infraPath +'station.txt').readlines()[2:]
station_list = [s.split()[0] for s in station]   # The station list derived from station.txt file

print("\nGetting day-2 train_nos from unscheduled.txt....")
unscheduled = open(infraPath +'unscheduled.txt').readlines()[2:]
train_nos = [u.split()[0] for u in unscheduled if u.split()[0][0]=='2']   # Day-2 trains only

print("\nGetting halts given in unscheduled.txt file.....")
unsch = open(infraPath +'unscheduled.txt').readlines()[2:]
scheduled_dict = {}
for u in unsch:
    temp = u.split()
    if(temp[0][0]!='2'):
        continue
    else:
        di = {}
        for i in temp[11:]:
            if(temp.index(i)%2==0):
                continue
            if(i==temp[-1]):
                break
            di[i] = temp[temp.index(i)+1]
    scheduled_dict[temp[0]] = di                 # Dict of dicts




print("\nGetting the overtake and allowance based halts...")
allowances = open(postprocessed_path +'allowances.txt').readlines()  # Allowances file

allowance_dict = {}
for al in allowances:
    temp = al.split()
    if(temp[0][0]=='2'):
        lis = [k for i,k in enumerate(temp) if(i%3==1)]
    else:
        continue
    allowance_dict[temp[0]] = lis                               # This contains only stations

overtake_df = pd.read_csv(postprocessed_path +'overtakes.csv')
overtake_df['Overtaken_T.No.'] = overtake_df['Overtaken_T.No.'].astype(float).astype(int).astype(str)
overtake_stations_dict = {}
for i in overtake_df.index.tolist():
    if(overtake_df.iloc[i]['Overtaken_T.No.'][0]=='2'):
        if(overtake_df.iloc[i]['Overtaken_T.No.'] not in overtake_stations_dict):
            overtake_stations_dict[overtake_df.iloc[i]['Overtaken_T.No.']]=[]
            overtake_stations_dict[overtake_df.iloc[i]['Overtaken_T.No.']].append(overtake_df.iloc[i]['stn_code'])
        else:
            overtake_stations_dict[overtake_df.iloc[i]['Overtaken_T.No.']].append(overtake_df.iloc[i]['stn_code'])    # This contains only stations
    else:
        continue

for train in train_nos:
    if(train not in overtake_stations_dict):
        overtake_stations_dict[train] = []


print("\nGetting traversal_dict_list from traversal details")
traversal_details = open(simulator_out +'TraversalDetails.txt').readlines()
current_train='None'
traversal_dict_list={}             # Traversal Dictionary
lis=[]
for t in traversal_details:
    if('Printing timetables for train' in t):
        traversal_dict_list[current_train]=lis
        current_train=t.split()[-1]
        lis=[]         # Empty list
    else:
        temp_lis=[]
        if(t.split()[2][-1]=='0'):             # Continue if it's a block
            continue
        temp_lis.append(station_dict[str(t.split()[2])])           # REQ Station dict is required
        temp_lis.append(min_to_HHMM_mod(float(t.split()[11])))     # min_to_HHMM_mod is required
        temp_lis.append(min_to_HHMM_mod(float(t.split()[14])))
        lis.append(temp_lis)
traversal_dict_list[current_train]=lis
del traversal_dict_list['None']


print("\nReading from the IC-IC google spreadsheet...")


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
         '../common/railway-project-283300-f09cf0b91c2b.json', scope) # Your json file here

gc = gspread.authorize(credentials)

wks = gc.open("InterchangePointsPanRoutesMajorJunctions").sheet1


data = wks.get_all_values()
headers = data.pop(0)

df = pd.DataFrame(data, columns=headers)
print("\nRead data into a pandas dataframe...")

df = df.loc[df['route']==sys.argv[1]]                    # 4th route stations
stn_list = [l for l in list(df['StationCode']) if l in station_list]         # Collect the major stations


print("\nGenerating TT for Human Viewing...")

#route = int(sys.argv[1])

#if route==1:
#    stn_list = ['NDLS', 'MTJ','SWM','KOTA', 'NAD','RTM', 'BRC','ST', 'BSR','BVI', 'MMCT']
#elif route==2:
#    stn_list = ['NDLS','AGC','DHO','GWL','JHS','BPL','ET','NGP','BPQ','WL','KI','BZA','GDR','MASA']
#elif route==3:
#    stn_list = ['HWHA','KGP','BHC','CTC','BBS','NWP','VSKP','RJY','BZA','GDR','MASA']
#elif route==4:
#    stn_list = ['HWHA','KGP','RHE','TATA','ROU','JSG','BSP','URK','MUP','NGP','BD','BSL','MMR','IGP','KYN','CSMT']
#elif route==5:
#    stn_list = ['MASB', 'AJJ', 'RU', 'GTL', 'WADI', 'SUR', 'DD', 'PUNE', 'LNL', 'KYN', 'CSMT']
#else:
#    stn_list = ['NDLS','GZB','TDL','ETW','CNB','PRYJ','DDU','SEB','GAYA','GMO','DHN','KAN','HWHB']


train_nos_int=[int(t) for t in train_nos]
train_nos_int.sort()
train_nos=[str(t) for t in train_nos_int]           # Sorted train_nos list

data_table_new = []
count=0
train_subset_list=[]
for train in tqdm(train_nos):              # All Train Numbers are done here   # REQ train_nos
    try:
        arr_lis=[]
        dep_lis=[]
        for s in stn_list:               # All stations are done here    # REQ stn_list
            arr_sim = 0
            pure_halt = False
            no_halt = False

            if(s in scheduled_dict[train] and s not in allowance_dict[train] and s not in overtake_stations_dict[train]):
                pure_halt = True
            if(s not in scheduled_dict[train] and s not in allowance_dict[train] and s not in overtake_stations_dict[train]):
                no_halt = True

            for lis in traversal_dict_list[train]:                 #  REQ traversal_dict_list
                if(s in lis and lis==traversal_dict_list[train][-1]):
                    pure_halt = True

                if(s in lis):

                    if(pure_halt==True and lis!=traversal_dict_list[train][-1]):
                        arr = float(HHMM_to_min(lis[2]))-float(scheduled_dict[train][s])
                        arr_lis.append(min_to_HHMM_mod(arr))
                    elif(pure_halt==True and lis==traversal_dict_list[train][-1]):             # Last station
                        arr_lis.append(lis[2])
                    elif(no_halt==True):
                        arr_lis.append(lis[2])
                    else:
                        arr_lis.append(lis[1])

                    dep_lis.append(lis[2])
                    arr_lis.append(' ')
                    dep_lis.append(' ')
                    arr_sim=1
                    break
            if(arr_sim==0):
                arr_lis.append(' ')
                dep_lis.append(' ')
                arr_lis.append(' ')
                dep_lis.append(' ')

        data_table_new.append(arr_lis)
        data_table_new.append(dep_lis)
        count+=1
        train_subset_list.append(train)
    except KeyError:
        print('sid'+train)

#
data_table_new=np.array(data_table_new)
train_nos_new=[item[1:] for item in train_subset_list for i in range(2)]

arr_dep=['Arr', 'Dep']*count
arrays = [train_nos_new,arr_dep]
tuples = list(zip(*arrays))

stn_list_new=[]
for i in stn_list:
    stn_list_new.append(i)
    stn_list_new.append(i)
sim_cris=[ 'SIM',' ']*len(stn_list)

arrays = [stn_list_new,sim_cris]
tuples2 = list(zip(*arrays))
index = pd.MultiIndex.from_tuples(tuples, names=['Train-->', ' '])
index2 = pd.MultiIndex.from_tuples(tuples2, names=[' ', ' '])

print("\n Writing all stations TT...")
df=pd.DataFrame(data_table_new.transpose(), index=index2, columns=index)
df.to_excel(postprocessed_path +'TTjustMajorStns.xlsx')
