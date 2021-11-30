import sys
import pandas as pd
from tqdm import tqdm
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#### Added by Soham
temporary_files="temporary_files/"
infraPath = "simulator_input/"
simulator_out = "simulator_output/"
commonPath = '../common/'
####


print("\nReading the cleaned train list...")
df = pd.read_csv(temporary_files + 'cleaned_train_list2.csv')      # Get EA and TA rates
allowance_dict = {}
for i in tqdm(df.index.tolist()):
    dic = {}
    dic['ea_rate'] = df.iloc[i]['EAminsPer100km']
    dic['ta_rate'] = df.iloc[i]['TAminsPer100km']
    allowance_dict[str(int(df.iloc[i]['Train_no']))] = dic
print("\nDone getting the allowance rates for every train...")

print("\nGetting the acceleration and deceleration losses...")
acc_dec_losses = pd.read_csv(commonPath + 'acc_decc_losses.csv')
acc_dec_loss = {}
#print(speed_dict['1012297'])
for i in tqdm(acc_dec_losses.index.tolist()):
    acc_dec_loss[str(int(acc_dec_losses.iloc[i]['train_speed(kmph)'])),str(round(acc_dec_losses.iloc[i]['acc(m/s2)'],3)),str(acc_dec_losses.iloc[i]['decc(m/s2)'])] = round(acc_dec_losses.iloc[i]['loss']/60,2)

print("\nDone getting the acceleration ND deceleration losses for trains....")


print("\n This code would work route-wise only and not for pan-X routes at a time\n")
print("\nExtracting station  from station.txt...")
stn = open(infraPath + 'station.txt').readlines()[2:]
station_dict = {k.split()[0]:k.split()[2] for k in stn}
stn_list_up = [s for s in station_dict]           # from ndls to mmct up direction trains
stn_list_down = stn_list_up.copy()
stn_list_down.reverse()       #

print("\nExtracting station dictionary from loop.txt...")
loop = open(infraPath + 'loop.txt').readlines()[2:]
loop_dict = {k.split()[0]:k.split()[3] for k in loop}
loop_dict_reverse = {}
for s in station_dict:
    loop_dict_reverse[s] = []
    for l in loop_dict:
        if(loop_dict[l]==s):
            loop_dict_reverse[s].append(l)


#### needs to be changed
#route = int(sys.argv[1])
#if route==1:
#    IC_station_list_down = ['MMCT','BSR','VAPI','ST','BRC','GDA','RTM','NAD','KOTA','SWM','GGC','MTJ','PWL','NDLS']
#elif route==2:
#    IC_station_list_down = ['NDLS','AGC','DHO','GWL','JHS','BPL','ET','NGP','BPQ','WL','KI','BZA','GDR','MASA'][::-1]
#elif route==3:
#    IC_station_list_down = ['HWHA','KGP','BHC','CTC','BBS','NWP','VSKP','RJY','BZA','GDR','MASA'][::-1]
#elif route==4:
#    IC_station_list_down = ['HWHA','KGP','RHE','TATA','ROU','JSG','BSP','URK','MUP','NGP','BD','BSL','MMR','IGP','KYN','CSMT'][::-1]
#elif route==5:
#    IC_station_list_down = ['CSMT','LNL','PUNE','DD','WADI','RU','MASB']
#else:
#    IC_station_list_down = ['NDLS','GZB','TDL','ETW','CNB','PRYJ','DDU','SEB','GAYA','GMO','DHN','KAN','HWHB'][::-1]
    
print("\nGetting station list from station.txt file....")

station = open(infraPath +'station.txt').readlines()[2:]
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

dfs = dfs[dfs['route']==sys.argv[1]]                    # Route 1, Route 4, and Route 5 exception towards 'CSMT,MMCT' > i.e. up  
dfs = dfs[dfs['allowanceStation']=='yes']               # Route 4 is HWH CSMT      
IC_station_list_down = [l for l in list(dfs['StationCode']) if l in station_list]

if sys.argv[1] not in ['1','5']:
    IC_station_list_down = IC_station_list_down[::-1]

print("\nThe IC and major arrival list is as follows:\n")
print(IC_station_list_down)
print("\n Above was the IC and major arrival list\n\n")

IC_station_list_up = IC_station_list_down.copy()
IC_station_list_up.reverse()           # NDLS to MMCT is up
IC_station_list = IC_station_list_down

print("\n\nThis is the IC station list {}".format(IC_station_list))

