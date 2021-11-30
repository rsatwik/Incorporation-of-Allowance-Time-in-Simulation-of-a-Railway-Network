# import pandas as pd
# import numpy as np
# import math
# import sys
# from decimal import Decimal
# from tqdm import tqdm

# inputPath='../common/' # path to input files
# outputPath='temporary_files/' # path to output files


# #print('1.NDLS-MMCT\n2.NDLS-MAS\n3.HWH-MAS\n4.CSMT-HWH\n5.CSMT-MAS\n6.NDLS-HWH\n')
# if len(sys.argv) < 3:
#     print(' Incorrect usage: give number as an argument:')
#     print('   1.NDLS-MMCT \n   2.NDLS-MAS  \n   3.HWH-MAS  \n', \
#                      '  4.CSMT-HWH  \n   5.CSMT-MAS  \n   6.NDLS-HWH')
#     print(' Give the appropriate integer [1..6] as argument and run again.')
#     sys.exit(1)

# userInput=int(sys.argv[1])

# truncationDisabled = int(sys.argv[2])
# '''
# if userInput == 1:
#     infraPath='simulator_input/1_NDLS-MMCT/' # path to infrastructure
# elif userInput == 2:
#     infraPath='simulator_input/2_NDLS-MAS/' # path to infrastructure
# elif userInput == 3:
#     infraPath='simulator_input/3_HWH-MAS/' # path to infrastructure
# elif userInput == 4:
#     infraPath='simulator_input/4_HWH-CSMT/' # path to infrastructure
# elif userInput == 5:
#     infraPath='simulator_input/5_MASB-CSMT/' # path to infrastructure
# elif userInput == 6:
#     infraPath='simulator_input/6_NDLS-HWH/' # path to infrastructure
# '''

# infraPath='simulator_input/'
# #####################################################################################################################

# df2=pd.read_csv(outputPath+'ModifiedAndDailyTrains6.csv')
# df2=df2.astype({'Unnamed: 0':str})
# df2=df2.set_index('Unnamed: 0')

# df3=df2.iloc[[0]].copy(deep=True)
# df3=df3.drop(df2.iloc[[0]].index[0])     # creates an empty dataframe df2

# cleantraindata=df2.index.drop_duplicates()

# for train in cleantraindata:

#     try:
#         actualTrainNo=int(str(train)[-5:]) if (str(train)[0]=='9')&(len(str(train))==6) else int(train)
#     except ValueError:
#         print('cannot find actual train number for:',train)
#         continue

#     try:
#         dftemp=(df2.loc[[train]].sort_values(by='SEQ')).copy(deep=True)
#     except Exception as e:
#         print(e.__class__,'**Could not make dftemp**',train)
#         sys.exit(1)

#     # https://docs.google.com/spreadsheets/d/1e12z8MQmc8m0-CrDLNOI2nXErUSkOTVta4AoNCQREA0/edit#gid=160408357
#     # Exceptions for each route (in fact all routes? -Madhu)
#     if True: # 3rd line trains # Madhu changed to True on 12th July (after NR/Satwik)
#         # if str(actualTrainNo) in ['64055','64053','12963','19670','64167']:
#             # dftemp=dftemp[~dftemp.loc[:,'SEQ'].isin(dftemp.loc[:,'SEQ'].to_list()[-2:])]
#         # if str(actualTrainNo) in ['12964']:
#             # dftemp=dftemp[~dftemp.loc[:,'SEQ'].isin(dftemp.loc[:,'SEQ'].to_list()[0:2])]
        
#         #MTJ-PWL-NDLS
#         try:
#             if str(actualTrainNo) in ['19019','14211','12919']:
#                 endPoint=int(dftemp[dftemp['STATION']=='PWL']['SEQ'][0]) # find where  endstation
#                 # endPoint is integer and sequence number for that train, for PWL -Madhu
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#                 # getting rid of latter stations -Madhu
#             if str(actualTrainNo) in ['12903','22209']: # end point change to PWL
#                 endPoint=int(dftemp[dftemp['STATION']=='MTJ']['SEQ'][0])
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#             if str(actualTrainNo) in ['12926','11058','12904']: # starting point change to MTJ
#                 startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='MTJ']['SEQ'][0])
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
#                 # overwrite

