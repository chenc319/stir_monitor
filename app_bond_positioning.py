### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ FUTURES ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
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
### -------------------------------------------------- 2YR --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_2y_bond_pos(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)

    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'UST 2Y NOTE']
    contract_size = 200000
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
    cot_positions.columns = ['dealer_long', 'dealer_short',
                             'asset_mgr_long', 'asset_mgr_short',
                             'lev_long', 'lev_short',
                             'total_long', 'total_short']
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

    colors = ['#2567c4', '#83c3f7', '#e5433a']
    labels = ['Dealer', 'Asset Manager', 'Leveraged Funds']

    ### PLOT ###
    cols = ['dealer_long','asset_mgr_long','lev_long']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="2yr Long Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_short', 'asset_mgr_short', 'lev_short']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="2yr Short Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_net', 'asset_mgr_net', 'lev_net']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="2yr Net Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_gross', 'asset_mgr_gross', 'lev_gross']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="2yr Gross Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- 5YR --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_5y_bond_pos(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)

    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'UST 5Y NOTE']
    contract_size = 100000
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
    cot_positions.columns = ['dealer_long', 'dealer_short',
                             'asset_mgr_long', 'asset_mgr_short',
                             'lev_long', 'lev_short',
                             'total_long', 'total_short']
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

    colors = ['#2567c4', '#83c3f7', '#e5433a']
    labels = ['Dealer', 'Asset Manager', 'Leveraged Funds']

    ### PLOT ###
    cols = ['dealer_long','asset_mgr_long','lev_long']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="5yr Long Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_short', 'asset_mgr_short', 'lev_short']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="5yr Short Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_net', 'asset_mgr_net', 'lev_net']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="5yr Net Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_gross', 'asset_mgr_gross', 'lev_gross']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="5yr Gross Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- 10YR -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_10y_bond_pos(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)

    future_contract_df = cftc_all_futures[cftc_all_futures['contract_market_name'] == 'UST 10Y NOTE']
    contract_size = 100000
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
    cot_positions.columns = ['dealer_long', 'dealer_short',
                             'asset_mgr_long', 'asset_mgr_short',
                             'lev_long', 'lev_short',
                             'total_long', 'total_short']
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

    colors = ['#2567c4', '#83c3f7', '#e5433a']
    labels = ['Dealer', 'Asset Manager', 'Leveraged Funds']

    ### PLOT ###
    cols = ['dealer_long','asset_mgr_long','lev_long']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="10yr Long Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_short', 'asset_mgr_short', 'lev_short']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="10yr Short Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_net', 'asset_mgr_net', 'lev_net']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="10yr Net Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    cols = ['dealer_gross', 'asset_mgr_gross', 'lev_gross']
    fig = go.Figure()
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=cot_positions.index, y=cot_positions[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="10yr Gross Positioning",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)