def goes_through_IC_point(start_loop,end_loop,direction,stn_list_down,stn_list_up,loop_dict):
    if(direction=='up'):
        # NDLS to MMCT
        for s in IC_station_list_up:         # up list NDLS to MMCT
            if(stn_list_up.index(loop_dict[start_loop])<=stn_list_up.index(s) and stn_list_up.index(loop_dict[end_loop])>=stn_list_up.index(s)):
                return True
        return False
    else:
        for s in IC_station_list_down:      # down list MMCT to NDLS
            if(stn_list_down.index(loop_dict[start_loop])<=stn_list_down.index(s) and stn_list_down.index(loop_dict[end_loop])>=stn_list_down.index(s)):
                return True
        return False


#print("\nUP is from NDLS to MMCT\n")
print("\nExtracting info from unscheduled.txt........\n\n")
unsch = open(infraPath + 'unscheduled1.txt').readlines()[2:]
speed_dict = {u.split()[0]:(u.split()[7],u.split()[4],u.split()[5]) for u in unsch}
# train_nos = [u.split()[0] for u in unsch]
direction_dict = {u.split()[0]:u.split()[1] for u in unsch}              # direction dictionary
speed_dict = {u.split()[0]:(u.split()[7],u.split()[4],u.split()[5]) for u in unsch}
# train_nos_up = [t for t in train_nos if direction_dict[t]=='up']
# train_nos_down = [t for t in train_nos if direction_dict[t]=='down']
# priority_dict ={u.split()[0]:u.split()[6] for u in unsch}

lis = []
exceptionStationList1=['X101' ,'X102' ,'X103' ,'KSRA' ,'OMB' ,'KE' ,'THS' ,'ATG' ,'ASO' ,'VSD' ,'KDV' ,'TLA' ,'ABY' ,'SHAD','KYN' ,'DI' ,'DIVA','TNA' ,'MLND','VK' ,'GC' ,'CLA' ,'DR' ,'BY' ,'CSMT']
exceptionStationList2=['LNL','KAD','MHLC','TKW','JBC','PDI','KJT','BVS','NRL','SHLU','VGI','BUD','ABH','ULNR','VLDI','KYN','DI','DIVA','TNA','MLND','VK','GC','CLA','DR','BY','CSMT']
exceptionStationList3=['BSR','BYR','BVI','ADH','BA','DDR','MMCT']
exceptionStationList=exceptionStationList1+exceptionStationList2+exceptionStationList3


for u in tqdm(unsch):
    temp = u.split()
    train_number = u.split()[0]
    start_loop = u.split()[8]
    end_loop = u.split()[9]
    
    if((loop_dict[end_loop] in exceptionStationList) and (u.split()[1]=='up')):
        lis.append(' '.join(temp))
        continue

    if(loop_dict[end_loop] in IC_station_list):               # Ends at an IC point that's all
        lis.append(' '.join(temp))
        continue
    else:

        if(not goes_through_IC_point(start_loop,end_loop,direction_dict[train_number],stn_list_down,stn_list_up,loop_dict)):
            # train touches no IC point
#             print(train_number)
#             print(loop_dict[start_loop],loop_dict[end_loop])
            # Here 2-3 stations before the end station give a allowance halt
            # again calculate the allowance from a distance measure
            # Then allocate 1-2-3 halts respectively
            ea_rate = allowance_dict[train_number[-5:]]['ea_rate']
            ta_rate = allowance_dict[train_number[-5:]]['ta_rate']
            total_allowance = abs(float(station_dict[loop_dict[start_loop]])-float(station_dict[loop_dict[end_loop]]))*(ea_rate+ta_rate)/100
#             print(total_allowance)
            if(total_allowance<7):           # Only one halt
                if(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8>0): # Allowance can indeed be allocated
                    if(direction_dict[train_number]=='up'):         # NDLS to MMCT
                        prev_station = stn_list_up[stn_list_up.index(loop_dict[end_loop])-1]
                        if(prev_station in temp):              # The halt needs to be extended
#                             print(temp)
                            temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2))
#                             print(temp)
                        else:
#                             print(temp)
                            # The halt needs to be inserted
                            if(loop_dict[end_loop] in temp):                  # last station in temp
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2)))
                            else:             # At the very end
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2)))
#                             print(temp)

                    else:       # down direction                                      # MMCT to NDLS
                        prev_station = stn_list_down[stn_list_down.index(loop_dict[end_loop])-1]
                        if(prev_station in temp):              # The halt needs to be extended
#                             print(temp)
                            temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2))
#                             print(temp)
                        else:
