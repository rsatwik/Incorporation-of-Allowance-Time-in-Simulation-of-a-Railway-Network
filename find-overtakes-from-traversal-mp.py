#usage: python3 find-overtakes-from-traversal-mp.py <path-of-infra> <time-table-not-detailed.csv>
import multiprocessing as mp
import pandas as pd
from tqdm import tqdm
import sys
import os

# this function finds all overtakes at a given stn
# returns overtakes as dataframe with columns=['Overtaking_T.No.','Dir','stn_code','arr','dep','H.Time','Overtaken_T.No.']

#### Added by Soham
infraPath = "simulator_input/"
simulator_out = "simulator_output/"
postprocessed_path = "postprocessed_files/"
####

def find_overtakes_station(stn_code):
    global overtake_data_all
    tt_data_stn=tt_data_stn_all[tt_data_stn_all['stn']==stn_code].copy()
    # print('\n--- '+str(len(tt_data_stn))+' trains go through station: '+stn_code)
    # print(stn_code)
    # tt_data_stn[['T.No.',,arr,dep,H.Time]] = tt_data_stn[['T.No.','arr','dep','H.Time']].apply(to_numeric)
    overtake_data = pd.DataFrame(columns=['trainno','dir','stn','arr','dep','halt','A.T.No.'])
    for index, tt_row in tt_data_stn.iterrows():
        # Train represented by tt_data_stn overtakes tt_row
        overtakes = tt_data_stn[(tt_row['dir'] == tt_data_stn['dir']) &
                                (tt_row['arr'] < tt_data_stn['arr'])
                                & (tt_row['dep'] > tt_data_stn['dep'])].copy()
        if not overtakes.empty:
            # all these trains were overtaken by tt_row's train no.
            overtakes.loc[:, 'A.T.No.'] = int(tt_row['trainno'])
            # overtakes.loc[:, 'Loop'] = stn_code
            overtake_data = overtake_data.append(
                # overtakes[['T.No.', 'A.T.No.']], ignore_index=True)
                overtakes, ignore_index=True)
    overtake_data = overtake_data.rename(columns={'trainno': 'Overtaking_T.No.', 'A.T.No.': 'Overtaken_T.No.','stn':'stn_code'})
    return overtake_data

# Main code starts here
stn_data=pd.read_csv(infraPath +'station.txt',delimiter=" ",names=['name','start','end','entry'],header=0)[['name']]
stn_code_list=stn_data.name.to_list()
# read the intermediate file created by generate-timetable-not-detailed.php
tt_data_stn_all = pd.read_csv(postprocessed_path+'/timetable-not-detailed.csv')

overtake_data_all = pd.DataFrame(columns=['Overtaking_T.No.','dir','stn_code','arr','dep','halt','Overtaken_T.No.'])
print('Finding overtakes ...')
with mp.Pool(mp.cpu_count()) as p:
    result=list(tqdm(p.imap(find_overtakes_station,stn_code_list),total=len(stn_code_list)))
    overtake_data_all=overtake_data_all.append(result,ignore_index=True)
    p.close()
    p.join()

print(overtake_data_all)
overtake_data_all.to_csv(postprocessed_path+"overtakes.csv",index=False)
