from helpers import str_to_datetime
import numpy as np
import datetime
import pandas as pd

def windowed_df_to_date_X_y(windowed_dataframe):
  df_as_np = windowed_dataframe.to_numpy()

  dates = df_as_np[:,0]

  middle_matrix = df_as_np[:,1:-1]
  X = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1)) # reshape data for the tf model last value represents univariate forecasting

  Y = df_as_np[:,-1]

  return dates, X.astype(np.float32), Y.astype(np.float32)

def df_to_windowed_df(dataframe, first_date_str, last_date_str, n=3):
  first_date = str_to_datetime(first_date_str)
  last_date  = str_to_datetime(last_date_str)

  target_date = first_date
  
  dates = []
  X, Y = [], []

  last_time = False
  while True:
    df_subset = dataframe.loc[:target_date].tail(n+1)
    
    if len(df_subset) != n+1:
      print(f'Error: Window of size {n} is too large for date {target_date}')
      return

    values = df_subset['Close'].to_numpy()
    x, y = values[:-1], values[-1]

    dates.append(target_date)
    X.append(x)
    Y.append(y)

    next_week = dataframe.loc[target_date:target_date+datetime.timedelta(days=7)]
    next_datetime_str = str(next_week.head(2).tail(1).index.values[0])
    next_date_str = next_datetime_str.split('T')[0]
    year_month_day = next_date_str.split('-')
    year, month, day = year_month_day
    next_date = datetime.datetime(day=int(day), month=int(month), year=int(year))
    
    if last_time:
      break
    
    target_date = next_date

    if target_date == last_date:
      last_time = True
    
  ret_df = pd.DataFrame({})
  ret_df['Target Date'] = dates
  
  X = np.array(X)
  for i in range(0, n):
    X[:, i]
    ret_df[f'Target-{n-i}'] = X[:, i]
  
  ret_df['Target'] = Y

  return ret_df

def prepare_note_duration_data(df, start_idx=0, end_idx=None, samples_per_row=3):
  df['end_time'] = df['start_time'].shift(-1)  # create end_time as next note’s start_time
  df = df.dropna(subset=['end_time'])          # drop last row where end_time would be NaN

  df = df.iloc[start_idx:end_idx].reset_index(drop=True)

  # Ensure we have a duration column
  if "duration" not in df.columns:
    if "start_time" in df.columns and "end_time" in df.columns:
      df["duration"] = df["end_time"] - df["start_time"]
    else:
      raise ValueError("DataFrame must have either 'duration' or both 'start_time' and 'end_time'.")

  rows = []
  for i in range(len(df) - samples_per_row):
    past_durations = df["duration"].iloc[i:i+samples_per_row].tolist()
    past_notes = df["note"].iloc[i:i+samples_per_row].tolist()

    target_duration = df["duration"].iloc[i + samples_per_row]
    target_note = df["note"].iloc[i + samples_per_row]

    row = past_durations + past_notes + [target_duration, target_note]
    rows.append(row)

  duration_cols = [f"duration_{j+1}" for j in range(samples_per_row)]
  note_cols = [f"note_{j+1}" for j in range(samples_per_row)]
  cols = duration_cols + note_cols + ["target_duration", "target_note"]

  return pd.DataFrame(rows, columns=cols)

def prepare_note_duration_data(df, start_idx=0, end_idx=None, samples_per_row=3):
    # Create end_time as the next note's start_time
    df['end_time'] = df['start_time'].shift(-1)
    df = df.dropna(subset=['end_time'])

    # Slice based on start/end index
    df = df.iloc[start_idx:end_idx].reset_index(drop=True)

    # Ensure we have a duration column
    if "duration" not in df.columns:
        if "start_time" in df.columns and "end_time" in df.columns:
            df["duration"] = df["end_time"] - df["start_time"]
        else:
            raise ValueError("DataFrame must have either 'duration' or both 'start_time' and 'end_time'.")

    rows = []
    for i in range(len(df) - samples_per_row):
        start_time = df["start_time"].iloc[i]  # keep start time of first note in window
        past_durations = df["duration"].iloc[i:i+samples_per_row].tolist()
        past_notes = df["note"].iloc[i:i+samples_per_row].tolist()

        target_duration = df["duration"].iloc[i + samples_per_row]
        target_note = df["note"].iloc[i + samples_per_row]

        row = [start_time] + past_durations + past_notes + [target_duration, target_note]
        rows.append(row)

    # Column names
    duration_cols = [f"duration_{j+1}" for j in range(samples_per_row)]
    note_cols = [f"note_{j+1}" for j in range(samples_per_row)]
    cols = ["start_time"] + duration_cols + note_cols + ["target_duration", "target_note"]

    return pd.DataFrame(rows, columns=cols)
