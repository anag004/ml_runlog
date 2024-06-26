import pygsheets
import pandas as pd 
import time

class MLRunlog: 
    def __init__(self, creds_path_, sheet_name_, worksheet_idx_=0):
        self.creds_path = creds_path_
        self.sheet_name = sheet_name_
        self.worksheet_idx = worksheet_idx_
        self.gc = pygsheets.authorize(service_file=creds_path_) 
    
    def get_sno(self):
        sheet = self.gc.open(self.sheet_name)
        worksheet = sheet[self.worksheet_idx]
        return len(worksheet.get_as_df()) + 1

    def allocate_sno(self, n, sno=None):
        if sno is None:
            sno = self.get_sno()
        self.log_data([{} for _ in range(n)], sno=sno)
        return list(range(sno, sno + n))


    def log_data(self, data_list=[], verify_timeout=None, sno=None, verify_col_idx=None):
        """
        verify_col_idx: index of the column to verify the data. This is 0 indexed. The data in this column should ideally be unique and a string
        """

        if len(data_list) == 0:
            return
        
        if sno is None:
            sno = self.get_sno()

        sheet = self.gc.open(self.sheet_name)
        worksheet = sheet[self.worksheet_idx]

        for i, row in enumerate(data_list):
            row['sno'] = sno + i

        # convert list of dicts to dataframe
        data_df = pd.DataFrame(data_list)
        data_df = self.move_sno_to_left(data_df)

        worksheet.set_dataframe(data_df.copy(), (sno + 1, 1), copy_head=False)        

        if verify_timeout:
            start_time = time.time() 
            while time.time() - start_time < verify_timeout:
                cell_value = self.get_data_at_cell(sno, verify_col_idx)
                expected_value = data_df.iloc[0, verify_col_idx + 1] # df is zero-indexed but the first column is sno so we do +1

                if cell_value == expected_value:
                    print("Data logged successfully")
                    return
                print("Data not found, retrying")
                time.sleep(1)   
            raise Exception("Data not found after timeout") 
        
    def get_data_at_cell(self, row, col):
        worksheet = self.gc.open(self.sheet_name)[self.worksheet_idx]
        # sno in the sheets start from 1 and pygsheets assumes the first row (with the header) is 1 since it is 1 indexed       
        # verify_col_idx is 0 indexed but the first column in the sheet is 1 indexed so we do +1
        # first column is sno so we do +1 aga
        return worksheet.cell((row + 1, col + 2)).value

    def move_sno_to_left(self, df):
        cols = df.columns.tolist()
        idx = cols.index('sno')
        del cols[idx]
        cols.insert(0, 'sno')
        df = df[cols] 
        df['sno'] = df['sno'].astype('int64') # this is how pygsheets reads it 

        return df
    
    def clear_sheet(self, retain_header=True):
        sheet = self.gc.open(self.sheet_name)
        worksheet = sheet[self.worksheet_idx]
        if retain_header:   
            worksheet.clear(start='A2', end='ZZ100000')
        else:
            worksheet.clear()


# write integration tests


