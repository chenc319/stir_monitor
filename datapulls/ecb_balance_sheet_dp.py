### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- FED BALANCE SHEET DATA PULL --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
from Functions import *
from pathlib import Path
import os
DATA_DIR = os.getenv('DATA_DIR', '../data')

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ ALL ARE WEDNESDAY LEVELS NOT WEEKLY AVERAGES ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### ASSETS ###
start = '1990-01-01'
end = pd.to_datetime('today')

import io
import requests
import pandas as pd

def ecb_get(flow, key, params=None):
    url = f"https://data-api.ecb.europa.eu/service/data/{flow}/{key}"
    headers = {"Accept": "text/csv"}
    r = requests.get(url, params=params or {}, headers=headers, timeout=30)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

# Example: one known series
df = ecb_get(
    flow="EXR",
    key="M.USD.EUR.SP00.A",
    params={"startPeriod": "2020-01"}
)