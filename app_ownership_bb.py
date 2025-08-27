### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ BUYBACKS ------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- BUYBACK VOLUME BY MATURITY --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_buyback_volume_by_maturity(start,end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        auction_df = pickle.load(file)
        auction_df.columns

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ TOTAL BUYBACK VOLUME ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_treasury_ownership(start,end, **kwargs):
    with open(Path(DATA_DIR) / 'us_treasury_ownership.pkl', 'rb') as file:
        us_treasury_ownership = pickle.load(file)
    all_types_of_owners = us_treasury_ownership['securities_owner'].unique()
    us_treasury_ownership_timeseries = pd.DataFrame()
    for entity in all_types_of_owners:
        entity_df = pd.DataFrame(us_treasury_ownership[
            us_treasury_ownership['securities_owner'] == entity]['securities_bil_amt'])
        entity_df.columns = [entity]
        us_treasury_ownership_timeseries = merge_dfs([us_treasury_ownership_timeseries,entity_df])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['U.S. Savings Bonds'],
                             name='U.S. Savings Bonds',
                             line=dict(color='#90B4E6', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Total Public Debt'],
                             name='Total Public Debt',
                             line=dict(color='#B7D2C9', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Total Privately Held'],
                             name='Total Privately Held',
                             line=dict(color='#F0CBC9', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['State And Local Governments'],
                             name='State And Local Governments',
                             line=dict(color='#F9ECA6', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Pension Funds - State And Local Governments'],
                             name='Pension Funds - State And Local Governments',
                             line=dict(color='#C3C9E6', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Pension Funds - Private'],
                             name='Pension Funds - Private',
                             line=dict(color='#E6C3CA', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Other Investors'],
                             name='Other Investors',
                             line=dict(color='#A6EDD4', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Mutual Funds'],
                             name='Mutual Funds',
                             line=dict(color='#E6D6C3', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Insurance Companies'],
                             name='Insurance Companies',
                             line=dict(color='#A6CEF9', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Foreign And International'],
                             name='Foreign And International',
                             line=dict(color='#E6E6E6', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Federal Reserve And Government Accounts'],
                             name='Federal Reserve And Government Accounts',
                             line=dict(color='#C3E6E6', width=2)))
    fig.add_trace(go.Scatter(x=us_treasury_ownership_timeseries.index,
                             y=us_treasury_ownership_timeseries['Depository Institutions'],
                             name='Depository Institutions',
                             line=dict(color='#D6C3E6', width=2)))
    fig.update_layout(
        title="US Treasury Ownership Estimates",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

