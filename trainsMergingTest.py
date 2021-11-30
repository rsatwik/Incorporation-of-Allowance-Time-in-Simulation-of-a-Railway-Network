import sys
import pandas as pd

# Read unscheduled.txt and find those trains which have nearly same starting times and priorities 
# At the same loop 


userInput=(sys.argv[1])

unsch = open(sys.argv[1]+'unscheduled.txt').readlines()[2:]
prob_same_trains = []
for u in unsch:
    train = u.split()[0]
    if(train[1]=='0'):
        continue
    direction = u.split()[1]
    start_time = u.split()[2]
    start_loop = u.split()[8]
    priority = u.split()[6]
    lis = [] 
    lis.append(train)
    for t in unsch[unsch.index(u)+1:]:
        ttrain = t.split()[0]
        tdirection = t.split()[1]
        tstart_time = t.split()[2]
        tstart_loop = t.split()[8] 
        tpriority = u.split()[6]
        if(tdirection==direction and tstart_loop==start_loop and priority==tpriority and abs(float(tstart_time)-float(start_time))<3):
            lis.append(ttrain)
    if(len(lis)>1):
        prob_same_trains.append(lis)
print(prob_same_trains)
dic = {}
dic_lis = []
for t in prob_same_trains:
    dic={'Train-1':t[0],'Train-2':t[1]}
    dic_lis.append(dic)
dataframe = pd.DataFrame.from_dict(dic_lis)
dataframe.to_excel(sys.argv[1]+'/Possible_Train_Merging.xlsx',index=False)
