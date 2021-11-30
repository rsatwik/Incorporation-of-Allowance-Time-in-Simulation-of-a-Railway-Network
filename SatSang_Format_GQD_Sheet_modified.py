#!/usr/bin/env python
# Written primarily by Bhushan Deo in May/June 2020
print("######################################### Briefly These are the expected filepaths #############################################\n")
print("GQD.csv         CRIS DATA      :: cris_input_folder_path")
print("TraversalDetails.txt            OUTPUT OF THE SIMULATOR         :: simulator_output_folder_path")
print("loop.txt                        INPUT TO THE SIMULATOR          :: simulator_input_folder_path")
print("station.txt                     INPUT TO THE SIMULATOR          :: simulator_input_folder_path")
print("unscheduled.txt                 INPUT TO THE SIMULATOR          :: simulator_input_folder_path")
print("allowances.txt                  COMPILED FROM SIDHARTHA'S CODE  :: simulator_output_folder_path")    # sid's allowance code 
print("removed_train_list.csv          REMOVED TRAIN LIST IF ANY       :: simulator_output_folder_path")    # can it be an empty file??? pls check 
print("train_type.txt    TO READ TRAIN TYPE AND TRAIN NAMES IF REQUIRED :: cris_input_folder_path")    # this is required for train type  
print("SatSang_Format.xlsx             CRIS IMPORTABLE SATSANG FORMAT  :: output_folder_path")


print("########################################## These are the variables which can be altered to change the filepaths ##################################\n")

print("\ncris_input_folder_path                        ::  preprocessed_files")
print("\nsimulator_input_folder_path                   ::  simulator_input")
print("\nsimulator_output_folder_path                  ::  simulator_output")
print("\noutput_folder_path                            ::  post_processed_files")

print("\n##########################################################################################################\n")


print("\nBeginning Execution...")


# In[20]:
import os
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from collections import defaultdict

# Folder Paths go here
start_time = time.time()              # Start time

# cris_input_folder_path = "preprocessed_files/"          # CRIS data files are present here
# simulator_input_folder_path = "simulator_input/" # Folder path
# simulator_output_folder_path = "simulator_output/"
# output_folder_path = "postprocessed_files/"      # Output Folder path

##### Added by Bhushan #############
inputPath = "../common/"
infraPath = "simulator_input/"
sim_out = "simulator_output/"
postprocessPath = "postprocessed_files/"
###################################

# The files required are:: TraversalDetails.txt simout 
# loop.txt infrapath
# station.txt infrapath
# unscheduled.txt infrapath
# input path train_type.txt
# input path GQD_Schedule_04thJuly20_WorkInProgress
# postprocesspath :: allowances.txt and overtakes.csv 
###########################################################################################################

def is_halt(simTime,train,station):                  
    # Is the station a halt from traversal details??? takes in loop (all 3 types: scheduled, allowance, overtakes
    arr = float(simTime[train][simTime[train].index(station)+1])
    dep = float(simTime[train][simTime[train].index(station)+2])
    if(abs(arr-dep)>1):
        return True
    return False

# Useful functions
def extract_flag(station,train): # whether terminates on route etc (not used as on 27th June)
    if(station!=start_end_dict[train][-1]):
        return 'Continue'
    else:
        if(end_station_times_dict[train][-2]==end_station_times_dict[train][-1]):
            return "Terminate"
        else:
            return "Exit"                           # Return either Exit-True or Exit-False

def acc_time_loss_calc(priority,maxspeed,train_type):           # Return the acceleration time loss according to priority and maxspeed
    if(priority=='1' or maxspeed=='130'):
        return 125
    elif(priority=='2'):          # at 110
        return 122
    elif(priority=='3'):          # at 110
        return 122
    elif(priority=='4' and train_type in ['MEMU','EMU']):
        return 125
    elif(priority=='4'):
        return 150


