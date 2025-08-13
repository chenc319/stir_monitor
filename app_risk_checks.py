# app_risk_checks.py

import pandas as pd
import requests
import functools as ft
from pandas_datareader import data as pdr
import streamlit as st
import plotly.graph_objs as go

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

def plot_dash_for_cash_spread(start, end, **kwargs):
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    dash_spread = iorb.join(fed_funds, how='inner', lsuffix='_IORB', rsuffix='_EFFR')
    dash_spread['Spread_bp'] = (dash_spread['EFFR'] - dash_spread['IORB']) * 100
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

def plot_new_sofr_system(start, end, **kwargs):
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    sofr_1m = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
    sofr_3m = pdr.DataReader('SOFR90DAYAVG', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index)
    srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    df_bp = pd.concat([
        fed_funds.rename(columns={'EFFR': 'EFFR'}),
        sofr.rename(columns={'SOFR': 'SOFR'}),
        sofr_1m.rename(columns={'SOFR30DAYAVG': 'SOFR 1M'}),
        sofr_3m.rename(columns={'SOFR90DAYAVG': 'SOFR 3M'}),
        srf,
        rrp.rename(columns={'RRPONTSYAWARD': 'RRP'})
    ], axis=1) * 100
    df_bp = df_bp.dropna()
    fig = go.Figure()
    for col, color in zip(['EFFR', 'SOFR 3M', 'SOFR 1M', 'SOFR', 'SRF', 'RRP'],
                          ['#9bdaf6', '#4dc6c6', '#356c82', '#001f35', '#fbc430', '#fdad23']):
        fig.add_trace(go.Scatter(x=df_bp.index, y=df_bp[col], mode='lines+markers', name=col, line=dict(color=color)))
    fig.update_layout(
        title="The New SOFR System",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_repo_rate_complex(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    def ofr_to_df(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index); srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    dvp_df = ofr_to_df('REPO-DVP_AR_OO-P')
    gcf_df = ofr_to_df('REPO-GCF_AR_AG-P')
    tri_df = ofr_to_df('REPO-TRI_AR_OO-P')
    repo_df = merge_dfs([rrp, srf, sofr, dvp_df, gcf_df, tri_df]).dropna()
    repo_df.columns = ['RRP', 'SRF', 'SOFR', 'DVP', 'GCF', 'TRIPARTY']
    colors = {'SOFR': '#0B2138', 'DVP': '#48DEE9', 'TRIPARTY': '#7EC0EE', 'GCF': '#F9D15B', 'SRF': '#F9C846', 'RRP': '#F39C12'}
    fig = go.Figure()
    for col in repo_df.columns:
        fig.add_trace(go.Scatter(x=repo_df.index, y=repo_df[col], mode='lines+markers', name=col, line=dict(color=colors.get(col))))
    fig.update_layout(
        title="Visible Repo Rate Complex",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_sofr_distribution(start, end, **kwargs):
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    sofr1 = pdr.DataReader('SOFR1', 'fred', start, end)
    sofr25 = pdr.DataReader('SOFR25', 'fred', start, end)
    sofr75 = pdr.DataReader('SOFR75', 'fred', start, end)
    sofr99 = pdr.DataReader('SOFR99', 'fred', start, end)
    df = merge_dfs([sofr, sofr1, sofr25, sofr75, sofr99]).dropna()
    colors = ['#9DDCF9', '#4CD0E9', '#233852', '#F5B820', '#E69B93']
    names = ['SOFR', 'SOFR1', 'SOFR25', 'SOFR75', 'SOFR99']
    fig = go.Figure()
    for col, color in zip(names, colors):
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines+markers', name=col, line=dict(color=color)))
    fig.update_layout(
        title="SOFR Distribution",
        yaxis_title="Basis Points",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_fed_balance_sheet(start, end, **kwargs):
    treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    df = merge_dfs([treasury, mbs]).loc[start:end].dropna()
    df.columns = ['SOMA Treasury', 'SOMA MBS']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['SOMA Treasury'], mode='lines+markers', name='SOMA Treasury', line=dict(color="#46b5ca", width=3)))
    fig.add_trace(go.Scatter(x=df.index, y=df['SOMA MBS'], mode='lines+markers', name='SOMA MBS', line=dict(color="#17354c", width=3)))
    fig.update_layout(
        title="FED Balance Sheet",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_monitoring_reserves(start, end, **kwargs):
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    rrp_on = pdr.DataReader('RRPONTSYD', 'fred', start, end) / 1e3
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    tri_volume_df = pd.DataFrame(requests.get('https://data.financialresearch.gov/v1/series/timeseries?mnemonic=REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
    tri_volume_df['date'] = pd.to_datetime(tri_volume_df['date'])
    tri_volume_df.set_index('date', inplace=True)
    tri_volume_df = tri_volume_df / 1e12
    triparty_rrp_merge = merge_dfs([tri_volume_df, rrp]).dropna()
    tri_repo_diff = pd.DataFrame(triparty_rrp_merge.iloc[:, 0] - triparty_rrp_merge.iloc[:, 1], columns=['Triparty - RRP'])
    df = merge_dfs([reserves, tga, rrp, tri_repo_diff, rrp_on]).loc[start:end].dropna()
    df.columns = ['Bank Reserves', 'TGA', 'RRP', 'Triparty - RRP', 'RRP ON']
    series = [
        ('Bank Reserves', "#aad8ef"),
        ('TGA', "#4da3d7"),
        ('RRP', "#17293c"),
        ('Triparty - RRP', "#f5c23e"),
        ('RRP ON', "#f5b9ad"),
    ]
    fig = go.Figure()
    for col, color in series:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines+markers', name=col, line=dict(color=color)))
    fig.update_layout(
        title="Monitoring reserves",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_fed_action_vs_reserve_response(start, end, **kwargs):
    fed_action = pdr.DataReader('WALCL', 'fred', start, end) / 1e6
    reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    df = merge_dfs([fed_action, reserves_volume])
    df.columns = ['Fed Action', 'Reserve Response']
    df = df.resample('ME').last().diff(1).loc[start:end].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Fed Action'], mode='lines+markers', name='Fed Action', line=dict(color='#30b0c1', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Reserve Response'], mode='lines+markers', name='Reserve Response', line=dict(color='#17293c', width=2)))
    fig.update_layout(
        title="FED Action Vs Reserve Response",
        yaxis_title="30-Day Change (Trillions of $)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_fed_action_vs_reserve_response_v2(start, end, **kwargs):
    fed_action = pdr.DataReader('WALCL', 'fred', start, end) / 1e6
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    reserve_response_v2_merge = merge_dfs([rrp, tga_volume]).resample('ME').last()
    reserve_response_v2 = pd.DataFrame(reserve_response_v2_merge.sum(axis=1).diff(1))
    df = merge_dfs([fed_action.resample('ME').last().diff(1), reserve_response_v2])
    df.columns = ['Fed Action', 'RRP + TGA']
    df = df.loc[start:end].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Fed Action'], mode='lines+markers', name='Fed Action', line=dict(color='#30b0c1', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['RRP + TGA'], mode='lines+markers', name='RRP + TGA', line=dict(color='#17293c', width=2)))
    fig.update_layout(
        title="FED Action Vs Reserve Response",
        yaxis_title="30-Day Change (Trillions of $)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
