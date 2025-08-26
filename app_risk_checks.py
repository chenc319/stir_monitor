### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- RISK CHECKS ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import requests
import functools as ft
from pandas_datareader import data as pdr
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
base_path = '/Users/chenc/Documents/GitHub/stir_monitor/data/'

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- FED FUNDS - IORB -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_dash_for_cash_spread(start, end, **kwargs):
    iorb = pd.read_pickle(base_path + 'iorb.pkl')
    fed_funds = pd.read_pickle(base_path + 'fed_funds.pkl')
    dash_spread = iorb.join(fed_funds, how='inner', lsuffix='_IORB', rsuffix='_EFFR')
    dash_spread['Spread_bp'] = (dash_spread['EFFR'] - dash_spread['IORB']) * 100

    # ### PLOT ###
    # plt.figure(figsize=(10, 5))
    # plt.step(dash_spread.index, dash_spread['Spread_bp'],
    #          where='post', color='skyblue', alpha=0.85, linewidth=3)
    # plt.title('Monitoring the Dash For Cash\nFed Funds - IORB', fontsize=18, fontweight='bold', loc='left')
    # plt.ylabel('Basis Points', fontsize=13)
    # plt.xlabel('')
    # plt.grid(alpha=0.17)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dash_spread.index, y=dash_spread['Spread_bp'],
                             mode='lines+markers', name="EFFR - IORB"))
    fig.update_layout(
        title="Monitoring the Dash For Cash<br>Fed Funds - IORB",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- NEW SOFR SYSTEM --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_new_sofr_system(start, end, **kwargs):
    fed_funds = pd.read_pickle(base_path + 'fed_funds.pkl')
    sofr = pd.read_pickle(base_path + 'sofr.pkl')
    sofr_1m_avg = pd.read_pickle(base_path + 'sofr_1m_avg.pkl')
    sofr_3m_avg = pd.read_pickle(base_path + 'sofr_3m_avg.pkl')
    rrp = pd.read_pickle(base_path + 'rrp.pkl')
    srf = pd.DataFrame(index=sofr.index)
    srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    df_bp = pd.concat([
        fed_funds.rename(columns={'EFFR': 'EFFR'}),
        sofr.rename(columns={'SOFR': 'SOFR'}),
        sofr_1m_avg.rename(columns={'SOFR30DAYAVG': 'SOFR 1M'}),
        sofr_3m_avg.rename(columns={'SOFR90DAYAVG': 'SOFR 3M'}),
        srf,
        rrp.rename(columns={'RRPONTSYAWARD': 'RRP'})
    ], axis=1) * 100
    df_bp = df_bp.dropna()
    df_bp = df_bp['2025-04-01':]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df_bp.index, df_bp['EFFR'], label='EFFR', color='#9bdaf6')
    # plt.plot(df_bp.index, df_bp['SOFR 3M'], label='SOFR 3M', color='#4dc6c6')
    # plt.plot(df_bp.index, df_bp['SOFR 1M'], label='SOFR 1M', color='#356c82')
    # plt.plot(df_bp.index, df_bp['SOFR'], label='SOFR', color='#001f35', linewidth=2)
    # plt.plot(df_bp.index, df_bp['SRF'], label='SRF', color='#fbc430')
    # plt.plot(df_bp.index, df_bp['RRP'], label='RRP', color='#fdad23')
    # plt.ylabel("Basis Points")
    # plt.title("The New SOFR System", fontsize=20, fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col, color in zip(['EFFR', 'SOFR 3M', 'SOFR 1M', 'SOFR', 'SRF', 'RRP'],
                          ['#9bdaf6', '#4dc6c6', '#356c82', '#001f35', '#fbc430', '#fdad23']):
        fig.add_trace(go.Scatter(x=df_bp.index, y=df_bp[col],
                                 mode='lines+markers',
                                 name=col,
                                 line=dict(color=color)))
    fig.update_layout(
        title="The New SOFR System",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- VISIBLE REPO RATE COMPLEX ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_repo_rate_complex(start, end, **kwargs):


    rrp = pd.read_pickle(base_path + 'rrp.pkl')
    sofr = pd.read_pickle(base_path + 'sofr.pkl')
    srf = pd.DataFrame(index=sofr.index)
    srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    dvp_df = pd.read_pickle(base_path + 'dvp_df.pkl')
    gcf_df = pd.read_pickle(base_path + 'gcf_df.pkl')
    tri_df = pd.read_pickle(base_path + 'tri_df.pkl')
    repo_df = merge_dfs([rrp, srf, sofr, dvp_df, gcf_df, tri_df]).dropna()
    repo_df.columns = ['RRP', 'SRF', 'SOFR', 'DVP', 'GCF', 'TRIPARTY']
    colors = {'SOFR': '#0B2138', 'DVP': '#48DEE9', 'TRIPARTY': '#7EC0EE',
              'GCF': '#F9D15B', 'SRF': '#F9C846', 'RRP': '#F39C12'}
    repo_df = repo_df['2025-04-01':]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(repo_df.index, repo_df['RRP'],
    #          lw=2, color=colors['RRP'], label="RRP")
    # plt.plot(repo_df.index, repo_df['SRF'],
    #          lw=2, color=colors['SRF'], label="SRF", alpha=0.95)
    # plt.plot(repo_df.index, repo_df['SOFR'],
    #          lw=2, color=colors['SOFR'], label="SOFR")
    # plt.plot(repo_df.index, repo_df['DVP'],
    #          lw=2, color=colors['DVP'], label="DVP")
    # plt.plot(repo_df.index, repo_df['GCF'],
    #          lw=2, color=colors['GCF'], label="GCF")
    # plt.plot(repo_df.index, repo_df['TRIPARTY'],
    #          lw=2, color=colors['TRIPARTY'], label="TRIPARTY")
    # plt.ylabel("Basis Points")
    # plt.title("Visible Repo Rate Complex", fontsize=20, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col in repo_df.columns:
        fig.add_trace(go.Scatter(x=repo_df.index, y=repo_df[col],
                                 mode='lines+markers',
                                 name=col, line=dict(color=colors.get(col))))
    fig.update_layout(
        title="Visible Repo Rate Complex",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SOFR DISTRIBUTION -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr_distribution(start, end, **kwargs):
    sofr = pd.read_pickle(base_path + 'sofr.pkl')
    sofr1 = pd.read_pickle(base_path + 'sofr1.pkl')
    sofr25 = pd.read_pickle(base_path + 'sofr25.pkl')
    sofr75 = pd.read_pickle(base_path + 'sofr75.pkl')
    sofr99 = pd.read_pickle(base_path + 'sofr99.pkl')
    df = merge_dfs([sofr, sofr1, sofr25, sofr75, sofr99]).dropna()
    colors = ['#9DDCF9', '#4CD0E9', '#233852', '#F5B820', '#E69B93']
    names = ['SOFR', 'SOFR1', 'SOFR25', 'SOFR75', 'SOFR99']
    df = df['2025-04-01':]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(df.index, df['SOFR'],
    #          label='SOFR', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(df.index, df['SOFR1'],
    #          label='SOFR 1%', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(df.index, df['SOFR25'],
    #          label='SOFR 25%', color='#233852', lw=2)  # dark blue
    # plt.plot(df.index, df['SOFR75'],
    #          label='SOFR 75%', color='#F5B820', lw=2)  # yellow/orange
    # plt.plot(df.index, df['SOFR99'],
    #          label='SOFR 99%', color='#E69B93', lw=2)  # salmon/pink
    # plt.ylabel("Basis Points")
    # plt.title("SOFR Distribution", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col, color in zip(names, colors):
        fig.add_trace(go.Scatter(x=df.index, y=df[col],
                                 mode='lines+markers',
                                 name=col,
                                 line=dict(color=color)))
    fig.update_layout(
        title="SOFR Distribution",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- FED BALANCE SHEET -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_balance_sheet(start, end, **kwargs):
    treasury = pd.read_pickle(base_path + 'treasury.pkl')
    mbs = pd.read_pickle(base_path + 'mbs.pkl')
    df = merge_dfs([treasury, mbs]).loc[start:end].dropna()
    df.columns = ['SOMA Treasury', 'SOMA MBS']

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df.index, df['SOMA Treasury'],
    #          color="#46b5ca", lw=3, label='SOMA Treasury')
    # plt.plot(df.index, df['SOMA MBS'],
    #          color="#17354c", lw=3, label='SOMA MBS')
    # plt.title("FED Balance Sheet", fontsize=22, fontweight="bold")
    # plt.ylabel("Dollars (Trillions)")
    # plt.ylim(1, 6.5)
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=2)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['SOMA Treasury'],
                             mode='lines+markers',
                             name='SOMA Treasury',
                             line=dict(color="#46b5ca", width=3)))
    fig.add_trace(go.Scatter(x=df.index, y=df['SOMA MBS'],
                             mode='lines+markers',
                             name='SOMA MBS',
                             line=dict(color="#17354c", width=3)))
    fig.update_layout(
        title="FED Balance Sheet",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ MONITORING RESERVES ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_monitoring_reserves(start, end, **kwargs):
    reserves = pd.read_pickle(base_path + 'reserves.pkl')
    tga = pd.read_pickle(base_path + 'tga.pkl')
    rrp_on_volume = pd.read_pickle(base_path + 'rrp_on_volume.pkl')
    rrp_volume = pd.read_pickle(base_path + 'rrp_volume.pkl')
    tri_volume_df = pd.read_pickle(base_path + 'tri_volume_df.pkl')
    triparty_rrp_merge = merge_dfs([tri_volume_df, rrp_volume]).dropna()
    tri_repo_diff = pd.DataFrame(triparty_rrp_merge.iloc[:, 0] -
                                 triparty_rrp_merge.iloc[:, 1], columns=['Triparty - RRP'])
    df = merge_dfs([reserves, tga, rrp_volume, tri_repo_diff, rrp_on_volume]).loc[start:end].dropna()
    df.columns = ['Bank Reserves', 'TGA', 'RRP', 'Triparty - RRP', 'RRP ON']
    series = [
        ('Bank Reserves', "#aad8ef"),
        ('TGA', "#4da3d7"),
        ('RRP', "#17293c"),
        ('Triparty - RRP', "#f5c23e"),
        ('RRP ON', "#f5b9ad"),
    ]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df.index, df['Bank Reserves'],
    #          label="Bank Reserves", color="#aad8ef", lw=3)
    # plt.plot(df.index, df['TGA'],
    #          label="TGA", color="#4da3d7", lw=2)
    # plt.plot(df.index, df['RRP'],
    #          label="RRP", color="#17293c", lw=2)
    # plt.plot(df.index, df['Triparty - RRP'],
    #          label="Triparty - RRP", color="#f5c23e", lw=2)
    # plt.plot(df.index, df['RRP ON'],
    #          label="RRP ON", color="#f5b9ad", lw=2)
    # plt.title("Monitoring reserves", fontsize=22, fontweight="bold")
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col, color in series:
        fig.add_trace(go.Scatter(x=df.index, y=df[col],
                                 mode='lines+markers',
                                 name=col,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Monitoring reserves",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ FED ACTION VS RESERVE RESPONSE -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_action_vs_reserve_response(start, end, **kwargs):
    fed_action = pd.read_pickle(base_path + 'fed_action.pkl')
    reserves_volume = pd.read_pickle(base_path + 'reserves.pkl')
    df = merge_dfs([fed_action, reserves_volume])
    df.columns = ['Fed Action', 'Reserve Response']
    df = df.resample('ME').last().diff(1).loc[start:end].dropna()

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df.index,
    #          df['Fed Action'],
    #          label='Fed Action', color='#30b0c1', linewidth=2)
    # plt.plot(df.index,
    #          df['Reserve Response'],
    #          label='Reserve Response', color='#17293c', linewidth=2)
    # plt.ylabel('30-Day Change (Trillions of $)')
    # plt.title('FED Action Vs Reserve Response')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Fed Action'],
                             mode='lines+markers',
                             name='Fed Action',
                             line=dict(color='#30b0c1', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Reserve Response'],
                             mode='lines+markers',
                             name='Reserve Response',
                             line=dict(color='#17293c', width=2)))
    fig.update_layout(
        title="FED Action Vs Reserve Response",
        yaxis_title="30-Day Change (Trillions of $)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ FED ACTION VS RESERVE RESPONSE -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_action_vs_reserve_response_v2(start, end, **kwargs):
    fed_action = pd.read_pickle(base_path + 'fed_action.pkl')
    rrp = pd.read_pickle(base_path + 'rrp_volume.pkl')
    tga_volume = pd.read_pickle(base_path + 'tga.pkl')
    reserve_response_v2_merge = merge_dfs([rrp, tga_volume]).resample('ME').last()
    reserve_response_v2 = pd.DataFrame(reserve_response_v2_merge.sum(axis=1).diff(1))
    df = merge_dfs([fed_action.resample('ME').last().diff(1), reserve_response_v2])
    df.columns = ['Fed Action', 'RRP + TGA']
    df = df.loc[start:end].dropna()

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df.index,
    #          df['Fed Action'],
    #          label='Fed Action', color='#30b0c1', linewidth=2)
    # plt.plot(df.index,
    #          df['RRP + TGA'],
    #          label='RRP + TGA', color='#17293c', linewidth=2)
    # plt.ylabel('30-Day Change (Trillions of $)')
    # plt.title('FED Action Vs Reserve Response')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Fed Action'],
                             mode='lines+markers',
                             name='Fed Action',
                             line=dict(color='#30b0c1', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['RRP + TGA'],
                             mode='lines+markers',
                             name='RRP + TGA',
                             line=dict(color='#17293c', width=2)))
    fig.update_layout(
        title="FED Action Vs Reserve Response",
        yaxis_title="30-Day Change (Trillions of $)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
