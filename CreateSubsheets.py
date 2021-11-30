import glob
import pandas as pd
import os
from datetime import datetime
import sys

# Name of the combined excel sheet is passed as the second command line argument while running the script
# If the base name(the argument the is passed while calling the function) of the combined sheet is same then it will
# ignore the previously combined file to avoid repetition of sheets.


def combine_subsheets(name):

    # name of the final csv file
    now = datetime.now()
    dt_string = now.strftime("%m-%d-%HH%MM")
    comb_filename = name + "-" + dt_string + ".xlsx"


    # load the files
    xlsx_files = glob.glob('*.xls')
    xlsx_files.extend(glob.glob('*.xlsx'))
    csv_files = glob.glob('*.csv')

    writer = pd.ExcelWriter(comb_filename, engine='xlsxwriter')

    # add all excel files in seperate sheets
    for f in xlsx_files:

        df = pd.read_excel(io = f, sheet_name = None)
        file_name = os.path.splitext(f)[0].split('\\')[-1]
        len_df = len(df)
        for value in df.values():
            if len(value) == 0:
                len_df -= 1

        if name not in file_name:
            for key,value in df.items():
                if len(value) != 0:
                    if (len_df == 1) and ('Sheet' in key):
                        sheet_name = file_name.upper()
                    else:
                        sheet_name = (file_name + '_' + key).upper()
                    value.to_excel(writer, sheet_name = sheet_name, index=False)

    # add all csv files in seperate sheets
    for f in csv_files:
        file_name = (os.path.splitext(f)[0].split('\\')[-1]).upper()
        df = pd.read_csv(f)
        df.to_excel(writer, sheet_name=file_name, index=False)

    writer.save()

    # sorting the sheets in ascending order
    df_comb = pd.read_excel(io=comb_filename, sheet_name=None)
    writer1 = pd.ExcelWriter(comb_filename, engine='xlsxwriter')
    for key in sorted(df_comb.keys()):
        value = df_comb[key]
        value.to_excel(writer1, sheet_name=key, index=False)
    writer1.save()

try:
    name = sys.argv[1]       # Add this line in the main code before calling the generate_subsheets(name) function
    combine_subsheets(name)

except:
    print('''
    Pass the name, that the final combined excel sheet will have, as an argument while running the code. 
    Timestamp will be added to this name.
    It will combine all the csv,xls,xlsx files present in the working directory. 
    It ignores all those files that have same base name as the argument that is passed''')
    pass




