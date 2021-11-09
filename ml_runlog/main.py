import pygsheets
import pandas as pd 
import os
import warnings

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

    def reorder_cols(self, df):
        cols = df.columns.tolist()
        idx = cols.index('sno')
        del cols[idx]
        cols.insert(0, 'sno')
        df = df[cols]

        return df

    def log_data(self, **kwargs):
        """Data is in the form of kwarg=value"""

        sno = self.get_sno() # Starts from zero
        assert('sno' not in kwargs.keys())
        kwargs['sno'] = [sno]
        df = pd.DataFrame(kwargs)
        df = self.reorder_cols(df)        

        self.worksheet.set_dataframe(df, (sno + 1, 1), copy_head=False)

    def get_sno(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = self.worksheet.get_as_df()
        
        return len(df) + 1

if __name__ == "__main__":
    # This runs a simple demo of the sheetlogger
    # Ensure that the spreadsheet sheetlogger-test is empty
    logger = SheetLogger("/home/anag/creds.json", "sheetlogger-test")
    logger.log_data(run_id="ornate-course",
                    accuracy="98%",
                    training_time="99")
