### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- LIQUIDITY STRESS -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
from pandas_datareader import data as pdr
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
from plotly.subplots import make_subplots
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- SOFR - IORB ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr_iorb(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'iorb.pkl', 'rb') as file:
        iorb = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)

    spread_df = iorb.join(sofr, how='inner', lsuffix='_IORB', rsuffix='_SOFR')
    spread_df['Spread_bp'] = (spread_df['SOFR'] - spread_df['IORB']) * 100
    spread_df = spread_df[start:end].dropna()

    ### PLOT ###
    plt.figure(figsize=(10, 5))
    plt.step(spread_df.index, spread_df['Spread_bp'],
             where='post', color='skyblue', alpha=0.85, linewidth=3)
    plt.title('Repo Liquidity Stress: SOFR - IORB', fontsize=18, fontweight='bold', loc='left')
    plt.ylabel('Basis Points', fontsize=13)
    plt.xlabel('')
    plt.grid(alpha=0.17)
    plt.tight_layout()
    plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=spread_df.index, y=spread_df['Spread_bp'],
                             mode='lines', name="SOFR - IORB"))
    fig.update_layout(
        title="Repo Liquidity Stress: SOFR - IORB",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- SOFR - FED FUNDS -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr_fedfunds(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)

    spread_df = fed_funds.join(sofr, how='inner', lsuffix='_IORB', rsuffix='_SOFR')
    spread_df['Spread_bp'] = (spread_df['SOFR'] - spread_df['EFFR']) * 100
    spread_df = spread_df[start:end].dropna()

    ### PLOT ###
    plt.figure(figsize=(10, 5))
    plt.step(spread_df.index, spread_df['Spread_bp'],
             where='post', color='skyblue', alpha=0.85, linewidth=3)
    plt.title('Secured vs. Unsecured: SOFR - EFFR', fontsize=18, fontweight='bold', loc='left')
    plt.ylabel('Basis Points', fontsize=13)
    plt.xlabel('')
    plt.grid(alpha=0.17)
    plt.tight_layout()
    plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=spread_df.index, y=spread_df['Spread_bp'],
                             mode='lines', name="SOFR - EFFR"))
    fig.update_layout(
        title="Secured vs. Unsecured: SOFR - EFFR",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SOFR - REPO VENUES ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr_repo_venues(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)

    spread_df = merge_dfs([sofr,gcf_df,dvp_df,tri_df])
    spread_df.columns = ['sofr','gcf','dvp','tri']
    spread_df['sofr-gcf'] = (spread_df['sofr'] - spread_df['gcf']) * 100
    spread_df['sofr-dvp'] = (spread_df['sofr'] - spread_df['dvp']) * 100
    spread_df['sofr-tri'] = (spread_df['sofr'] - spread_df['tri']) * 100
    spread_df = spread_df[start:end].dropna()

    ### PLOT ###
    fig = make_subplots(rows=1, cols=3, subplot_titles=['SOFR-GCF',
                                                        'SOFR-DVP',
                                                        'SOFR-TRI'])
    for i, (col, color, label) in enumerate(zip(['sofr-gcf','sofr-dvp','sofr-tri'],
                                                ['#f8b62d', '#f8772d', '#2f90c5'],
                                                ['SOFR-GCF','SOFR-DVP','SOFR-TRI'])):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=spread_df.index,
                y=spread_df[col],
                mode='lines',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="SOFR vs. Repo Venue Spreads",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)