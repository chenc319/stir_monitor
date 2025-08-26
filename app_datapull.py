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
    with open(base_path + 'iorb.pkl', 'wb') as file:
        pickle.dump(iorb, file)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    with open(base_path + 'fed_funds.pkl', 'wb') as file:
        pickle.dump(fed_funds, file)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    with open(base_path + 'sofr.pkl', 'wb') as file:
        pickle.dump(sofr, file)
    sofr_1m_avg = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
    with open(base_path + 'sofr_1m_avg.pkl', 'wb') as file:
        pickle.dump(sofr_1m_avg, file)
    sofr_3m_avg = pdr.DataReader('SOFR90DAYAVG', 'fred', start, end)
    with open(base_path + 'sofr_3m_avg.pkl', 'wb') as file:
        pickle.dump(sofr_3m_avg, file)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    with open(base_path + 'rrp.pkl', 'wb') as file:
        pickle.dump(rrp, file)