def dec_time_loss_calc(priority,maxspeed,train_type):           # Return the deceleration time loss according to priority and maxspeed
    if(priority=='1' or maxspeed=='130'):
        return 72
    elif(priority=='2'):          # at 110
        return 61
    elif(priority=='3'):          # at 110
        return 61
    elif(priority=='4' and train_type in ['MEMU','EMU']):
        return 25
    elif(priority=='4'):
        return 35

def create_loss_dict(priority,maxspeed,train_type,key,loss_dict):
  # this one is enough. (The earlier two are incorporated WITHIN this.)
    if(priority=='1' or maxspeed=='130'):
        loss_dict[key]=[72,125]
    elif(priority=='2'):          # at 110
        loss_dict[key]=[61,122]
    elif(priority=='3'):          # at 110
        loss_dict[key]=[61,122]
    elif(priority=='4' and train_type in ['MEMU','EMU']):
        loss_dict[key]=[25,125]
    elif(priority=='4'):
        loss_dict[key]=[35,150]
    return loss_dict

print("\nReading the GQD dataframe and extracting all train numbers... Please put the latest GQD file...")
gqd_df = pd.read_csv(inputPath + 'GQD_Schedule_04thJuly20_WorkInProgress.csv')                # GQD dataframe
gqdTrnNums = list(gqd_df['TRAIN'].unique())                         # All train numbers


with open(sim_out+'TraversalDetails.txt') as td:
    traversal_details=td.readlines() 
    # traversal_details is now a list (each row is one element)

print("\nExtracting Some traversal details from TraversalDetails.txt...")
current_train='None'
simTime={}
# each train number is the key, and value is the list (loop number, arrTime, DepTime)
lis=[]
for t in tqdm(traversal_details):
    if('Printing timetables for train' in t): # starting of a new train
        simTime[current_train]=lis # create a new entry in t...dict by 
        # putting value lis
        current_train=t.split()[-1]
        lis=[]         # Empty list initialization for the FOLLOWING(NEW) train
    else: # keeps appending as long as not the NEXT train
        if(t.split()[2][-1]=='0'):                                 # Not a block but a loop
            continue
        lis.append(t.split()[2]) # loop number
        lis.append(t.split()[11]) # arrival time
        lis.append(t.split()[14]) # departure time

simTime[current_train]=lis # only last inclusion was remaining

del simTime['None']

print("\nExtracting Station Dictionaries from loop.txt...")
loop = open(infraPath +'/loop.txt','r').readlines()[2:]
station = open(infraPath+'/station.txt','r').readlines()[2:]
stn_list = [s.split()[0] for s in station]

# keys are loop numbers, values are station names
station_dict = {s.split()[0]:s.split()[3] for s in loop if s.split()[3] in stn_list}

# keys are now station names, values are list of loop numbers
station_dict_reverse = defaultdict(list) # initializing (for next line to do the needful)
[station_dict_reverse[s.split()[3]].append(s.split()[0]) for s in loop if s.split()[3] in stn_list]

# 

print("\nExtracting some station distances from station.txt...")
stnDistDc = {}
with open(infraPath+'station.txt') as stnf:
    station_list = stnf.readlines()
station_list = station_list[2:]
for s in tqdm(station_list):
    if(len(s.split())==0):
        break
    else:
        temp = s.split()
        stnDistDc[temp[0]] = float(temp[1])

print("\nExtracting max speeds priorities direction and halts of train from unscheduled.txt")
print("\tExtracting info only for Day-2 trains")
maxspeed_dict={}
priority_dict={}
direction_dict={}
train_unsch_dict={}
train_nos=[]
train_nos_up=[]
train_nos_down=[]
with open(infraPath+'unscheduled.txt') as unsch:
    unscheduled=unsch.readlines()
    # unscheduled is a list of rows (from the above file)

