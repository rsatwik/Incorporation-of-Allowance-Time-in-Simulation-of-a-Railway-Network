# usage: python3 find-allowance-station-mp.py <infr-path> <unscheduled-file> <acc_decc_loss-file> <gqd-halt-pattern-file> <output-file>

import multiprocessing as mp
import sys
import pandas as pd
import json
from collections import defaultdict
import os
from tqdm import tqdm
from pandas import ExcelWriter
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials

### changed by Soham
infra_path="simulator_input/"
postprocessingPath = "postprocessed_files/"
commonPath = "../common/"
####################


# start reading from end of this function

def find_allowance(line):
    # global ta_data
    # global train_halt_pattern_POST,train_halt_pattern_PRE
    global stn_list,stn_list_reversed,ic_and_major_arr,ic_and_major_arr_rev
    global stn_data,acc_decc_loss
    global spl_list,spl_ta

    if not line=="\n":
        train = line.split(" ")
        tno=train[0]
        tdir=train[1]
        uhalt_list = train[11:]
        if not len(uhalt_list) == 2*int(train[10]):
            print("warning: number of halts don't match", tno)

        # station wise scheduled halt
        if tno in train_halt_pattern.keys():
            halt_raw = train_halt_pattern[tno]
        elif tno[2:] in train_halt_pattern.keys() :
            tno=tno[2:]
            halt_raw = train_halt_pattern[tno]
        # elif tno in train_halt_pattern_PRE.keys():
        #     halt_raw = train_halt_pattern_PRE[tno]
        # elif tno[2:] in train_halt_pattern_PRE.keys() :
        #     tno=tno[2:]
        #     halt_raw = train_halt_pattern_PRE[tno]
        else:
            halt_raw=[]
        halt = 0
        halt_arr = {}
        for i in range(0, len(halt_raw), 2):
            halt_arr[halt_raw[i]] = float(halt_raw[i + 1])

        # station wise unscheduled halt
        uhalt = 0
        stn_alw_arr = {}
        for i in range(0, len(uhalt_list), 2):
            x = 60 * float(uhalt_list[i + 1])
            # subtract scheduled halt (if any)
            if uhalt_list[i] in halt_arr.keys():
                x -= 60 * halt_arr[uhalt_list[i]]
            if not uhalt_list[i] in halt_arr.keys():
                loss=acc_decc_loss[(abs(acc_decc_loss['acc(m/s2)']-float(train[4]))<0.001) & (abs(acc_decc_loss['decc(m/s2)']-float(train[5]))<0.001) & (abs(acc_decc_loss['train_speed(kmph)']-float(train[7]))< 3 )][['loss']].loss.to_list()
                if len(loss)==0:
                    print(train[4]+','+train[5]+','+train[7])
                x += loss[0]
            uhalt += x
            if not x==0:
                stn_alw_arr[uhalt_list[i]] = [x,0]

        if tdir=="down":
            current_stn_list = stn_list_reversed
        elif tdir=="up":
            current_stn_list = stn_list

        # train_ta_data=ta_data[ta_data['TRAIN_NO']==int(tno)].copy()
        # IC-to-IC TA calculation
        for i in range(0, len(ic_and_major_arr)-1):
            if tdir=="down":
                start_idx = stn_list_reversed.index(ic_and_major_arr[i])
                end_idx = stn_list_reversed.index(ic_and_major_arr[i + 1])
                sub_stn_arr = stn_list_reversed[start_idx + 1: end_idx+1]
                ic_start=ic_and_major_arr[i]
                ic_end=ic_and_major_arr[i + 1]
            elif tdir=="up":
                start_idx = stn_list.index(ic_and_major_arr_rev[i])
                end_idx = stn_list.index(ic_and_major_arr_rev[i + 1])
                sub_stn_arr = stn_list[start_idx + 1: end_idx+1]
                ic_start=ic_and_major_arr_rev[i]
                ic_end=ic_and_major_arr_rev[i + 1]

            # sub_stn_ta=train_ta_data[train_ta_data['STTN_CODE'].isin(sub_stn_arr) & (~(train_ta_data['TRFCALWC']==0))].copy()
            # if len(sub_stn_ta)>0:
            #     # find no of stations with allowance within this sub_stns and equally divide TA
            #     n=len(list(set(stn_alw_arr.keys())&set(sub_stn_arr)))
            #     if n==0:
            #         # print("** "+str(train[0])+" : TA mismatch\n")
            #         ta_per_stn=0
            #     else:
            #         total_ta=sum(sub_stn_ta.TRFCALWC.to_list())
            n=len(list(set(stn_alw_arr.keys())&set(sub_stn_arr)))
                # optimize this by converting stn_data to dict
            if n>0:
                for idx,row in stn_data[stn_data['name']==ic_start][['start','end']].iterrows():
                    start_dist=sum(row.tolist())/2
                for idx,row in stn_data[stn_data['name']==ic_end][['start','end']].iterrows():
                    end_dist=sum(row.tolist())/2
                total_dist_ta=abs(end_dist-start_dist)*0.07*60
                # total_ta=min(total_dist_ta,total_ta)
                if tno in spl_list:
                    total_dist_ta=abs(end_dist-start_dist)*spl_ta*60
                total_ta=total_dist_ta
                ta_per_stn=total_ta/n

                ta_bal=0
                for ta_stn in list(set(stn_alw_arr.keys())&set(sub_stn_arr)):
                    if (stn_alw_arr[ta_stn][0]-ta_per_stn-ta_bal) <=0:
                        stn_alw_arr[ta_stn][1]=stn_alw_arr[ta_stn][0]
                        ta_bal+=ta_per_stn-stn_alw_arr[ta_stn][0]
                        stn_alw_arr[ta_stn][0]=0
                    else:
                        stn_alw_arr[ta_stn][0]-=ta_per_stn+ta_bal
                        stn_alw_arr[ta_stn][1]=ta_per_stn+ta_bal
                        ta_bal=0

        return str(train[0])+" "+ " ".join([stn+" "+"{:.3f}".format(a[0])+" {:.1f}".format(a[1]) for stn,a in zip([s for s in current_stn_list if s in stn_alw_arr.keys()],[stn_alw_arr[s] for s in current_stn_list if s in stn_alw_arr.keys()])])+"\n"


