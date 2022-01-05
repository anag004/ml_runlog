import pygsheets
import pandas as pd 
import os
import warnings
import psutil
import time

def reorder_cols(df):
    cols = df.columns.tolist()
    idx = cols.index('sno')
    del cols[idx]
    cols.insert(0, 'sno')
    df = df[cols]

    return df

def get_sno(worksheet):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = worksheet.get_as_df()
    
    return len(df) + 1

def monitor_health(worksheet, sno):
    while True:
        parent_pid = os.getppid()

        if parent_pid != 1:
            status = "ALIVE"
        else:
            status = "DEAD"

        status_dict = {"status": [status]}
        df = pd.DataFrame(status_dict)
        worksheet.set_dataframe(df, (sno + 1, 1), copy_head=False)

        if status == "DEAD":
            print("Parent died, terminating ml_runlog")
            exit()

        time.sleep(0.1)
