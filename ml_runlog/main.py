import pygsheets
import pandas as pd 
import time

class MLRunlog: 
    def __init__(self, creds_path_, sheet_name_, worksheet_idx_=0):
        self.creds_path = creds_path_
        self.sheet_name = sheet_name_
        self.worksheet_idx = worksheet_idx_
        self.gc = pygsheets.authorize(service_file=creds_path_) 

    def _parse_numeric_sno(self, value):
        if value is None:
            return None

        value_str = str(value).strip()
        if value_str == "":
            return None

        try:
            return int(value_str)
        except (TypeError, ValueError):
            pass

        try:
            value_float = float(value_str)
        except (TypeError, ValueError):
            return None

        if value_float.is_integer():
            return int(value_float)

        return None

    def _find_sno_column(self, df):
        for col in df.columns:
            if str(col).strip().lower() == "sno":
                return col
        return None

    def _require_sno_column(self, df):
        sno_col = self._find_sno_column(df)
        assert sno_col is not None, "Missing required 'sno' header in sheet"
        return sno_col

    def _build_sno_row_map(self, df):
        sno_col = self._require_sno_column(df)

        sno_row_map = {}
        for idx, value in enumerate(df[sno_col].tolist()):
            parsed_sno = self._parse_numeric_sno(value)
            if parsed_sno is None:
                continue
            if parsed_sno in sno_row_map:
                continue
            # +2 because dataframe row 0 maps to sheet row 2 (row 1 is header).
            sno_row_map[parsed_sno] = idx + 2

        return sno_row_map

    def get_sno(self):
        sheet = self.gc.open(self.sheet_name)
        worksheet = sheet[self.worksheet_idx]
        df = worksheet.get_as_df()
        sno_col = self._require_sno_column(df)

        parsed_snos = []
        for value in df[sno_col].tolist():
            parsed_sno = self._parse_numeric_sno(value)
            if parsed_sno is not None:
                parsed_snos.append(parsed_sno)

        return (max(parsed_snos) + 1) if parsed_snos else 1

    def allocate_sno(self, n, sno=None):
        if n <= 0:
            return []

        sheet = self.gc.open(self.sheet_name)
        worksheet = sheet[self.worksheet_idx]
        df = worksheet.get_as_df()

        if sno is None:
            start_sno = self.get_sno()
        else:
            start_sno = int(sno)

        reserved_rows = [{"sno": start_sno + i} for i in range(n)]
        reserved_df = pd.DataFrame(reserved_rows)
        reserved_df = self.move_sno_to_left(reserved_df)

        # Reserve rows at the end of current sheet data.
        worksheet.set_dataframe(reserved_df.copy(), (len(df) + 2, 1), copy_head=False)

        return list(range(start_sno, start_sno + n))


    def log_data(self, data_list=[], verify_timeout=None, sno=None, verify_col_idx=None):
        """
        verify_col_idx: index of the column to verify the data. This is 0 indexed. The data in this column should ideally be unique and a string
        """

        if len(data_list) == 0:
            return

        sheet = self.gc.open(self.sheet_name)
        worksheet = sheet[self.worksheet_idx]
        df = worksheet.get_as_df()

        if sno is None:
            sno_col = self._find_sno_column(df)
            if sno_col is None:
                sno = 1
            else:
                parsed_snos = [self._parse_numeric_sno(v) for v in df[sno_col].tolist()]
                parsed_snos = [s for s in parsed_snos if s is not None]
                sno = (max(parsed_snos) + 1) if parsed_snos else 1
        else:
            sno = int(sno)

        for i, row in enumerate(data_list):
            row['sno'] = sno + i

        # convert list of dicts to dataframe
        data_df = pd.DataFrame(data_list)
        data_df = self.move_sno_to_left(data_df)

        sno_row_map = self._build_sno_row_map(df)
        next_append_row = len(df) + 2
        write_rows = []

        for i in range(len(data_df)):
            row_sno = int(data_df.iloc[i, 0])
            write_row = sno_row_map.get(row_sno)
            if write_row is None:
                write_row = next_append_row
                next_append_row += 1
                sno_row_map[row_sno] = write_row
            write_rows.append(write_row)

        # Write all rows in a single API call if they target contiguous sheet rows,
        # otherwise fall back to per-row writes.
        if write_rows == list(range(write_rows[0], write_rows[0] + len(write_rows))):
            worksheet.set_dataframe(data_df.copy(), (write_rows[0], 1), copy_head=False)
        else:
            for i, write_row in enumerate(write_rows):
                worksheet.set_dataframe(data_df.iloc[[i]].copy(), (write_row, 1), copy_head=False)

        if verify_timeout:
            start_time = time.time()
            while time.time() - start_time < verify_timeout:
                cell_value = worksheet.cell((write_rows[0], verify_col_idx + 2)).value
                expected_value = data_df.iloc[0, verify_col_idx + 1] # df is zero-indexed but the first column is sno so we do +1

                if cell_value == expected_value:
                    print("Data logged successfully")
                    return
                print("Data not found, retrying")
                time.sleep(1)
            raise Exception("Data not found after timeout")
        
    def get_data_at_cell(self, row, col):
        worksheet = self.gc.open(self.sheet_name)[self.worksheet_idx]
        df = worksheet.get_as_df()
        sno_row_map = self._build_sno_row_map(df)
        sheet_row = sno_row_map.get(int(row))
        if sheet_row is None:
            return None

        # verify_col_idx is 0 indexed but sheet columns are 1 indexed; +1 for 1-indexing and +1 for the sno column.
        return worksheet.cell((sheet_row, col + 2)).value

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
