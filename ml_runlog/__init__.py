from numpy import e
from .main import *
import pygsheets
import os
import pandas as pd

creds_path = None
sheet_name = None
worksheet_idx = -1
gc = None
worksheet = None
sno = None
sno_logged = False

def init(creds_path_, sheet_name_, worksheet_idx_=0, log_heartbeat=True):
    global creds_path
    global sheet_name
    global worksheet_idx
    global gc
    global sheet
    global sno
    global worksheet 
    global column_idx

    creds_path = creds_path_
    sheet_name = sheet_name_
    worksheet_idx = worksheet_idx_

    gc = pygsheets.authorize(service_file=creds_path) 
    sheet = gc.open(sheet_name)
    worksheet = sheet[worksheet_idx]
    sno = get_sno(worksheet)
    column_idx = 2 # 0th column is for logging heartbeat

    if log_heartbeat:
        if os.fork() > 0:
            # Parent process
            return 
        else:
            monitor_health(worksheet, sno)

def log_data(offset=0, increment_cols=True, **kwargs):
    global sno 
    global column_idx
    global worksheet 
    global sno_logged

    if not sno_logged:
        sno_logged = True
        assert('sno' not in kwargs.keys())
        kwargs['sno'] = [sno]
        df = pd.DataFrame(kwargs)
        df = reorder_cols(df)
    else:
        first_key = list(kwargs.keys())[0]
        kwargs[first_key] = [kwargs[first_key]]
        df = pd.DataFrame(kwargs)

    if os.fork() == 0:
        try:
            # Do this in a separate process to prevent blocking
            worksheet.set_dataframe(df, (sno + 1, column_idx + offset), copy_head=False)
        except e:
            print(e)

        exit() 

    if increment_cols:
        column_idx += len(kwargs) + offset