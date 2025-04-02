# ml_runlog - logging for machine learning experiments

![Version](https://img.shields.io/pypi/v/ml-runlog)

This package is a wrapper around `pygsheets` and uses the google sheets API to automatically log launched runs to a google sheet. 

## Installation

- Follow instructions to make a google cloud console account (non CMU id)
- Use these instructions to make a service account and get a `credentials.json`: https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account
- Make the spreadsheet and share it to the client email in the service account credentials
- Run `pip install ml_runlog` to install the package

## Logging data

To log data, add some code to the beginning of your training script. First, connect to the sheet you want to log to. 

```
runlog = ml_runlog.MLRunlog(
    creds_path, # path to credentials.json file
    sheet_name  # name of the sheet you want to log to
)
```

Data can be logged in the following way 

```
runlog.log_data(
      data_list=[
          {
              "timestamp": datetime.now(),
              "run_name": run_name,
              "run_url": run_url,
              "machine": os.uname().nodename,
              "script_name": sys.argv[0],
              "log_dir": self.log_dir,
              "commit_hash": get_current_commit_hash(),
              "overrides": self.extract_overrides(sys.argv[1:]),
              "task": self.args.task,
              "ig_version": pkg_resources.get_distribution("isaacgym").version,
              "artifact_url": artifact_url,
              "comments": os.getenv("SHEET_LOGGER"),
          }
      ],
      verify_col_idx=1,  # column index used to verify row data was logged correctly (optional) 
      verify_timeout=10, # maximum amount of time for which data logging is retried before returning 
      sno=sno, # specify which row to log to, if ommitted entry is added to the first empty row
      
  )
```

Each run of the script will append a new row to the sheet which can then be moved around as needed. If a row needs to be added at a specified location the `sno` keyword argument can be supplied. 

![example image](./example_image.png)

## Retrieving runs

Runs can be retrieved by serial number as follows. The retrieved data can be used by a script that fetches configs from wandb or runs eval. 

```
worksheet = runlog.gc.open(runlog.sheet_name)[runlog.worksheet_idx]
df = worksheet.get_as_df()
row = df.iloc[idx].tolist()
```