# main code starts here
# ta_data=pd.read_excel('/home/sid/railways/Files recieved from cris/Delhi_Mumbai_TimeTable.xlsx',sheet_name='Train Schedule')[['TRAIN_NO','STTN_CODE','TRFCALWC']]
# train_halt_pattern_PRE = eval(open('train_stn_halt_dict_PRE.txt', 'r').read())
# train_halt_pattern_POST = eval(open('train_stn_halt_dict_POST.txt', 'r').read())
# path of infrastructure - directory containing station.txt, loop.txt ...


# train_halt_pattern=eval(open('../gqd_exp/GDQ-halt-pattern.txt', 'r').read())
train_halt_pattern=eval(open(postprocessingPath + 'GQD-halt-pattern.txt', 'r').read())

spl_list=['12951','12952','12953','12954']
spl_ta=0.03
stn_data = pd.read_csv(infra_path+'station.txt', delimiter=" ", names=['name', 'start', 'end', 'entry'], header=0)
stn_list = stn_data.name.to_list()
stn_list_reversed=stn_data.name.to_list().copy()
stn_list_reversed.reverse()
loopDict={}
with open(infra_path+'loop.txt') as l:
    for lp in l.readlines()[2:]:
        temp = lp.split()
        lpNum = temp[0]
        lpDir = temp[1]
        lpStation = temp[3].strip()
        loopDict[lpNum]=lpStation.replace('"','')

#route=int(sys.argv[1])

#if route==1:
#   ic_and_major_arr = ['NDLS', 'PWL', 'MTJ', 'GGC', 'SWM', 'KOTA', 'NAD', 'RTM', 'GDA', 'BRC', 'ST', #'VAPI', 'MMCT']
#elif route==2:
#    ic_and_major_arr = #['NDLS','AGC','DHO','GWL','JHS','BPL','ET','NGP','BPQ','WL','KI','BZA','GDR','MASA']
#elif route==3:
#    ic_and_major_arr = ['HWHA','KGP','BHC','CTC','BBS','NWP','VSKP','RJY','BZA','GDR','MASA']
#elif route==4:
#    ic_and_major_arr = #['HWHA','KGP','RHE','TATA','ROU','JSG','BSP','URK','MUP','NGP','BD','BSL','MMR','IGP','KYN','CSMT']
#elif route==5:
#    ic_and_major_arr = ['MASB', 'AJJ', 'RU', 'GTL', 'WADI', 'SUR', 'DD', 'PUNE', 'LNL', 'KYN', 'CSMT']
#else:
#    ic_and_major_arr = ['NDLS','GZB','TDL','ETW','CNB','PRYJ','DDU','SEB','GAYA','GMO','DHN','KAN','HWHB']

print("\nGetting station list from station.txt file....")

station = open(infra_path +'station.txt').readlines()[2:]
station_list = [s.split()[0] for s in station]                           # The station list derived from station.txt file

print("\nReading from the IC-IC google spreadsheet...")

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
         '../common/railway-project-283300-f09cf0b91c2b.json', scope) # Your json file here

gc = gspread.authorize(credentials)

wks = gc.open("InterchangePointsPanRoutesMajorJunctions").sheet1


data = wks.get_all_values()
headers = data.pop(0)

dfs = pd.DataFrame(data, columns=headers)
print("\nRead data into a pandas dataframe...")

dfs = dfs[dfs['route']==sys.argv[1]]
dfs = dfs[dfs['allowanceStation']=='yes']               # Route 4 is HWH CSMT
ic_and_major_arr = [l for l in list(dfs['StationCode']) if l in station_list]
ic_and_major_arr_rev=  ic_and_major_arr.copy()
ic_and_major_arr_rev.reverse()
print("\nThe IC and major arrival list is as follows:\n")
print(ic_and_major_arr)
print("\n Above was the IC and major arrival list\n\n")


# acc-decc loss file
acc_decc_loss = pd.read_csv(commonPath +'acc_decc_losses.csv')

allowance_dict={}
extra_halt={}

print("\nFinding allowances ...")
with open(infra_path +'unscheduled.txt') as unsch:
    unscheduled_list = unsch.readlines()
unscheduled_list = unscheduled_list[2:]


# this is the file to which the allowance data is written
allowance_file=open(postprocessingPath +'allowances.txt',"w")
with mp.Pool(mp.cpu_count()) as p:
    r = list(tqdm(p.imap(find_allowance, unscheduled_list), total=len(unscheduled_list)))
    #print(r)
    allowance_file.writelines(r)
    p.close()
    p.join()
