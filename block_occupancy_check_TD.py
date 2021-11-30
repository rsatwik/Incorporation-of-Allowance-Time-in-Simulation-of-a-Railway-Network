# Checking Block Occupancy in TD file 
# The input files required are # TraversalDetails.txt # loop.txt # station.txt # unscheduled.txt 

from collections import defaultdict
import pandas as pd
import time
import sys                              # To take argument from the user here 

############# Added by Bhushan Deo ######################
inputPath = "../common/"
infraPath = "simulator_input/"
sim_out = "simulator_output/"
postprocessPath = "postprocessed_files/"
valdir = "validation/"
#########################################################

def seconds_to_HHMM(seconds):
    return time.strftime('%H:%M', time.gmtime(seconds)) 

TD = open(sim_out+'TraversalDetails.txt','r').readlines()
loop = open(infraPath+'loop.txt','r').readlines()[2:]
station = open(infraPath+'station.txt','r').readlines()[2:]
stn_list = [s.split()[0] for s in station]
station_dict = {s.split()[0]:s.split()[3] for s in loop if s.split()[3] in stn_list}
station_dict_reverse = defaultdict(list)
[station_dict_reverse[s.split()[3]].append(s.split()[0]) for s in loop if s.split()[3] in stn_list]
unsch = open(infraPath+'unscheduled.txt','r').readlines()[2:]
train_nos_up = [u.split()[0] for u in unsch if u.split()[1]=='up']
train_nos_down = [u.split()[0] for u in unsch if u.split()[1]=='down']
for i,t in enumerate(TD):
    if(i==len(TD)-1):
        TD_det[curr_train] = lis
        break
    if('Printing timetables for train' in t):
        if(i!=0):
            TD_det[curr_train] = lis
        else:
            TD_det={}
        curr_train = t.split()[-1]
        
        lis=[]
    else:
        if(t.split()[2] in station_dict):
            lis+=[t.split()[2],t.split()[11],t.split()[14]]

dictionary_list = []
print("\nDoing for up direction blocks....")
ref_train = str(sys.argv[1])              # Reference train which occupies the whole route in the up direction 
for l in TD_det[ref_train]:
    if(l in station_dict): 
        lis = []           # Lis of conflicting trains 
        st_stn = station_dict[l]
        if(st_stn==stn_list[-1]):
            break
        else:
            end_stn = stn_list[stn_list.index(st_stn)+1]       # Block is found out now
        for t in train_nos_up:
            for k in station_dict_reverse[st_stn]:
                if(k in TD_det[t] and k!=TD_det[t][-3]):            # Not the last loop of the train
                    dictionary = {'Block':str(st_stn)+'-'+str(end_stn),'Train':t,'Arr':TD_det[t][TD_det[t].index(k)+2] , 'Dep':TD_det[t][TD_det[t].index(k)+4]}
                    dictionary_list.append(dictionary)
                    break

up_dir_dataframe = pd.DataFrame.from_dict(dictionary_list)        
block_up = up_dir_dataframe['Block'].unique().tolist() 
up_dir_dataframe['Block']=up_dir_dataframe['Block'].astype('category')
up_dir_dataframe['Arr']=pd.to_numeric(up_dir_dataframe['Arr'])
up_dir_dataframe['Dep']=pd.to_numeric(up_dir_dataframe['Dep'])
# # Now we have the dataframe 
with open(valdir+'TD_block_occupancy.txt','w') as stxt:
    stxt.write("Traversal details block occupancies\n")
    for bu in block_up:
        curr_df=up_dir_dataframe.loc[up_dir_dataframe['Block']==bu].sort_values('Dep').reset_index()[['Block','Train','Arr','Dep']]
        if [i for i, j in zip(list(curr_df['Arr'][1:]), curr_df['Dep'][:-1]) if i < j]:
            dprt_time=[(i,j) for i, j in zip(list(curr_df['Arr'][1:]), curr_df['Dep'][:-1]) if i < j]
     
            for k in dprt_time:
                first_train = curr_df.iloc[curr_df.index[curr_df['Dep'] == k[1]].tolist()[0]]
                second_train = curr_df.iloc[curr_df.index[curr_df['Arr'] == k[0]].tolist()[0]]
                stxt.write("\n")
                stxt.write("{} occupies {} from {} to {}, {} occupies {} from {} to {}".format(str(first_train['Train']),str(bu),str(seconds_to_HHMM(60*float(first_train['Arr']))),str(seconds_to_HHMM(60*float(first_train['Dep']))),str(second_train['Train']),str(bu),str(seconds_to_HHMM(60*float(second_train['Arr']))),str(seconds_to_HHMM(60*float(second_train['Dep'])))))
    stxt.close()

print("\n Written occupancies in " + valdir + " TD_block_occupancy.txt")
