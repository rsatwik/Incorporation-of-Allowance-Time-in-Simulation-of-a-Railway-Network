# IC Sectional details for division based analysis

# The dataframe would have the following columns
import pandas as pd
from collections import defaultdict
import os
from tqdm import tqdm
from pandas import ExcelWriter
import glob
import sys

### Added by Soham
infraPath = "simulator_input/"
sim_out = "simulator_output/"
postprocessPath = "postprocessed_files/"
commonPath="../common/"
##############


# the reference stations needs to be route specific
#route = int(sys.argv[1])
#if route==1:
#    reference_stations_up = ['NDLS','MMCT']
#elif route==2:
#    reference_stations_up = ['NDLS','MASA']
#elif route==3:
#    reference_stations_up = ['HWHA','MASA']
#elif route ==4:
#    reference_stations_up = ['HWHA','CSMT']
#elif route==5:
#    reference_stations_up = ['MASB','CSMT']
#else:
#    reference_stations_up = ['NDLS','HWHB']

# These are up direction stations
#reference_stations_down = reference_stations_up.copy()
#reference_stations_down.reverse()

# Train Number
# Start-End Station in that division
# Km.
# Time of Run
# Average Speed
# Then a overall sheet
# Optional is number of total halts train experiences in that section
# Optional is allowance given for that train in that IC-IC section

print("################# Files Required for this program are.....######### ")
print("\n Station.txt Loop.txt Unscheduled.txt TraversalDetails.txt \n")

unshed = {}
with open(infraPath+'unscheduled.txt') as s:
    for row in s.readlines()[2:]:
        x=row.strip().split(' ')
        unshed[x[0][2:]]=x[1]

def get_first_station(traversal_list_actual_time,station_1,station_2,stn_list,station_dict):
    for i,s in enumerate(traversal_list_actual_time):

        if(stn_list.index(station_dict[s])>=stn_list.index(station_1) and stn_list.index(station_dict[s])<stn_list.index(station_2)):
            return s
        else:
            continue
    return 'None'

def get_last_station(traversal_list_actual_time,station_1,station_2,stn_list,station_dict):
    tr_list = traversal_list_actual_time.copy()
    tr_list.reverse()
    st_list = stn_list.copy()
    st_list.reverse()
    return(get_first_station(tr_list,station_2,station_1,st_list,station_dict))




def minutes_to_HHMM(minutes):
    minutes = minutes%1440           # Keep minutes between 0-1440
    hours = minutes//60
    mm = minutes%60
    if(len(str(hours))==1):
        hours = '0'+str(hours)
    if(len(str(mm))==1):
        mm = '0'+str(mm)
    return str(hours) + ':' + str(mm)

def adding_extra_columns():
    # in_df=pd.read_csv(commonPath+'TrainNameDetails.csv',header = 1)
    # print("---------------------------------------------------------------------------------------------------")
    # data_frame['Train-Name'],data_frame['Train-Type'],data_frame['Priority'] = 'No Data','No Data','No Data'
    # for i,j in data_frame.iterrows():
    #     try:
    #         data_frame.loc[i,'Priority']=int(in_df[in_df['Train']==j['Train'][1:7]]['priority'].values)
    #         data_frame.loc[i,'Train-Type']=in_df[in_df['Train']==j['Train'][1:7]]['Train-type'].values 
    #         data_frame.loc[i,'Train-Name']=in_df[in_df['Train']==j['Train'][1:7]]['Train-Name'].values 
    #     except KeyError:
    #         pass

    train_dict = {}
    with open(commonPath+'TrainNameDetails.csv') as f:
        for i in f.readlines()[2:]:
            train_no = i.split(",")[1]
            train_type = i.split(",")[8]
            train_name = i.split(",")[7]
            priority = i.split(",")[9]
            train_dict[train_no] = {"Number": train_no,"Type": train_type,"Name": train_name,"Priority":priority}
            
    data_frame["Type"]=""
    data_frame["Name"]=""
    data_frame["Priority"]=""
    data_frame["Direction"]=""
    for i,j in data_frame.iterrows():
        if str(j['Train'])[1:] in train_dict:
            data_frame.loc[i,'Name']=train_dict[str(j['Train'])[1:]]['Name']
            data_frame.loc[i,'Type']=train_dict[str(j['Train'])[1:]]['Type']
            data_frame.loc[i,'Priority']=train_dict[str(j['Train'])[1:]]['Priority']
            data_frame.loc[i,'Direction']=unshed[j['Train'][1:]]


# Get station dict and station dict reverse
print("\n Getting the station list...")
station = open(infraPath +'station.txt','r').readlines()[2:]
station_distance_dict = {s.split()[0]:s.split()[1] for s in station}
stn_list_up = [s.split()[0] for s in station]
stn_list_down = stn_list_up.copy()
stn_list_down.reverse()

reference_stations_up = [stn_list_up[0],stn_list_up[-1]]             # The first and the last stations are being put here....
# These are up direction stations
reference_stations_down = reference_stations_up.copy()
reference_stations_down.reverse()

print("\n Getting station-loop dictionaries...")
loop = open(infraPath +'loop.txt','r').readlines()[2:]
station_dict = {s.split()[0]:s.split()[3] for s in loop if s.split()[3] in stn_list_up}
station_dict_reverse = defaultdict(list)
[station_dict_reverse[s.split()[3]].append(s.split()[0]) for s in loop if s.split()[3] in stn_list_up]
station_dict_reverse = dict(station_dict_reverse)


