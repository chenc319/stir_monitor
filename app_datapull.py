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
    with open(Path(DATA_DIR) / 'iorb.pkl', 'wb') as file:
        pickle.dump(iorb, file)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'wb') as file:
        pickle.dump(fed_funds, file)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'wb') as file:
        pickle.dump(sofr, file)
    sofr_1m_avg = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr_1m_avg.pkl', 'wb') as file:
        pickle.dump(sofr_1m_avg, file)
    sofr_3m_avg = pdr.DataReader('SOFR90DAYAVG', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr_3m_avg.pkl', 'wb') as file:
        pickle.dump(sofr_3m_avg, file)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    with open(Path(DATA_DIR) / 'rrp.pkl', 'wb') as file:
        pickle.dump(rrp, file)
    def ofr_to_df(mnemonic):
        base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')
    dvp_df = ofr_to_df('REPO-DVP_AR_OO-P')
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'wb') as file:
        pickle.dump(dvp_df, file)
    gcf_df = ofr_to_df('REPO-GCF_AR_AG-P')
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'wb') as file:
        pickle.dump(gcf_df, file)
    tri_df = ofr_to_df('REPO-TRI_AR_OO-P')
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'wb') as file:
        pickle.dump(tri_df, file)
    sofr1 = pdr.DataReader('SOFR1', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr1.pkl', 'wb') as file:
        pickle.dump(sofr1, file)
    sofr25 = pdr.DataReader('SOFR25', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr25.pkl', 'wb') as file:
        pickle.dump(sofr25, file)
    sofr75 = pdr.DataReader('SOFR75', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr75.pkl', 'wb') as file:
        pickle.dump(sofr75, file)
    sofr99 = pdr.DataReader('SOFR99', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr99.pkl', 'wb') as file:
        pickle.dump(sofr99, file)

    ### VOLUME ###
    treasury = pdr.DataReader('TREAST', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'treasury.pkl', 'wb') as file:
        pickle.dump(treasury, file)
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'mbs.pkl', 'wb') as file:
        pickle.dump(mbs, file)
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) * 1e9
    with open(Path(DATA_DIR) / 'reserves.pkl', 'wb') as file:
        pickle.dump(reserves, file)
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) * 1e9
    with open(Path(DATA_DIR) / 'tga.pkl', 'wb') as file:
        pickle.dump(tga, file)
    rrp_on_volume = pdr.DataReader('RRPONTSYD', 'fred', start, end) * 1e9
    with open(Path(DATA_DIR) / 'rrp_on_volume.pkl', 'wb') as file:
        pickle.dump(rrp_on_volume, file)
    rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'wb') as file:
        pickle.dump(rrp_volume, file)
    tri_volume_df = ofr_to_df('REPO-TRI_TV_TOT-P')
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'wb') as file:
        pickle.dump(tri_volume_df, file)
    fed_action = pdr.DataReader('WALCL', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'fed_action.pkl', 'wb') as file:
        pickle.dump(fed_action, file)