#                             print(temp)
                            # The halt needs to be inserted
                            if(loop_dict[end_loop] in temp):                  # last station in temp
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2)))
                            else:             # At the very end
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2)))
#                             print(temp)
            else:              # 2 stations !!!!!!!!
                if(direction_dict[train_number]=='up'):
                    prev_station = stn_list_up[stn_list_up.index(loop_dict[end_loop])-1]
                    prev_prev_station = stn_list_up[stn_list_up.index(loop_dict[end_loop])-2]
                    halt_dur = (total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8*2)/2
#                     print(temp)
                    if(prev_station in temp):
                        temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_dur,2))
                    if(prev_prev_station in temp):
                        temp[temp.index(prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_station)+1])+halt_dur,2))
                    if(prev_station not in temp and prev_prev_station not in temp):
                        if(loop_dict[end_loop] in temp):            # Last station is indeed present
                            temp.insert(-2,prev_station)
                            temp.insert(-2,str(round(halt_dur,2)))
                            temp.insert(-4,prev_prev_station)
                            temp.insert(-4,str(round(halt_dur,2)))
                        else:
                            temp.insert(len(temp),prev_prev_station)
                            temp.insert(len(temp),str(round(halt_dur,2)))
                            temp.insert(len(temp),prev_station)
                            temp.insert(len(temp),str(round(halt_dur,2)))
                    if(prev_station not in temp):
                        if(loop_dict[end_loop] in temp):
                            temp.insert(-2,prev_station)
                            temp.insert(-2,str(round(halt_dur,2)))
                        else:
                            temp.insert(len(temp),prev_station)
                            temp.insert(len(temp),str(round(halt_dur,2)))
                    if(prev_prev_station not in temp):
                        if(loop_dict[end_loop] in temp):       # both are present
                            temp.insert(-4,prev_prev_station)
                            temp.insert(-4,str(round(halt_dur,2)))
                        else:                           # only prev station is present
                            temp.insert(-2,prev_prev_station)
                            temp.insert(-2,str(round(halt_dur,2)))
#                     print(temp)
                else:
                    prev_station = stn_list_down[stn_list_down.index(loop_dict[end_loop])-1]
                    prev_prev_station = stn_list_down[stn_list_down.index(loop_dict[end_loop])-2]
                    halt_dur = (total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8*2)/2
#                     print(temp)
                    # prev station present, extend the halt duration
                    if(prev_station in temp):
                        temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_dur,2))
                    if(prev_prev_station in temp):
                        temp[temp.index(prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_station)+1])+halt_dur,2))
                    if(prev_station not in temp and prev_prev_station not in temp):
                        if(loop_dict[end_loop] in temp):            # Last station is indeed present
                            temp.insert(-2,prev_station)
                            temp.insert(-2,str(round(halt_dur,2)))
                            temp.insert(-4,prev_prev_station)
                            temp.insert(-4,str(round(halt_dur,2)))
                        else:
                            temp.insert(len(temp),prev_prev_station)
                            temp.insert(len(temp),str(round(halt_dur,2)))
                            temp.insert(len(temp),prev_station)
                            temp.insert(len(temp),str(round(halt_dur,2)))
                    if(prev_station not in temp):
                        if(loop_dict[end_loop] in temp):
                            temp.insert(-2,prev_station)
                            temp.insert(-2,str(round(halt_dur,2)))
                        else:
                            temp.insert(len(temp),prev_station)
                            temp.insert(len(temp),str(round(halt_dur,2)))
                    if(prev_prev_station not in temp):
                        if(loop_dict[end_loop] in temp):       # both are present
                            temp.insert(-4,prev_prev_station)
                            temp.insert(-4,str(round(halt_dur,2)))
                        else:                           # only prev station is present
                            temp.insert(-2,prev_prev_station)
                            temp.insert(-2,str(round(halt_dur,2)))
#                     print(temp)




#             continue

        else:                 # train goes through atleast one IC point
            # just worry about the last IC point to the next station
            if(direction_dict[train_number]=='up'):              # NDLS to MMCT
                for i,s in enumerate(IC_station_list_up):           # NDLS to MMCT
                    if(stn_list_up.index(loop_dict[end_loop])>stn_list_up.index(s) and stn_list_up.index(loop_dict[end_loop])<stn_list_up.index(IC_station_list_up[i+1])):
                        last_ic = s
                        end_station = loop_dict[end_loop]
#                         print(train_number,last_ic,end_station)
                        break           # This direction is from NDLS to MMCT

            elif(direction_dict[train_number]=='down'):
                for i,s in enumerate(IC_station_list_down):           # MMCT to NDLS
                    if(stn_list_down.index(loop_dict[end_loop])>stn_list_down.index(s) and stn_list_down.index(loop_dict[end_loop])<stn_list_down.index(IC_station_list_down[i+1])):
                        last_ic = s
                        end_station = loop_dict[end_loop]