# Get traversal dict actual time from the traversal details
with open(sim_out +'TraversalDetails.txt') as td:
    traversal_details=td.readlines()

print("\nExtracting Some traversal details from TraversalDetails.txt...")
current_train='None'
traversal_dict_actual_time={}
lis=[]
for t in tqdm(traversal_details):
    if('Printing timetables for train' in t):
        traversal_dict_actual_time[current_train]=lis
        current_train=t.split()[-1]
        lis=[]         # Empty list
    else:
        if(t.split()[2] not in station_dict):                                 # Not a block but a loop
            continue
        lis+=[t.split()[2],t.split()[11],t.split()[14]]                       # In minutes
traversal_dict_actual_time[current_train]=lis
del traversal_dict_actual_time['None']

print("\nExtracting day-2 trains list...")
# t_n_n= open('train_numbers_names.txt').readlines()[1:]
# train_type_dict = {t.split()[0]:t.split()[-1] for t in t_n_n}
unsch = open(infraPath+'unscheduled.txt','r').readlines()[2:]
train_nos = [u.split()[0] for u in unsch if u.split()[0][0]=='2']
direction_dict = {u.split()[0]:u.split()[1] for u in unsch if u.split()[0][0]=='2'}
maxspeed_dict = {u.split()[0]:u.split()[7] for u in unsch if u.split()[0][0]=='2'}
train_nos_up=[t for t in train_nos if direction_dict[t]=='up']
train_nos_down = [t for t in train_nos if direction_dict[t]=='down']

print("\n ...Done extracting required information")
print(train_nos)
# print(traversal_dict_actual_time['2069161'])

for s in reference_stations_down:                  # Start from MMCT and go to NDLS
    dictionary_list = []
    if(s==reference_stations_down[-1]):            # Last station break here
        break
    else:
        print("\n Compiling data for {}-{}".format(s,reference_stations_down[reference_stations_down.index(s)+1]))
        for train in train_nos:
            try:
                if(direction_dict[train]=='down'):
                    first_stn = get_first_station(traversal_dict_actual_time[train][0::3],s,reference_stations_down[reference_stations_down.index(s)+1],stn_list_down,station_dict)
                    last_stn = get_last_station(traversal_dict_actual_time[train][0::3],s,reference_stations_down[reference_stations_down.index(s)+1],stn_list_down,station_dict)
                    if(first_stn=='None' or last_stn=='None'):
                        print(first_stn,last_stn)
                        continue
                    section = str(station_dict[first_stn])+'-'+str(station_dict[last_stn])
                    time_of_run = abs(float(traversal_dict_actual_time[train][traversal_dict_actual_time[train].index(first_stn)+1])-float(traversal_dict_actual_time[train][traversal_dict_actual_time[train].index(last_stn)+1]))
                    distance = abs(float(station_distance_dict[station_dict[first_stn]])-float(station_distance_dict[station_dict[last_stn]]))
                    avg_speed = 60*distance/time_of_run
                    dictionary = {'Train':train[1:],'MPS(kmph.)':maxspeed_dict[train],'Section':section,'TOR(minutes)':time_of_run,'Dist(km)':distance,'Avg. Speed(kmph.)':avg_speed}
                    # ,'Type':train_type_dict[train[2:]]
                    dictionary_list.append(dictionary)
                else:                     # Direction is up
                    first_stn = get_first_station(traversal_dict_actual_time[train][0::3],reference_stations_down[reference_stations_down.index(s)+1],s,stn_list_up,station_dict)
                    last_stn = get_last_station(traversal_dict_actual_time[train][0::3],reference_stations_down[reference_stations_down.index(s)+1],s,stn_list_up,station_dict)
                    if(first_stn=='None' or last_stn=='None'):
                        print(first_stn,last_stn)
                        continue
                    section = str(station_dict[first_stn])+'-'+str(station_dict[last_stn])
                    time_of_run = abs(float(traversal_dict_actual_time[train][traversal_dict_actual_time[train].index(first_stn)+1])-float(traversal_dict_actual_time[train][traversal_dict_actual_time[train].index(last_stn)+1]))
                    distance = abs(float(station_distance_dict[station_dict[first_stn]])-float(station_distance_dict[station_dict[last_stn]]))
                    avg_speed = 60*distance/time_of_run
                    dictionary = {'Train':train[1:],'MPS(kmph.)':maxspeed_dict[train],'Section':section,'TOR(minutes)':time_of_run,'Dist(km)':distance,'Avg. Speed(kmph.)':avg_speed}
                    dictionary_list.append(dictionary)
            except KeyError:
                print('sid'+train)

    print(dictionary_list)
    data_frame = pd.DataFrame.from_dict(dictionary_list)
    adding_extra_columns()
    data_frame.to_excel(postprocessPath+'{}-{}.xlsx'.format(s,reference_stations_down[reference_stations_down.index(s)+1]),index=False)


print(data_frame)
writer = ExcelWriter(postprocessPath+"ETE_details.xlsx")
file_list = [postprocessPath+'{}-{}.xlsx'.format(s,reference_stations_down[reference_stations_down.index(s)+1]) for s in reference_stations_down if s!=reference_stations_down[-1]]
for filename in glob.glob(postprocessPath+"*.xlsx"):
    if(filename not in file_list):
        continue

    excel_file = pd.ExcelFile(filename)
    (_, f_name) = os.path.split(filename)
    (f_short_name, _) = os.path.splitext(f_name)
    for sheet_name in excel_file.sheet_names:
        df_excel = pd.read_excel(filename)
        df_excel.to_excel(writer, f_short_name, index=False)

writer.save()
