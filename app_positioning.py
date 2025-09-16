### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- POSITIONING ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
from plotly.subplots import make_subplots
DATA_DIR = os.getenv('DATA_DIR', 'data')

### FUNCTIONS ###
def merge_dfs(array_of_dfs):
    new_df = ft.reduce(lambda left,
                              right: pd.merge(left,
                                                    right,
                                                    left_index=True,
                                                    right_index=True,
                                                    how='outer'), array_of_dfs)
    return(new_df)

def rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    rolling_mean = series.rolling(window=window, min_periods=window).mean()
    rolling_std = series.rolling(window=window, min_periods=window).std()
    return (series - rolling_mean) / rolling_std
def rolling_corr(series1: pd.Series, series2: pd.Series, window: int) -> pd.Series:
    return series1.rolling(window=window, min_periods=window).corr(series2)
def rolling_corr_matrix(df: pd.DataFrame, window: int) -> dict:
    result = {}
    cols = df.columns
    for i, col1 in enumerate(cols):
        for col2 in cols[i+1:]:
            name = f"{col1}_vs_{col2}"
            result[name] = df[col1].rolling(window=window, min_periods=window).corr(df[col2])
    return result


### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ FED FUNDS ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fedfunds_futures_positions(start,end,**kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)
    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'FED FUNDS']
    contract_size = 5000000
    cot_positions = future_contract_df[[
        'dealer_positions_long_all',
        'dealer_positions_short_all',
        'asset_mgr_positions_long',
        'asset_mgr_positions_short',
        'lev_money_positions_long',
        'lev_money_positions_short',
        'tot_rept_positions_long_all',
        'tot_rept_positions_short',
    ]].sort_index()
    cot_positions.columns = ['dealer_long','dealer_short',
                             'asset_mgr_long','asset_mgr_short',
                             'lev_long','lev_short',
                             'total_long','total_short']
    cot_positions = cot_positions * contract_size
    cot_positions['dealer_gross'] = cot_positions['dealer_long'] + cot_positions['dealer_short']
    cot_positions['asset_mgr_gross'] = cot_positions['asset_mgr_long'] + cot_positions['asset_mgr_short']
    cot_positions['lev_gross'] = cot_positions['lev_long'] + cot_positions['lev_short']
    cot_positions['total_gross'] = cot_positions['total_long'] + cot_positions['total_short']
    cot_positions['dealer_net'] = cot_positions['dealer_long'] - cot_positions['dealer_short']
    cot_positions['asset_mgr_net'] = cot_positions['asset_mgr_long'] - cot_positions['asset_mgr_short']
    cot_positions['lev_net'] = cot_positions['lev_long'] - cot_positions['lev_short']
    cot_positions['total_net'] = cot_positions['total_long'] - cot_positions['total_short']
    cot_positions = cot_positions[start:end]
    cot_positions_diff = cot_positions.diff(1).dropna()
    cot_positions_diff = cot_positions_diff[start:end]

    ### PLOT ###
    fig = go.Figure()
    cols = [
        'dealer_long', 'asset_mgr_long','lev_long',
        'dealer_short', 'asset_mgr_short', 'lev_short',
        'dealer_net', 'asset_mgr_net', 'lev_net',
        'dealer_gross', 'asset_mgr_gross', 'lev_gross'
    ]
    labels = [
        'Dealer Long',
        'Asset Managers Long',
        'Leveraged Funds Long',
        'Dealer Short',
        'Asset Managers Short',
        'Leveraged Funds Short',
        'Dealer Net',
        'Asset Managers Net',
        'Leveraged Funds Net',
        'Dealer Gross',
        'Asset Managers Gross',
        'Leveraged Funds Gross'
    ]
    colors = ['#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145'
              ]
    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=cot_positions.index,
                y=cot_positions[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Weekly Positions",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=cot_positions_diff.index,
                y=cot_positions_diff[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Weekly Change",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- SOFR 1M ------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr1m_futures_positions(start,end,**kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)
    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'SOFR-1M']
    contract_size = 5000000
    cot_positions = future_contract_df[[
        'dealer_positions_long_all',
        'dealer_positions_short_all',
        'asset_mgr_positions_long',
        'asset_mgr_positions_short',
        'lev_money_positions_long',
        'lev_money_positions_short',
        'tot_rept_positions_long_all',
        'tot_rept_positions_short',
    ]].sort_index()
    cot_positions.columns = ['dealer_long','dealer_short',
                             'asset_mgr_long','asset_mgr_short',
                             'lev_long','lev_short',
                             'total_long','total_short']
    cot_positions = cot_positions * contract_size
    cot_positions['dealer_gross'] = cot_positions['dealer_long'] + cot_positions['dealer_short']
    cot_positions['asset_mgr_gross'] = cot_positions['asset_mgr_long'] + cot_positions['asset_mgr_short']
    cot_positions['lev_gross'] = cot_positions['lev_long'] + cot_positions['lev_short']
    cot_positions['total_gross'] = cot_positions['total_long'] + cot_positions['total_short']
    cot_positions['dealer_net'] = cot_positions['dealer_long'] - cot_positions['dealer_short']
    cot_positions['asset_mgr_net'] = cot_positions['asset_mgr_long'] - cot_positions['asset_mgr_short']
    cot_positions['lev_net'] = cot_positions['lev_long'] - cot_positions['lev_short']
    cot_positions['total_net'] = cot_positions['total_long'] - cot_positions['total_short']
    cot_positions = cot_positions[start:end]
    cot_positions_diff = cot_positions.diff(1).dropna()
    cot_positions_diff = cot_positions_diff[start:end]

    ### PLOT ###
    fig = go.Figure()
    cols = [
        'dealer_long', 'asset_mgr_long','lev_long',
        'dealer_short', 'asset_mgr_short', 'lev_short',
        'dealer_net', 'asset_mgr_net', 'lev_net',
        'dealer_gross', 'asset_mgr_gross', 'lev_gross'
    ]
    labels = [
        'Dealer Long',
        'Asset Managers Long',
        'Leveraged Funds Long',
        'Dealer Short',
        'Asset Managers Short',
        'Leveraged Funds Short',
        'Dealer Net',
        'Asset Managers Net',
        'Leveraged Funds Net',
        'Dealer Gross',
        'Asset Managers Gross',
        'Leveraged Funds Gross'
    ]
    colors = ['#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145'
              ]
    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=cot_positions.index,
                y=cot_positions[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Weekly Positions",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=cot_positions_diff.index,
                y=cot_positions_diff[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Weekly Change",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- SOFR 3M ------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr3m_futures_positions(start,end,**kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)
    contract_imm_idx = sofr
    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'SOFR-3M']
    future_contract_df['contract_units']
    future_contract_df.columns
    contract_size = 2500
    cot_positions = future_contract_df[[
        'dealer_positions_long_all',
        'dealer_positions_short_all',
        'asset_mgr_positions_long',
        'asset_mgr_positions_short',
        'lev_money_positions_long',
        'lev_money_positions_short',
        'tot_rept_positions_long_all',
        'tot_rept_positions_short',
    ]].sort_index()
    cot_positions.columns = ['dealer_long','dealer_short',
                             'asset_mgr_long','asset_mgr_short',
                             'lev_long','lev_short',
                             'total_long','total_short']
    cot_positions = cot_positions * contract_size
    cot_positions['dealer_gross'] = cot_positions['dealer_long'] + cot_positions['dealer_short']
    cot_positions['asset_mgr_gross'] = cot_positions['asset_mgr_long'] + cot_positions['asset_mgr_short']
    cot_positions['lev_gross'] = cot_positions['lev_long'] + cot_positions['lev_short']
    cot_positions['total_gross'] = cot_positions['total_long'] + cot_positions['total_short']
    cot_positions['dealer_net'] = cot_positions['dealer_long'] - cot_positions['dealer_short']
    cot_positions['asset_mgr_net'] = cot_positions['asset_mgr_long'] - cot_positions['asset_mgr_short']
    cot_positions['lev_net'] = cot_positions['lev_long'] - cot_positions['lev_short']
    cot_positions['total_net'] = cot_positions['total_long'] - cot_positions['total_short']
    cot_positions = cot_positions[start:end]
    cot_positions_diff = cot_positions.diff(1).dropna()
    cot_positions_diff = cot_positions_diff[start:end]

    ### PLOT ###
    fig = go.Figure()
    cols = [
        'dealer_long', 'asset_mgr_long','lev_long',
        'dealer_short', 'asset_mgr_short', 'lev_short',
        'dealer_net', 'asset_mgr_net', 'lev_net',
        'dealer_gross', 'asset_mgr_gross', 'lev_gross'
    ]
    labels = [
        'Dealer Long',
        'Asset Managers Long',
        'Leveraged Funds Long',
        'Dealer Short',
        'Asset Managers Short',
        'Leveraged Funds Short',
        'Dealer Net',
        'Asset Managers Net',
        'Leveraged Funds Net',
        'Dealer Gross',
        'Asset Managers Gross',
        'Leveraged Funds Gross'
    ]
    colors = ['#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145'
              ]
    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=cot_positions.index,
                y=cot_positions[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Weekly Positions",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=cot_positions_diff.index,
                y=cot_positions_diff[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Weekly Change",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- SOFR 3M ------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def correlation_with_sofr(start,end,**kwargs):
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)

    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'FED FUNDS']
    contract_size = 5000000
    cot_positions = future_contract_df[[
        'dealer_positions_long_all',
        'dealer_positions_short_all',
        'asset_mgr_positions_long',
        'asset_mgr_positions_short',
        'lev_money_positions_long',
        'lev_money_positions_short',
        'tot_rept_positions_long_all',
        'tot_rept_positions_short',
    ]].sort_index()
    cot_positions.columns = ['dealer_long','dealer_short',
                             'asset_mgr_long','asset_mgr_short',
                             'lev_long','lev_short',
                             'total_long','total_short']
    cot_positions = cot_positions * contract_size
    cot_positions['dealer_gross'] = cot_positions['dealer_long'] + cot_positions['dealer_short']
    cot_positions['asset_mgr_gross'] = cot_positions['asset_mgr_long'] + cot_positions['asset_mgr_short']
    cot_positions['lev_gross'] = cot_positions['lev_long'] + cot_positions['lev_short']
    cot_positions['total_gross'] = cot_positions['total_long'] + cot_positions['total_short']
    cot_positions['dealer_net'] = cot_positions['dealer_long'] - cot_positions['dealer_short']
    cot_positions['asset_mgr_net'] = cot_positions['asset_mgr_long'] - cot_positions['asset_mgr_short']
    cot_positions['lev_net'] = cot_positions['lev_long'] - cot_positions['lev_short']
    cot_positions['total_net'] = cot_positions['total_long'] - cot_positions['total_short']
    cot_positions_diff = cot_positions.diff(1).dropna()

    tri_merge_df = merge_dfs([
        rolling_zscore(cot_positions_diff,52),tri_df]).dropna()
    tri_merge_df['value'] = tri_merge_df['value'].diff(1).shift(-1)
    gcf_merge_df = merge_dfs([
        rolling_zscore(cot_positions_diff, 52), gcf_df]).dropna()
    gcf_merge_df['value'] = gcf_merge_df['value'].diff(1).shift(-1)
    dvp_merge_df = merge_dfs([
        rolling_zscore(cot_positions_diff, 52), dvp_df]).dropna()
    dvp_merge_df['value'] = dvp_merge_df['value'].diff(1).shift(-1)
    sofr_merge_df = merge_dfs([
        rolling_zscore(cot_positions_diff, 52), sofr]).dropna()
    sofr_merge_df['SOFR'] = sofr_merge_df['SOFR'].diff(1).shift(-1)

    tri_corr_dict = {}
    dvp_corr_dict = {}
    gcf_corr_dict = {}
    sofr_corr_dict = {}
    for col in tri_merge_df.columns:
        tri_corr_dict[col] = rolling_corr(tri_merge_df[col],tri_merge_df['value'],52)
        dvp_corr_dict[col] = rolling_corr(dvp_merge_df[col],dvp_merge_df['value'],52)
        gcf_corr_dict[col] = rolling_corr(gcf_merge_df[col],gcf_merge_df['value'],52)
    for col in sofr_merge_df.columns:
        sofr_corr_dict[col] = rolling_corr(sofr_merge_df[col],sofr_merge_df['SOFR'],52)

    tri_corr_df = pd.DataFrame(tri_corr_dict)
    tri_corr_df = tri_corr_df.drop('value',axis=1)
    tri_corr_df = tri_corr_df[start:end]
    dvp_corr_dict = pd.DataFrame(dvp_corr_dict)
    dvp_corr_dict = dvp_corr_dict.drop('value',axis=1)
    dvp_corr_dict = dvp_corr_dict[start:end]
    gcf_corr_dict = pd.DataFrame(gcf_corr_dict)
    gcf_corr_dict = gcf_corr_dict.drop('value',axis=1)
    gcf_corr_dict = gcf_corr_dict[start:end]
    sofr_corr_dict = pd.DataFrame(sofr_corr_dict)
    sofr_corr_dict = sofr_corr_dict.drop('SOFR',axis=1)
    sofr_corr_dict = sofr_corr_dict[start:end]

    ### PLOT ###
    fig = go.Figure()
    cols = [
        'dealer_long', 'asset_mgr_long', 'lev_long',
        'dealer_short', 'asset_mgr_short', 'lev_short',
        'dealer_net', 'asset_mgr_net', 'lev_net',
        'dealer_gross', 'asset_mgr_gross', 'lev_gross'
    ]
    labels = [
        'Dealer Long',
        'Asset Managers Long',
        'Leveraged Funds Long',
        'Dealer Short',
        'Asset Managers Short',
        'Leveraged Funds Short',
        'Dealer Net',
        'Asset Managers Net',
        'Leveraged Funds Net',
        'Dealer Gross',
        'Asset Managers Gross',
        'Leveraged Funds Gross'
    ]
    colors = ['#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145',
              '#FF7B7B',
              '#4FC3F7',
              '#FFC145'
              ]
    fig = make_subplots(rows=4, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=sofr_corr_dict.index,
                y=sofr_corr_dict[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="SOFR Rolling Correlation",
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)





