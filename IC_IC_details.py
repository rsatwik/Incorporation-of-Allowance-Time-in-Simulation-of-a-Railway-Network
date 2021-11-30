# IC Sectional details for division based analysis

# The dataframe would have the following columns
import pandas as pd
from collections import defaultdict
import os
from tqdm import tqdm
from pandas import ExcelWriter
import glob
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials


### Added by Soham
infraPath = "simulator_input/"
sim_out = "simulator_output/"
postprocessPath = "postprocessed_files/"
########

#### NEEDS CHANGE
#route = int(sys.argv[1])
#if route==1:
#    reference_stations_up = ['NDLS','PWL','MTJ','GGC','SWM','KOTA','NAD','RTM','BRC','ST','VAPI','MMCT']
#elif route==2:
#    reference_stations_up = ['NDLS','AGC','DHO','GWL','JHS','BPL','ET','NGP','BPQ','WL','KI','BZA','GDR','MASA']
#elif route==3:
#    reference_stations_up = ['HWHA','KGP','BHC','CTC','BBS','NWP','VSKP','RJY','BZA','GDR','MASA']
#elif route==4:
#    reference_stations_up = ['HWHA','KGP','RHE','TATA','ROU','JSG','BSP','URK','MUP','NGP','BD','BSL','MMR','IGP','KYN','CSMT']
#elif route==5:
#   reference_stations_up = ['MASB', 'AJJ', 'RU', 'GTL', 'WADI', 'SUR', 'DD', 'PUNE', 'LNL', 'KYN', 'CSMT']
#else:
#    reference_stations_up = ['NDLS','GZB','TDL','ETW','CNB','PRYJ','DDU','SEB','GAYA','GMO','DHN','KAN','HWHB']
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




# Get station dict and station dict reverse
print("\n Getting the station list...")
station = open(infraPath+'station.txt','r').readlines()[2:]
station_distance_dict = {s.split()[0]:s.split()[1] for s in station}
stn_list_up = [s.split()[0] for s in station]
stn_list_down = stn_list_up.copy()
stn_list_down.reverse()

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

dfs = dfs.loc[dfs['route']==sys.argv[1]]    
dfs= dfs[dfs['allowanceStation']=='yes']          # Route 4 is HWH CSMT    
  
reference_stations_up = [l for l in list(dfs['StationCode']) if l in station_distance_dict]


#reference_stations_up=reference_stations_up[::-1]

if sys.argv[1] in ['1','5']:
    reference_stations_down =  reference_stations_up
    reference_stations_up=reference_stations_up[::-1]
else:
    reference_stations_down =  reference_stations_up[::-1]    

print("\nThe IC and major arrival list is as follows:\n")
print(reference_stations_up)
print("\n Above was the IC and major arrival list\n\n")




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
unsch = open(infraPath +'unscheduled.txt','r').readlines()[2:]
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
                print("Key error ",train)
                

    print(dictionary_list)
    data_frame = pd.DataFrame.from_dict(dictionary_list)
    data_frame.to_excel(postprocessPath+'{}-{}.xlsx'.format(s,reference_stations_down[reference_stations_down.index(s)+1]),index=False)




writer = ExcelWriter(postprocessPath +"IC-IC_details.xlsx")
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