#             #GZB-NZM
#             if str(actualTrainNo) in ['19020','14318','14320','12172','12912','22918']: # starting point change to MTJ
#                 startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='NZM']['SEQ'][0])
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
#             if str(actualTrainNo) in ['18237','14317','14319','12171','12911','22917']:
#                 endPoint=int(dftemp[dftemp['STATION']=='NZM']['SEQ'][0])
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#             if len(list(dftemp['STATION']))==1: # for CHANGED (over-shortened routes, skip train)
#                 print(train,'has single station on the route after 3rd line adjustment**')
#                 continue

#             # NDLS-ALJN
#             if str(actualTrainNo) in ['14163','64581','64583','64168']:
#                 endPoint=int(dftemp[dftemp['STATION']=='ALJN']['SEQ'][0])
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]

#             #HWH-CSMT
#             if str(actualTrainNo) in ['66047']:
#                 endPoint=int(dftemp[dftemp['STATION']=='AJJ']['SEQ'][0])
#                 dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#             if str(train) in ['66048']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='AJJ']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))] 
            

#             if not truncationDisabled:
#                 #STN-SKG
#                 if str(actualTrainNo) in ['22387']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='STN']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
#                 if str(train) in ['919607']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='STN']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
#                 if str(actualTrainNo) in ['22388']:
#                     endPoint=int(dftemp[dftemp['STATION']=='ALJN']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#                 if str(actualTrainNo) in ['13009']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='STN']['SEQ'][0])
#                     endPoint=int(dftemp[dftemp['STATION']=='JTHT']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,endPoint+1))]
#                 if str(actualTrainNo) in ['13010']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='JTHT']['SEQ'][0])
#                     endPoint=int(dftemp[dftemp['STATION']=='STN']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,endPoint+1))]

            
#             #### Train removed due to exceptions
#             #### 13239
# 		    ####13239
# 		    ####13240
# 		    ####13240
# 		    ####22971
# 		    #### 18238
# 		    #### 18477
# 		    #### 18478
# 		    ####12141
#             ####12142
#             ####12519
#             ####16359
#             ####16360
#             ####12335
#             ####12336
#             ####15547
#             ####15548
            
#                 #NEWC-JTHT
#                 if str(actualTrainNo) in ['12149','12947','15631','25631','13008','12424','12310','12436','22406','12236','12318','12316','12326','12368','19421','12394','12392','13258','12304','63264','22352','14006','12578','15635','11106','15667','15125','20802','63234','12741','13424','19063','14004','14008','14016','22947','13134','13120','13430','15564','15956','22450','14038','14020','12546','82356','12362','19313','19321','12328','12370','63228','22356','13414','13484','63226','13238','19669','12356','13006','12506','54272','22913','12334','12396','12488','13050','15484','17610','12332','12274','22466','20504','20506','15623']:
#                     endPoint=int(dftemp[dftemp['STATION']=='NEWC']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#                 if str(actualTrainNo) in ['12150','12948','15632','25632','13007','12423','12309','12435','22405','12235','12317','12315','12325','12367','19422','12393','12391','13257','12303','63263','22351','14005','12577','15636','11105','15668','15126','20801','63233','12742','12520','13423','22353','19064','14003','14007','14015','22948','13133','13119','13429','15563','15955','22449','14037','14019','12545','82355','12361','19314','19322','12327','12369','63227','22355','13413','13483','63225','13237','19670','12355','13005','12505','54271','22914','12333','12395','12487','13049','15483','17609','22972','12331','12273','22465','20503','20505','15624']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='NEWC']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
#                 if str(actualTrainNo) in ['13307','18609','12875','18103','14223','18631','18611','18311','15021','63557','12371','12353','12381','63553','11046','12357','13167','13151']:
#                     endPoint=int(dftemp[dftemp['STATION']=='JTHT']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(int(list(dftemp['SEQ'])[0]),endPoint+1))]
#                 if str(actualTrainNo) in ['13308','18610','12876','18104','14224','18632','18612','18312','15022','63558','12372','12354','12382','63554','11045','12358','13152']:
#                     startPoint=int(df2.loc[train][df2.loc[train]['STATION']=='JTHT']['SEQ'][0])
#                     dftemp=dftemp[dftemp['SEQ'].isin(range(startPoint,int(list(dftemp['SEQ'])[-1])+1))]
#         except:
#         	print(actualTrainNo," station error.")

#         if len(list(dftemp['STATION']))==1: # for CHANGED (over-shortened routes, skip train)
#             print(train,'has single station on the route after 3rd line adjustment**')
#             continue # talk to NR/Satwik and then replace ==1 with < 5

#     df3 = pd.concat([df3,dftemp])

# df3.to_csv(outputPath+'ModifiedAndDailyTrains7.csv')