#                         print(train_number,last_ic,end_station)
                        break           # This direction is from NDLS to MMCT
            if(abs(float(station_dict[last_ic])-float(station_dict[end_station]))>15):       # Else don't care
                ea_rate = allowance_dict[train_number[-5:]]['ea_rate']
                ta_rate = allowance_dict[train_number[-5:]]['ta_rate']
                total_allowance = abs(float(station_dict[last_ic])-float(station_dict[end_station]))*(ea_rate+ta_rate)/100

                if(direction_dict[train_number]=='up'):          # NDLS to MMCT
                    if(total_allowance<7):         # 1 station
#                         print(temp)
                        if(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8>0):
                            prev_station = stn_list_up[stn_list_up.index(end_station)-1]
                            halt_duration = round(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2)

                            if(prev_station in temp):
                                temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_duration,2))
                            else:
                                if(loop_dict[end_loop] in temp):
                                    temp.insert(-2,prev_station)
                                    temp.insert(-2,halt_duration)
                                else:
                                    temp.insert(len(temp),prev_station)
                                    temp.insert(len(temp),halt_duration)
#                         print(temp)

                    elif(total_allowance<14):
                        prev_station = stn_list_up[stn_list_up.index(end_station)-1]
                        prev_prev_station = stn_list_up[stn_list_up.index(end_station)-2]
                        halt_dur = (total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8*2)/2
#                         print(temp)
                        # prev station present, extend the halt duration
                        if(prev_station in temp):
                            temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_dur,2))
                        if(prev_prev_station in temp):
                            temp[temp.index(prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_station)+1])+halt_dur,2))
                        if(prev_station not in temp and prev_prev_station not in temp):
                            if(loop_dict[end_loop] in temp):            # Last station is indeed present
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                        if(prev_station not in temp):
                            if(loop_dict[end_loop] in temp):
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                        if(prev_prev_station not in temp):
                            if(loop_dict[end_loop] in temp):       # both are present
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                            else:                           # only prev station is present
                                temp.insert(-2,prev_prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
#                         print(temp)

                    else:
                        prev_station = stn_list_up[stn_list_up.index(end_station)-1]
                        prev_prev_station = stn_list_up[stn_list_up.index(end_station)-2]
                        prev_prev_prev_station = stn_list_up[stn_list_up.index(end_station)-3]
                        halt_dur = (total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8*3)/3
#                         print(temp)
#                         print(prev_station,prev_prev_station,prev_prev_prev_station,end_station)
#                         print(stn_list_up)
                        # prev station present, extend the halt duration
                        if(prev_station in temp):
                            temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_dur,2))
                        if(prev_prev_station in temp):
                            temp[temp.index(prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_station)+1])+halt_dur,2))
                        if(prev_prev_prev_station in temp):
                            temp[temp.index(prev_prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_prev_station)+1])+halt_dur,2))
                        if(prev_station not in temp and prev_prev_station not in temp and prev_prev_prev_station not in temp):
                            if(loop_dict[end_loop] in temp):            # Last station is indeed present
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                                temp.insert(-6,prev_prev_prev_station)
                                temp.insert(-6,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_prev_prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                                temp.insert(len(temp),prev_prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))

                        if(prev_station not in temp):
                            if(loop_dict[end_loop] in temp):
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))

                        if(prev_prev_station not in temp):                        # prev_station is present here
                            if(loop_dict[end_loop] in temp):       # both are present
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                            else:                           # only prev station is present
                                temp.insert(-2,prev_prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))

                        if(prev_prev_prev_station not in temp):                        # prev_station is present here
                            if(loop_dict[end_loop] in temp):       # both are present
                                temp.insert(-6,prev_prev_prev_station)
                                temp.insert(-6,str(round(halt_dur,2)))
                            else:                           # only prev station is present
                                temp.insert(-4,prev_prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
#                         print(temp)
                else:                         # MMCT to NDLS
#                     print(temp)
                    if(total_allowance<7):         # 1 station
#                         print(temp)
                        if(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8>0):
                            prev_station = stn_list_down[stn_list_down.index(end_station)-1]
                            halt_duration = round(total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8,2)

                            if(prev_station in temp):
                                temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_duration,2))
                            else:
                                if(loop_dict[end_loop] in temp):
                                    temp.insert(-2,prev_station)
                                    temp.insert(-2,halt_duration)
                                else:
                                    temp.insert(len(temp),prev_station)
                                    temp.insert(len(temp),halt_duration)