for u in tqdm(unscheduled[2:]):
    # take relevant info from unscheduled.txt
    lis=[]
    temp=u.split()
    if(len(u.split())==0):
        break # reached end of file (break out of for loop)
    train_no=temp[0]
    if(train_no[:2]!='20' and train_no[:2]!='29'):          # Do only for day-2 trains
        continue # go to next u in the for loop

    lis.append(temp[6])
    for i in range(8,len(temp)):
        lis.append(temp[i])
    train_unsch_dict[train_no]=lis # known/scheduled halts
    priority_dict[u.split()[0]]=u.split()[6] # Update the priority Dictionary
    direction_dict[u.split()[0]]=u.split()[1]
    maxspeed_dict[u.split()[0]]=u.split()[7]
    if u.split()[1]=='up':
        train_nos_up.append(train_no)
    else:
        train_nos_down.append(train_no)

train_nos = train_nos_up+train_nos_down

print("\nExtracting train types which is required to compute acc/dec losses...")
with open(inputPath+'train_type.txt') as f: # Combined by Chandrashekhar
    train_info=f.readlines()                                           # Info being read in train_info 


# train_numbers_name_dict={}
train_type={}
for t in tqdm(train_info[1:]): # needed for SatSang output as we require the train type here 
    temp=t.split()
    if(len(temp)==0):
        break # reached end of file/list
    else:
        if('20'+str(temp[0]) in train_nos):
            curr_train='20'+str(temp[0])
        elif('29'+str(temp[0]) in train_nos):
            curr_train='29'+str(temp[0])
        else:
            continue
        # train_numbers_name_dict[curr_train]=" ".join(temp[1:-1])         # The Numbers-Name Dict
        train_type[curr_train]=temp[-1]                                  # Train type last entry of the line goes here 
# print(train_type['2916032'])
EaTaDc={}                        # EA TA dictionary 

with open(postprocessPath+'allowances.txt') as al:              # Created by sidhartha 
    allowance_info=al.readlines()

for a in allowance_info[2:]:
    if(len(a.split())==0):
        break 
    else:
        current_train=a.split()[0]
        EaTaDc[current_train]=a.split()[1:]


