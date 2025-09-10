### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- FED BALANCE SHEET -------------------------------------------- ###
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
from plotly.subplots import make_subplots
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- LIABILITIES ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_balance_sheet_liabilities(start, end, **kwargs):
    ### LIABILITIES ###
    with open(Path(DATA_DIR) / 'fed_liabilities_currency.pkl', 'rb') as file:
        fed_liabilities_currency = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_foreign_repo.pkl', 'rb') as file:
        fed_liabilities_foreign_repo = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_rrp.pkl', 'rb') as file:
        fed_liabilities_rrp = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_reserves.pkl', 'rb') as file:
        fed_liabilities_reserves = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_tga.pkl', 'rb') as file:
        fed_liabilities_tga = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_gse_dmfu.pkl', 'rb') as file:
        fed_liabilities_gse_dmfu = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_total.pkl', 'rb') as file:
        fed_liabilities_total = pickle.load(file)
    fed_liabilities_merge = merge_dfs([fed_liabilities_currency,
                                       fed_liabilities_rrp,
                                       fed_liabilities_foreign_repo,
                                       fed_liabilities_reserves,
                                       fed_liabilities_tga,
                                       fed_liabilities_gse_dmfu,
                                       fed_liabilities_total]).dropna()
    fed_liabilities_merge.index = pd.to_datetime(fed_liabilities_merge.index.values)
    fed_liabilities_merge.columns = ['currency','rrp','foreign_repo',
                                     'reserves','tga','gse_dmfu','total']
    fed_liabilities_merge['others'] = (fed_liabilities_merge['total']-
                                       fed_liabilities_merge['currency'] -
                                       fed_liabilities_merge['rrp']-
                                       fed_liabilities_merge['foreign_repo']-
                                       fed_liabilities_merge['reserves']-
                                       fed_liabilities_merge['tga']-
                                       fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['rrp_total'] = fed_liabilities_merge['rrp'] + fed_liabilities_merge['foreign_repo']
    fed_liabilities_merge['reserves_total'] = (fed_liabilities_merge['reserves'] +
                                               fed_liabilities_merge['tga'] +
                                               fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge = fed_liabilities_merge[start:end]
    fed_liabilities_merge_diff = fed_liabilities_merge.diff(1).dropna()

    ### PLOT ###
    fig = go.Figure()
    cols = ['currency', 'rrp', 'foreign_repo', 'reserves', 'tga', 'gse_dmfu']
    labels = [
        'Currency',
        'RRP Facility',
        'Foreign RP Facility',
        'Commercial Bank Reserves',
        'TGA',
        'GSE/DMFU'
    ]
    colors = ['#9bdaf6', '#4dc6c6', '#356c82', '#001f35', '#fbc430', '#fdad23']
    for col, color, label in zip(cols,colors,labels):
        fig.add_trace(go.Scatter(x=fed_liabilities_merge.index, y=fed_liabilities_merge[col],
                                 mode='lines+markers',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Fed Balance Sheet: Liabilities Summary",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=2, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_liabilities_merge.index,
                y=fed_liabilities_merge[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Fed Balance Sheet: Liabilities Subplots",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=2, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_liabilities_merge_diff.index,
                y=fed_liabilities_merge_diff[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Fed Balance Sheet: Liabilities Weekly Change Subplots",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)



def plot_fed_balance_sheet_assets(start, end, **kwargs):
    ### ASSETS ###
    with open(Path(DATA_DIR) / 'fed_assets_securities_outright.pkl', 'rb') as file:
        fed_assets_securities_outright = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_treasury_securities.pkl', 'rb') as file:
        fed_assets_treasury_securities = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_notes_and_bonds.pkl', 'rb') as file:
        fed_assets_notes_and_bonds = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_mbs.pkl', 'rb') as file:
        fed_assets_mbs = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_total.pkl', 'rb') as file:
        fed_assets_total = pickle.load(file)
    fed_assets_merge = merge_dfs([fed_assets_securities_outright,
                                  fed_assets_treasury_securities,
                                  fed_assets_notes_and_bonds,
                                  fed_assets_mbs,
                                  fed_assets_total]).dropna()
    fed_assets_merge.index = pd.to_datetime(fed_assets_merge.index.values)
    fed_assets_merge.columns = ['securities_outright', 'treasuries',
                                'notes_bonds', 'mbs', 'total']
    fed_assets_merge['lending_portfolio'] = (fed_assets_merge['total'] - fed_assets_merge['securities_outright'])



