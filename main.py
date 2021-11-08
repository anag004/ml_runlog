import pygsheets
import pandas as pd 
import os
import ipdb

class SheetLogger:
    """
    Log runs to a sheet, the sheet can have several headers  
    The leftmost column must be 'sno' 
    """

    def __init__(self, creds_path, sheet_name, worksheet_idx=0) -> None:
        self.creds_path = creds_path
        self.sheet_name = sheet_name
        self.worksheet_idx = worksheet_idx
        self.gc = pygsheets.authorize(service_file=self.creds_path)
        self.sheet = self.gc.open(self.sheet_name)
        self.worksheet = self.sheet[worksheet_idx]

    def log_data(self, **kwargs):
        """Data is in the form of kwarg=value"""

        sno = self.get_sno() # Starts from zero
        assert('sno' not in kwargs.keys())
        kwargs['sno'] = sno
        df = pd.DataFrame(kwargs)
        self.sheet.set_dataframe(df, (sno + 1, 1), copy_head=False)

    def get_sno(self):
        df = self.sheet.get_as_df()
        return df.iloc[-1, 0] + 1