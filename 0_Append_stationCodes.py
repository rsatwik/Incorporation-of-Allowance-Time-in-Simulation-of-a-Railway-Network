import pandas as pd
import numpy as np
import math
import sys
from decimal import Decimal
from tqdm import tqdm

inputPath='../common/' # path to input files
outputPath='temporary_files/' # path for output

########################################################################################################

#stationTxtDF=pd.read_csv(infraPath+'station.txt',sep=' ',index_col=0)

gqdDF=pd.read_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress.csv',low_memory=False)
gqdDF['Stn. Code']=10001
stationCodeDF=pd.read_csv('preprocessed_files/StationCode.csv',index_col='Stations')

for index,row in tqdm(gqdDF.iterrows()):
	try:
	    train=row['TRAIN']
	    station=row['STATION']
	    gqdDF.loc[index,'Stn. Code']=stationCodeDF.loc[station,'stncode']
	except:
		continue
		# print(str(station)+',')

gqdDF=gqdDF.astype({'TRAIN': str})
gqdDF=gqdDF.set_index('TRAIN')

gqdDF.to_csv(inputPath+'GQD_Schedule_04thJuly20_WorkInProgress-StationCodes.csv')
