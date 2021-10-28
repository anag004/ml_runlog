import pygsheets
import pandas as pd
import os

creds_path = os.path.join(os.path.expanduser("~"), "creds.json")
gc = pygsheets.authorize(service_file=creds_path)

# Create empty dataframe
df = pd.DataFrame()

# Create a column
df['name'] = ['John', 'Steve', 'Sarah']

#open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
sh = gc.open('test')

#select the first sheet 
wks = sh[0]

#update the first sheet with df, starting at cell B2. 
wks.set_dataframe(df,(1,1))
