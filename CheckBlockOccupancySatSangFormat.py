# folder paths go here 
# Currently being done for Mumbai Delhi Route 
# The required files for this program are station.txt SatSang_Format.csv 

import pandas as pd
import time 
from tqdm import tqdm 
import sys 

############# Added by Bhushan Deo ######################
inputPath = "../common/"
infraPath = "simulator_input/"
sim_out = "simulator_output/"
postprocessPath = "postprocessed_files/"
valdir = "validation/"
#########################################################


def seconds_to_HHMM(seconds):
    return time.strftime('%H:%M', time.gmtime(seconds)) 



print("\nCreating up and down direction block lists ")
station = [u.split()[0] for u in open(infraPath+'station.txt','r').readlines()[2:]]
block_up = [str(s)+'-'+str(station[i+1]) for i,s in enumerate(station) if i<len(station)-1]
block_down = [str(s)+'-'+str(station[::-1][i+1]) for i,s in enumerate(station[::-1]) if i<len(station[::-1])-1]
print("\nCreated up and down block lists ")

print("\nReading SatSang format into a dataframe....")
satsang_df = pd.read_csv(postprocessPath+'SatSang_Format.csv')
print("\n Finding conflicts for up direction blocks.....")
satsang_df['TRAINNUMBER'] = satsang_df['TRAINNUMBER'].astype('category')
satsang_df['BLCKSCTN'] = satsang_df['BLCKSCTN'].astype('category')
satsang_df['NEXTARVL'] = satsang_df['NEXTARVL'].astype('category')
satsang_df['DPRTTIME'] = satsang_df['DPRTTIME'].astype('category')
with open(valdir+'SatSang_block_occupancy.txt','w') as stxt:
    stxt.write("Writing SatSang block occupancies\n")
    for bu in block_up:
        curr_df=satsang_df.loc[satsang_df['BLCKSCTN']==bu].sort_values('NEXTARVL').reset_index()[['TRAINNUMBER','DPRTTIME','NEXTARVL']]
        if [i for i, j in zip(list(curr_df['DPRTTIME'][1:]), curr_df['NEXTARVL'][:-1]) if i < j]:
            dprt_time=[(i,j) for i, j in zip(list(curr_df['DPRTTIME'][1:]), curr_df['NEXTARVL'][:-1]) if i < j]
            for k in dprt_time:
                first_train = curr_df.iloc[curr_df.index[curr_df['NEXTARVL'] == k[1]].tolist()[0]]
                second_train = curr_df.iloc[curr_df.index[curr_df['DPRTTIME'] == k[0]].tolist()[0]]
                stxt.write("\n")
                stxt.write("{} occupies {} from {} to {}, {} occupies {} from {} to {}".format(str(first_train['TRAINNUMBER']),str(bu),str(seconds_to_HHMM(int(first_train['DPRTTIME']))),str(seconds_to_HHMM(int(first_train['NEXTARVL']))),str(second_train['TRAINNUMBER']),str(bu),str(seconds_to_HHMM(int(second_train['DPRTTIME']))),str(seconds_to_HHMM(int(second_train['NEXTARVL'])))))

    


    stxt.close()


# end_time = time.time()
# print("Program required {} to complete execution".format(end_time-start_time))


