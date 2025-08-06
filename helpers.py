from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime

def html_get_df(filename):
  # Load the HTML file
  with open(filename, "r", encoding="utf-8") as file:
      soup = BeautifulSoup(file, "lxml")

  # Find all rows in the table
  rows = soup.find_all("tr", class_="yf-1jecxey")

  # Parse each row
  data = []
  for row in rows:
      cells = row.find_all("td")
      if len(cells) == 7:
          data.append([
              cells[0].text.strip(),  # Date
              float(cells[1].text.strip()),  # Open
              float(cells[2].text.strip()),  # High
              float(cells[3].text.strip()),  # Low
              float(cells[4].text.strip()),  # Close
              float(cells[5].text.strip()),  # Adj Close
              int(cells[6].text.strip().replace(",", ""))  # Volume
          ])

  # Convert to DataFrame
  columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
  df = pd.DataFrame(data, columns=columns)

  # Convert Date to datetime
  df['Date'] = pd.to_datetime(df['Date'])

  # Sort by Date
  df = df.sort_values(by='Date')

  return df

def str_to_datetime(s):
  split = s.split('-')
  year, month, day = int(split[0]), int(split[1]), int(split[2])
  return datetime.datetime(year=year, month=month, day=day)

