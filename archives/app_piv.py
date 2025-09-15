### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- PRIVATE INVESTMENT FUNDS ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pandas_datareader import data as pdr
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', '../data')

### FUNCTIONS ###
def merge_dfs(array_of_dfs):
    new_df = ft.reduce(lambda left,
                              right: pd.merge(left,
                                                    right,
                                                    left_index=True,
                                                    right_index=True,
                                                    how='outer'), array_of_dfs)
    return(new_df)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- PRIVATE INVESTMENT FUNDS ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_private_investments(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)

    fed_funds_futures = cftc_all_futures[
        cftc_all_futures['contract_market_name'] == 'FED FUNDS']
    fed_funds_futures = fed_funds_futures.sort_index()
    sofr3m_futures = cftc_all_futures[
        cftc_all_futures['contract_market_name'] == 'SOFR-3M']
    sofr3m_futures = sofr3m_futures.sort_index()
    sofr1m_futures = cftc_all_futures[
        cftc_all_futures['contract_market_name'] == 'SOFR-1M']
    sofr1m_futures = sofr1m_futures.sort_index()

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(fed_funds_futures.index,
    #          fed_funds_futures['lev_money_positions_long'],
    #          color='#9DDCF9', lw=2)
    # plt.plot(sofr3m_futures.index,
    #          sofr3m_futures['lev_money_positions_long'],
    #          color='#4CD0E9', lw=2)
    # plt.plot(sofr1m_futures.index,
    #          sofr1m_futures['lev_money_positions_long'],
    #          color='#233852', lw=2)
    # plt.ylabel("$ (Trillions)")
    # plt.title("MMF's Investments in Overnight/Open Repo", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    long_merge_df = merge_dfs([fed_funds_futures['lev_money_positions_long']*5000000,
                               sofr3m_futures['lev_money_positions_long']*2500,
                               sofr1m_futures['lev_money_positions_long']*4167]).dropna()
    long_merge_df.columns = ['fedfunds', 'sofr3m', 'sofr1m']
    long_merge_df = long_merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=long_merge_df.index,
                             y=long_merge_df['fedfunds'],
                             mode='lines+markers',
                             name='Fed Funds',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="Private Investments Long Positions - Fed Funds",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    short_merge_df = merge_dfs([fed_funds_futures['lev_money_positions_short']*5000000,
                                sofr3m_futures['lev_money_positions_short']*2500,
                                sofr1m_futures['lev_money_positions_short']*4167]).dropna()
    short_merge_df.columns = ['fedfunds', 'sofr3m', 'sofr1m']
    short_merge_df = short_merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=short_merge_df.index,
                             y=short_merge_df['fedfunds'],
                             mode='lines+markers',
                             name='Fed Funds',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="Private Investments Short Positions - Fed Funds",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    net_merge_df = long_merge_df - short_merge_df
    net_merge_df = net_merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=net_merge_df.index,
                             y=net_merge_df['fedfunds'],
                             mode='lines+markers',
                             name='Fed Funds',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="Private Investments Net Positions - Fed Funds",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=long_merge_df.index,
                             y=long_merge_df['sofr1m'],
                             mode='lines+markers',
                             name='SOFR 1M',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=long_merge_df.index,
                             y=long_merge_df['sofr3m'],
                             mode='lines+markers',
                             name='SOFR 3M',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="Private Investments Long Positions - SOFR",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=short_merge_df.index,
                             y=short_merge_df['sofr1m'],
                             mode='lines+markers',
                             name='SOFR 1M',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=short_merge_df.index,
                             y=short_merge_df['sofr3m'],
                             mode='lines+markers',
                             name='SOFR 3M',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="Private Investments Short Positions - SOFR",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=net_merge_df.index,
                             y=net_merge_df['sofr1m'],
                             mode='lines+markers',
                             name='SOFR 1M',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=net_merge_df.index,
                             y=net_merge_df['sofr3m'],
                             mode='lines+markers',
                             name='SOFR 3M',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="Private Investments Net Positions - SOFR",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)