#                         print(temp)

                    elif(total_allowance<14):
                        prev_station = stn_list_down[stn_list_down.index(end_station)-1]
                        prev_prev_station = stn_list_down[stn_list_down.index(end_station)-2]
                        halt_dur = (total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8*2)/2
#                         print(temp)
                        # prev station present, extend the halt duration
                        if(prev_station in temp):
                            temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_dur,2))
                        if(prev_prev_station in temp):
                            temp[temp.index(prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_station)+1])+halt_dur,2))
                        if(prev_station not in temp and prev_prev_station not in temp):
                            if(loop_dict[end_loop] in temp):            # Last station is indeed present
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                        if(prev_station not in temp):
                            if(loop_dict[end_loop] in temp):
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                        if(prev_prev_station not in temp):
                            if(loop_dict[end_loop] in temp):       # both are present
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                            else:                           # only prev station is present
                                temp.insert(-2,prev_prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
#                         print(temp)

                    else:
                        prev_station = stn_list_down[stn_list_down.index(end_station)-1]
                        prev_prev_station = stn_list_down[stn_list_down.index(end_station)-2]
                        prev_prev_prev_station = stn_list_down[stn_list_down.index(end_station)-3]
                        halt_dur = (total_allowance-acc_dec_loss[speed_dict[train_number]]*0.8*3)/3
                        print(temp)
#                         print(prev_station,prev_prev_station,prev_prev_prev_station,end_station)
#                         print(stn_list_up)
                        # prev station present, extend the halt duration
                        if(prev_station in temp):
                            temp[temp.index(prev_station)+1] = str(round(float(temp[temp.index(prev_station)+1])+halt_dur,2))
                        if(prev_prev_station in temp):
                            temp[temp.index(prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_station)+1])+halt_dur,2))
                        if(prev_prev_prev_station in temp):
                            temp[temp.index(prev_prev_prev_station)+1] = str(round(float(temp[temp.index(prev_prev_prev_station)+1])+halt_dur,2))
                        if(prev_station not in temp and prev_prev_station not in temp and prev_prev_prev_station not in temp):
                            if(loop_dict[end_loop] in temp):            # Last station is indeed present
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                                temp.insert(-6,prev_prev_prev_station)
                                temp.insert(-6,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_prev_prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                                temp.insert(len(temp),prev_prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))

                        if(prev_station not in temp):
                            if(loop_dict[end_loop] in temp):
                                temp.insert(-2,prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))
                            else:
                                temp.insert(len(temp),prev_station)
                                temp.insert(len(temp),str(round(halt_dur,2)))

                        if(prev_prev_station not in temp):                        # prev_station is present here
                            if(loop_dict[end_loop] in temp):       # both are present
                                temp.insert(-4,prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
                            else:                           # only prev station is present
                                temp.insert(-2,prev_prev_station)
                                temp.insert(-2,str(round(halt_dur,2)))

                        if(prev_prev_prev_station not in temp):                        # prev_station is present here
                            if(loop_dict[end_loop] in temp):       # both are present
                                temp.insert(-6,prev_prev_prev_station)
                                temp.insert(-6,str(round(halt_dur,2)))
                            else:                           # only prev station is present
                                temp.insert(-4,prev_prev_prev_station)
                                temp.insert(-4,str(round(halt_dur,2)))
        lis.append(' '.join([str(t) for t in temp]))



    #                         print(total_allowance-acc_dec_loss[speed_dict[train_number]]*2*0.8,2)
#                     else:
#                         prev_station = stn_list_up[stn_list_up.index(end_station)-1]
#                         prev_prev_station = stn_list_up[stn_list_up.index(end_station)-2]
#                         prev_prev_prev_station = stn_list_up[stn_list_up.index(end_station)-3]
# #                         print(train_number)
# #                         print(speed_dict[train_number])
# #                         print(total_allowance-acc_dec_loss[speed_dict[train_number]]*3*0.8,3)







# print(stn_list_up)        # NDLS to MMCT
# 2 cases when it ends at a non-IC point
# Second case when it starts in between and ends in between an IC-IC section

temp_lis = []
for l in lis:
    temp = l.split()
    le = (len(temp)-11)/2
    temp[10] = str(int(le))
    temp_lis.append(' '.join(temp))
lis = temp_lis

with open(infraPath + 'unscheduled-full.txt','w') as u:
    u.write('/*TrainNo. direction startTime(minutes) length(km) acceleration(m/s^2) deceleration(m/s^2) priority maximumSpeed(kmph) startLoop endLoop NumberOfHalts Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes) Station Halt(minutes)*/')
    u.write('\n\n')
    for k in lis:
        u.write(k)
        u.write('\n')
u.close()