print("\nExtracting Scheduled Halts Dictionary from GQD Dataframe...")
train_sch_dict={}
continuing_trains = []
start_end_dict = {}                 # These are CRIS dicts
end_station_times_dict = {}
train_nos_new = []
for train_no in tqdm(train_nos): # train_nos is from unscheduled (train_no is a STRING)
    try:
        lis=[]
        if(int(train_no[-5:]) in gqdTrnNums): # unique train numbers from GQD.csv file
            curr_df=gqd_df.loc[gqd_df['TRAIN']==int(train_no[-5:])] # take only last 5 digits
        else: # to be sure about this string/integer mixup within GQD-xls does not create hurdle
            curr_df=gqd_df.loc[gqd_df['TRAIN']==str(train_no[-5:])] #
    #    curr_df=gqd_df.loc[gqd_df['TRAIN']==int(train_no[-5:])] if(int(train_no[-5:]) in gqdTrnNums) else curr_df=gqd_df.loc[gqd_df['TRAIN']==str(train_no[-5:])]
        start_end_dict[train_no] = [list(curr_df['STATION'])[0],list(curr_df['STATION'])[-1]] # picks start and end of each train (from GQD)
        end_station_times_dict[train_no] = [list(curr_df['ARVL'])[-1],list(curr_df['DPRT'])[-1],list(curr_df['NEXT'])[-1]] # picks values from GQD data
        lis.append(train_unsch_dict[str(train_no)][0]) # from unscheduled.txt (known halts)
        lis.append(train_unsch_dict[str(train_no)][1]) # but source/destination missing
        lis.append(train_unsch_dict[str(train_no)][2])
        sch_halts=0 # scheduled by CRIS!
    #     curr_df=curr_df.dropna()
        temp_lis=[]
        first_row=curr_df.iloc[0]
        temp_list=[]
        arr_time_start=int(first_row['ARVL'])
        for stn in list(curr_df['STATION']): # to take really the CRIS scheduled halts ONLY
            if(stn not in station_dict_reverse):                    # This station lies outside our route
                if(stn==list(curr_df['STATION'])[-1]):              # Last station not in station reverse dictionary
                    continuing_trains.append(train_no)              # It's a continuing train
                continue                                            # Have to continue because station doesn't lie
            if(stn==list(curr_df['STATION'])[-1]):                  # Last station
                stn_df=curr_df.loc[curr_df['STATION']==stn].iloc[0] # means NOT a halt
                if(float(stn_df['DPRT'])!=float(stn_df['NEXT'])): # Next arrival and departure are different, which means this is a HALT
                    continuing_trains.append(train_no)

            stn_df=curr_df.loc[curr_df['STATION']==stn].iloc[0]
            if(float(stn_df['ARVL'])!=float(stn_df['DPRT'])):
                sch_halts+=1
                temp_list.append(str(stn))
                temp_list.append(str(float(int(abs(float(stn_df['ARVL'])-float(stn_df['DPRT'])))//60)))
        dep_time_end=int(stn_df['DPRT'])
        temp_lis.append(arr_time_start)
        temp_lis.append(dep_time_end)
        lis.append(str(sch_halts))
        for l in temp_list:
            lis.append(l)
        train_sch_dict[str(train_no)]=lis
        if(len(simTime[train_no])<15): # each dict-value: has 3 entries per train
            continue # skip trains that have 4 stations or less (5*3 = 15)
        else:
            train_nos_new.append(train_no)
    except KeyError:
        print("Train {} not in TD but in unscheduled.txt".format(train_no))
train_nos = train_nos_new











print("\nNow adding the first and the last stations to the created scheduled dict...")

for train in tqdm(train_nos): # train_sch_dict came from GQD data 
    train_sch_dict[train].insert(4,'0.0') # inserts 0 minute halts at source and destination stations
    train_sch_dict[train].insert(4,station_dict[train_sch_dict[train][1]]) # source
    train_sch_dict[train].insert(len(train_sch_dict[train]),station_dict[train_sch_dict[train][2]]) # destination
    train_sch_dict[train].insert(len(train_sch_dict[train]),'0.0') # destination
    train_sch_dict[train][3] = str(int(train_sch_dict[train][3])+2) # hike up number of halts
# train_sch_dict: 

#print(simTime['2012952'])             # Loop number arrival then departure in minutes in a list for a train
#print(EaTaDc['2012952'])                             # Station followed by TA consumed and EA consumed in seconds
print("\nMaking the overtaken dictionary...")
overtaken_dataframe = pd.read_csv(postprocessPath+'overtakes.csv')
overtaken_dataframe=overtaken_dataframe[overtaken_dataframe['Overtaken_T.No.'].astype(str).str[0]=='2'].reset_index()[['Overtaken_T.No.','stn_code']]    # Only day-2 trains, and only relevant columns
#print(overtaken_dataframe)
overtaken_dictionary=defaultdict(list) # initializing
[overtaken_dictionary[k].append(v) for k,v in zip(overtaken_dataframe['Overtaken_T.No.'].astype(int).astype(str), overtaken_dataframe['stn_code'])]
# overtaken_dictionary=dict(zip(overtaken_dataframe['Overtaken_T.No.'].astype(int).astype(str), overtaken_dataframe['stn_code']))        # Keys are strings
#print(station_dict_reverse)                  # loops for a particular station
# print(is_halt(simTime,'2012952','21900001'))           # This is true

######################################################## Print Length of various dictionaries to maintain consistency ###################################
#print("\n Printing lengths of some of the dictionaries ")
#print(len(train_nos))
#print(len(simTime))
#print(len(station_dict))
#print(len(station_dict_reverse))
#print(len(stnDistDc))
#print(len(maxspeed_dict))
#print(len(direction_dict))
#print(len(priority_dict))
#print(len(train_unsch_dict))
#print(len(train_nos))
#print(len(EaTaDc))
#print(len(train_sch_dict))
#print(len(start_end_dict))
#print(len(end_station_times_dict))


overtaken_dictionary = dict(overtaken_dictionary) # made objects into normal dictionary
print(len(overtaken_dictionary))
for train in train_nos:
    if(train not in overtaken_dictionary):
        overtaken_dictionary[train] = [] # Sidhartha' file has only overtaken trains. Initiate empty for others.
print(len(overtaken_dictionary))
print("\n############################# Creating SatSang Format ################################################################################")
print("\n Only if allowance based halt is a non-overtake halt, then the timings are artificially edited to consume allowance")
print("\n Overtake based allowance halts are shown as halts in the SatSang format")
print("\n Dec loss is consumed in the previous section, acc loss and halt duration are consumed in the next section")

# Just first check whether an allowance station then check whether an overtake station
# if allowance station and not a overtake station
# then just make arrival = departure


column_names=['TRAINNUMBER','SEQNUMBER','STTNCODE','BLCKSCTN','COABLCKSCTN','BLCKBUSYDAYS','ARVLTIME','STPGTIME','DPRTTIME','ACCTIME','DECTIME','ENGGALWC','TRFCALWC','EXTRATIME','STTNLINE','BLCKSCTNLINE','NEXTARVL','RUNTIME']


dictionary_list = []                          # List of dictionaries

curr_station='-'
prev_station='-'
next_station='-'

print("\nGetting the acc dec loss dictionary to distribute losses over multiple small sections....")

nested_loss_dict = {}

for train in tqdm(train_nos):
    try:
        loss_dict = {}
        o=0 # o is just a counter
        while(o<=len(simTime[train])-3):
            curr_station= station_dict[str(simTime[train][o])]
            if(curr_station in train_sch_dict[train] or curr_station in overtaken_dictionary[train]):
                loss_dict = create_loss_dict(priority_dict[train],maxspeed_dict[train],train_type[train],curr_station,loss_dict)
            o+=3 # # nested dictionary, outer dict has key as train-no
        nested_loss_dict[train] = loss_dict # 
    except KeyError:
        print(train)

#     except:
#         print("\n Train number"+str(train)+" not present in train_numbers_name_list")
#         continue

print("\n PGMD is specific to NDLS-MMCT route.....")
print("\n If you don't want stations like PGMD (Pragati Maidan), please remove them from the infrastructure")
print("\n They may have acc/dec losses, allowances distributed")
print("\n If removed from infra, they'll automatically be removed from the SatSang format")

rogTrnLst = []
gqd_df['STATION'] = gqd_df['STATION'].astype('category')
gqd_df['TRAIN'] = gqd_df['TRAIN'].astype('category')
for train in tqdm(train_nos):                      # All the trains
    # print(train)
    j=0
    i=0
    balance = 0 # balance variable is not being used (
#     print(train)
    pgmd = 0 # Pragati Maidan needs an infrastructure # 
    prev_seq_number = 0
    try: # except (very last part) for a KeyError due to - (as of now), Bhushan put this try catch
        while(j<=len(simTime[train])-3):     # Till -3 only  loop over traversal dict actual time
            lis=[]

            if(train[1]=='0'): train_number=train[-6:]             # Append a zero no problem
            else: train_number=train[-6:]             # Representative Train so last 6 digits

            lis.append(train_number)             # Train Number

            if(j==0): # j is counter for traversal dict actual time (starting point!)
                curr_station= station_dict[str(simTime[train][j])]
                prev_station='-'
                prev_prev_station='-'
                next_station= station_dict[str(simTime[train][j+3])]
                next_next_station = station_dict[str(simTime[train][j+6])]
                next_next_next_station = station_dict[str(simTime[train][j+9])]

            elif(j==3):
                curr_station= station_dict[str(simTime[train][j])]
                prev_station=station_dict[str(simTime[train][j-3])]
                prev_prev_station='-'
                next_station= station_dict[str(simTime[train][j+3])]
                next_next_station = station_dict[str(simTime[train][j+6])]
                next_next_next_station = station_dict[str(simTime[train][j+9])]

            elif(j==len(simTime[train])-3): # very last station on our route
                curr_station= station_dict[str(simTime[train][j])]
                prev_station=station_dict[str(simTime[train][j-3])]
                prev_prev_station=station_dict[str(simTime[train][j-6])]
                next_station= '-'
                next_next_station = '-'
                next_next_next_station = '-'

            else: # all intermediate ones.
                curr_station= station_dict[str(simTime[train][j])]
                prev_station=station_dict[str(simTime[train][j-3])]
                prev_prev_station=station_dict[str(simTime[train][j-6])]
                next_station= station_dict[str(simTime[train][j+3])]
                if(j==len(simTime[train])-6):
                    next_next_station = '-'
                    next_next_next_station = '-'
                else:
                    next_next_station = next_next_station = station_dict[str(simTime[train][j+6])]
                    if(j==len(simTime[train])-9):
                        next_next_next_station = '-'
                    else:
                        next_next_next_station = station_dict[str(simTime[train][j+9])]

            # current and next stations have been extracted

            if(int(train[-5:]) in gqdTrnNums):
                curt = int(train[-5:])
            else:
                curt = str(train[-5:])

            if(curr_station=='PGMD'):
                lis.append(str(int(prev_seq_number)+1))
                pgmd=1
            elif(len(list(gqd_df.loc[(gqd_df['TRAIN']==curt) & (gqd_df['STATION']==curr_station)]['SEQ']))!=0):
                if(pgmd!=1):
                    lis.append(list(gqd_df.loc[(gqd_df['TRAIN']==curt) & (gqd_df['STATION']==curr_station)]['SEQ'])[0])
                    prev_seq_number = list(gqd_df.loc[(gqd_df['TRAIN']==curt) & (gqd_df['STATION']==curr_station)]['SEQ'])[0]
                else:
                    lis.append(int(list(gqd_df.loc[(gqd_df['TRAIN']==curt) & (gqd_df['STATION']==curr_station)]['SEQ'])[0])+1)
                    prev_seq_number = int(list(gqd_df.loc[(gqd_df['TRAIN']==curt) & (gqd_df['STATION']==curr_station)]['SEQ'])[0])+1
            else:
                lis.append('NA')      # Pragati Maidan not in cris infra
            # Sequence Number
            lis.append(curr_station)                  # Current Station  STTNCODE THAT IS


            # Seq Number and Current station are done


                                        # Next Station
            lis.append(str(curr_station)+'-'+str(next_station))                         # Block Section
            lis.append('?')                # COA Block Section
            lis.append('1')                # We're running daily trains

            # Now comes arrival departure times

            if(curr_station in EaTaDc[train] and curr_station not in overtaken_dictionary[train]):       # Allowance but not overtake
                acc_time_loss=acc_time_loss_calc(priority_dict[train],maxspeed_dict[train],train_type[train])
                dec_time_loss=dec_time_loss_calc(priority_dict[train],maxspeed_dict[train],train_type[train])

                if(curr_station not in train_sch_dict[train]):    # Not a scheduled halt

                    arrival_time=60*float(simTime[train][j+1])-(dec_time_loss)
                    # So only add artificial halt duration and time loss due to acceleration to get the arrival time
                    departure_time=arrival_time
                    stoppage_time=0                  # Because no official stoppage just the train slows down

                else:
                	# Here original scheduled halt duration is reported 
                    # Extension of a scheduled halt, here you report arrival_time+original halt duration
                    halt_duration= 60*float(train_sch_dict[train][train_sch_dict[train].index(curr_station)+1])     # From Traversal Scheduled Dict
                    arrival_time= 60*float(simTime[train][j+1])
                    if(curr_station==train_sch_dict[train][-2]):            # Last station
                        departure_time = arrival_time
                    else:
                        departure_time=arrival_time+halt_duration   # Arrival time + Scheduled Halt
                    stoppage_time=halt_duration

            else:                    # Actual arrival and departure times
                arrival_time = round(60*float(simTime[train][j+1]))
                if(curr_station==train_sch_dict[train][-2]):            # Last station
                    departure_time = arrival_time
                else:
                    departure_time = round(60*float(simTime[train][j+2]))
                stoppage_time = departure_time-arrival_time


            lis.append(round(arrival_time)-86400)            #Arrival Time
            lis.append(round(stoppage_time))           #Stoppage Time
            lis.append(round(departure_time)-86400)          #Departure Time

            # compute allowances
            if(curr_station in EaTaDc[train]):
                EA_value = float(EaTaDc[train][EaTaDc[train].index(curr_station)+1])
                TA_value = float(EaTaDc[train][EaTaDc[train].index(curr_station)+2])
            else:
                EA_value=0
                TA_value=0


            # Acc Dec Loss
            dec_time_loss = 0
            acc_time_loss = 0
            loss=0

            
            if((next_next_next_station in train_sch_dict[train]) or (next_next_next_station in overtaken_dictionary[train])  and abs(stnDistDc[next_next_next_station]-stnDistDc[next_next_station])<=2):
                loss=1
                dec_time_loss += nested_loss_dict[train][next_next_next_station][0]/5
                nested_loss_dict[train][next_next_next_station][0]-= nested_loss_dict[train][next_next_next_station][0]/5

            if((next_next_station in train_sch_dict[train]) or (next_next_station in overtaken_dictionary[train]) and abs(stnDistDc[next_next_station]-stnDistDc[next_station])<=2):
                loss=1
                dec_time_loss += nested_loss_dict[train][next_next_station][0]/3
                nested_loss_dict[train][next_next_station][0]-= nested_loss_dict[train][next_next_station][0]/3


            if(next_station in train_sch_dict[train] or next_station in overtaken_dictionary[train]):     # It is a halt
                # Get Deceleration time to decelerate to the next station
                loss=1
                dec_time_loss+=nested_loss_dict[train][next_station][0]
                nested_loss_dict[train][next_station][0]-= dec_time_loss

    #         print(curr_station,next_station)
            if(curr_station==train_sch_dict[train][-2]):  # Last station, no acc loss
                loss=0
            else:

                if(next_next_station!='-'):
                    if((next_station in train_sch_dict[train] or next_station in overtaken_dictionary[train]) and abs(stnDistDc[next_station]-stnDistDc[next_next_station])<=4.5):
                        loss=1
                        # Get the acceleration Time to accelerate from the previous halt
                        acc_time_loss+=nested_loss_dict[train][next_station][1]/5
                        nested_loss_dict[train][next_station][1]-=nested_loss_dict[train][next_station][1]/5
    #                 print(curr_station,next_station)
                if((curr_station in train_sch_dict[train] or curr_station in overtaken_dictionary[train]) and abs(stnDistDc[curr_station]-stnDistDc[next_station])<=4.5):
                    loss=1
                    # Get the acceleration Time to accelerate from the previous halt
                    acc_time_loss+=nested_loss_dict[train][curr_station][1]/3
                    nested_loss_dict[train][curr_station][1]-=nested_loss_dict[train][curr_station][1]/3

                if((curr_station in train_sch_dict[train] or curr_station in overtaken_dictionary[train]) and abs(stnDistDc[curr_station]-stnDistDc[next_station])>4.5):
                    loss=1
                    # Get the acceleration Time to accelerate from the previous halt
                    acc_time_loss+=nested_loss_dict[train][curr_station][1]
                    nested_loss_dict[train][curr_station][1]-=acc_time_loss


                if(prev_station in train_sch_dict[train] or prev_station in overtaken_dictionary[train]):
                    acc_time_loss+=nested_loss_dict[train][prev_station][1]
                    nested_loss_dict[train][prev_station][1]-=acc_time_loss
                    if(acc_time_loss!=0):
                        loss=1

            lis.append(round(acc_time_loss))                   # Acceleration time loss

            lis.append(round(dec_time_loss))                   # Deceleration time loss
            lis.append(round(EA_value))                        # EA value
            lis.append(round(TA_value))                        # TA value
            lis.append(0)                            # Extra Time


            stop_loop = str(simTime[train][j])        # Stop Loop
            if(stop_loop[-4]=='0'):                         # Up LOOP
                if(stop_loop[-3]=='0'):
                    loop_name='UP_ML'
                else:
                    loop_name='UP'
            elif(stop_loop[-4]=='1'):                       # DN LOOP
                if(stop_loop[-3]=='0'):
                    loop_name='DN_ML'
                else:
                    loop_name='DN'
            elif(stop_loop[-4]=='2'):                       # Common Loop
                loop_name='CMN'

            lis.append(loop_name+'-'+str(simTime[train][j][-1]))             # Loop Line

            if(train in train_nos_up):
                lis.append(1)             # Up Block Section Line
            else:
                lis.append(2)             # Down Block Section Line


            if(next_station=='-'):               # Next station is not present

                if(train in continuing_trains):
                    lis.append(0)                                  # For continuing trains the next arrival is zero
                else:

                    lis.append(round(departure_time)-86400)        # For terminating trains the next arrival is kept as last station departure time
                next_arrival_time = 0
            else:
                if(next_station in EaTaDc[train] and next_station not in overtaken_dictionary[train]):             # It's used up for allowance
                    acc_time_loss_two=acc_time_loss_calc(priority_dict[train],maxspeed_dict[train],train_type[train])
                    dec_time_loss_two=dec_time_loss_calc(priority_dict[train],maxspeed_dict[train],train_type[train])

                    if(next_station not in train_sch_dict[train]):    # Not a scheduled halt
                           # From Traversal Unscheduled Dict
                        next_arrival_time=60*float(simTime[train][j+4])-(dec_time_loss_two)
                                     # Because no official stoppage just the train slows down
                    else:
                                            # From Traversal Scheduled Dict
                        next_arrival_time= 60*float(simTime[train][j+4])


                else:                    # Maybe a scheduled halt or halt due to overtakes of other trains/congestion

                    if(next_station  in train_sch_dict[train]):        # It is a scheduled Halt but not an extended halt
                        next_arrival_time = 60*float(simTime[train][j+4])


                    else:
                        next_arrival_time = 60*float(simTime[train][j+4])   # Arrival Time
                lis.append(round(next_arrival_time)-86400)          # Day-2 train

            if(next_station=='-'):
                runtime = 0   # Runtime 0 for last station
            else:
                runtime = round(next_arrival_time)-round(departure_time)-round(EA_value)-round(TA_value)-round(acc_time_loss)-round(dec_time_loss)

            lis.append(runtime)                      # Append Runtime
            dictionary_data = {}
            for i,l in enumerate(column_names):
                dictionary_data[l] = lis[i]
                # print("before exitting", i, lis[i], l, dictionary_data[l], type(dictionary_data[l]))
                # sys.exit(1)
            dictionary_list.append(dictionary_data)

            j+=3            # Goto the next station
            i+=1
        # while loop ends and repeates
    except KeyError: 
        rogTrnLst.append(train)
        print("\nSatSang format not created for "+str(train), "due to KeyError (Bhushan)", curr_station, next_station)
        continue

data_frame = pd.DataFrame.from_dict(dictionary_list)
data_frame.to_csv(postprocessPath+'SatSang_Format.csv')
print("SatSang format not created for {} trains out of {} total trains".format(len(rogTrnLst),len(train_nos)))
end_time = time.time()
print("\nProgram to required %.4f seconds to complete execution" % (end_time-start_time) )
