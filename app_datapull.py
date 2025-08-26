### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- REFRESH DATA FUNCTION ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pandas_datareader import data as pdr
from pathlib import Path
import os
import pickle
import ftplib
import io
import pandas as pd
DATA_DIR = os.getenv('DATA_DIR', 'data')
base_path = '/Users/chenc/Documents/GitHub/stir_monitor/data/'

### FUNCTIONS ###

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left,
                                            right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'),
                     array_of_dfs)


def refresh_all_data():
    ### NEW DATES ###
    start = '1990-01-01'
    end = pd.to_datetime('today')

    ### RATES ###
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)

    with open(base_path + 'iorb.pkl', 'wb') as file:
        pickle.dump(iorb, file)

    file_path = Path(DATA_DIR) / 'all_us_comps_latest_sbc_df.pkl'
    with open(file_path, 'rb') as file:
        all_us_comps_latest_sbc_df = pickle.load(file)





