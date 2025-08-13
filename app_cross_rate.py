# app_cross_rate.py

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

# IORB Spreads Chart
def plot_iorb_spreads(start, end):
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    dvp_df = pd.DataFrame(requests.get(base_url + 'REPO-DVP_AR_OO-P').json(), columns=["date", "value"])
    gcf_df = pd.DataFrame(requests.get(base_url + 'REPO-GCF_AR_AG-P').json(), columns=["date", "value"])
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date", "value"])
    for df in [dvp_df, gcf_df, tri_df]:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    iorb_spreads_merge = merge_dfs([sofr, iorb, dvp_df, gcf_df, tri_df]).dropna() * 100
    iorb_spreads_merge.columns = ['SOFR','IORB','DVP','GCF','TRI']
    iorb_spreads_merge['SOFR-IORB'] = iorb_spreads_merge['SOFR'] - iorb_spreads_merge['IORB']
    iorb_spreads_merge['DVP-IORB'] = iorb_spreads_merge['DVP'] - iorb_spreads_merge['IORB']
    iorb_spreads_merge['GCF-IORB'] = iorb_spreads_merge['GCF'] - iorb_spreads_merge['IORB']
    iorb_spreads_merge['TRI-IORB'] = iorb_spreads_merge['TRI'] - iorb_spreads_merge['IORB']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=iorb_spreads_merge.index, y=iorb_spreads_merge['SOFR-IORB'], name="SOFR - IORB", line=dict(color='#6ECFF6')))
    fig.add_trace(go.Scatter(x=iorb_spreads_merge.index, y=iorb_spreads_merge['DVP-IORB'], name="DVP - IORB", line=dict(color='#07AFE3')))
    fig.add_trace(go.Scatter(x=iorb_spreads_merge.index, y=iorb_spreads_merge['GCF-IORB'], name="GCF - IORB", line=dict(color='#FFB400')))
    fig.add_trace(go.Scatter(x=iorb_spreads_merge.index, y=iorb_spreads_merge['TRI-IORB'], name="Triparty - IORB", line=dict(color='#F57235')))
    fig.add_hline(y=20, line_dash='dash', line_color='navy')
    fig.update_layout(title="IORB Spreads", yaxis_title='Basis Points', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# GCF-TRI Spread Chart
def plot_gcf_tri_spread(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    dvp_df = pd.DataFrame(requests.get(base_url + 'REPO-DVP_AR_OO-P').json(), columns=["date", "value"])
    gcf_df = pd.DataFrame(requests.get(base_url + 'REPO-GCF_AR_AG-P').json(), columns=["date", "value"])
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date", "value"])
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    for df in [dvp_df, gcf_df, tri_df]:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    iorb_spreads_merge = merge_dfs([sofr, iorb, dvp_df, gcf_df, tri_df]).dropna() * 100
    iorb_spreads_merge.columns = ['SOFR','IORB','DVP','GCF','TRI']
    iorb_spreads_merge = iorb_spreads_merge['2022-01-01':]
    iorb_spreads_merge['GCF-TRI'] = iorb_spreads_merge['GCF'] - iorb_spreads_merge['TRI']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=iorb_spreads_merge.index, y=iorb_spreads_merge['GCF-TRI'], name="GCF - TRI", line=dict(color='#6ECFF6')))
    fig.add_hline(y=20, line_dash='dash', line_color='navy')
    fig.update_layout(title="GCF - TRI Spread", yaxis_title='Basis Points', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# Tri-party - Term Spread Chart
def plot_triparty_term_spread(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date", "value"])
    tri_df['date'] = pd.to_datetime(tri_df['date'])
    tri_df.set_index('date', inplace=True)
    term1w_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_LE30-P').json(), columns=["date", "value"])
    term1w_df['date'] = pd.to_datetime(term1w_df['date'])
    term1w_df.set_index('date', inplace=True)
    tri_term_merge = merge_dfs([tri_df*100, term1w_df*100]).dropna().resample('W').last()
    tri_term_merge.columns = ['tri','dvp_30d']
    tri_term_merge['diff'] = (tri_term_merge['tri'] - tri_term_merge['dvp_30d'])
    tri_term_merge = tri_term_merge['2022-01-01':]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tri_term_merge.index, y=tri_term_merge['diff'], name="Term Spread Proxy", line=dict(color='#48DEE9')))
    fig.update_layout(title="Tri Party Term Spread (ON vs <30d)", yaxis_title='Basis Points', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# The New System (SOFR-EFFR)
def plot_sofr_effr_chart(start, end):
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    sofr_effr_merge = merge_dfs([sofr, fed_funds]).dropna()
    sofr_effr_merge['sofr-effr'] = sofr_effr_merge['SOFR'] - sofr_effr_merge['EFFR']
    sofr_effr_merge['sofr-effr_ma'] = sofr_effr_merge['sofr-effr'].rolling(21).mean()
    sofr_effr_merge = sofr_effr_merge['2023-12-01':]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sofr_effr_merge.index, y=sofr_effr_merge['sofr-effr'], name="SOFR-EFFR", line=dict(color='#48DEE9')))
    fig.add_trace(go.Scatter(x=sofr_effr_merge.index, y=sofr_effr_merge['sofr-effr_ma'], name="SOFR-EFFR 1 Month Index", line=dict(color='#0B2138')))
    fig.update_layout(title="The New System", yaxis_title='Basis Points', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# Visible Repo Rate Complex
def plot_repo_rate_complex_cross(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    dvp_df = pd.DataFrame(requests.get(base_url + 'REPO-DVP_AR_OO-P').json(), columns=["date", "value"])
    gcf_df = pd.DataFrame(requests.get(base_url + 'REPO-GCF_AR_AG-P').json(), columns=["date", "value"])
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date", "value"])
    for df in [dvp_df, gcf_df, tri_df]:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index); srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25
    repo_rate_complex_df = merge_dfs([rrp, srf, sofr, dvp_df, gcf_df, tri_df])['2025-04-01':].dropna()
    repo_rate_complex_df.columns = ['RRP','SRF','SOFR','DVP','GCF','TRIPARTY']
    colors = {'SOFR': '#0B2138','DVP': '#48DEE9','TRIPARTY': '#7EC0EE','GCF': '#F9D15B','SRF': '#F9C846','RRP': '#F39C12'}
    fig = go.Figure()
    for col in repo_rate_complex_df.columns:
        fig.add_trace(go.Scatter(x=repo_rate_complex_df.index, y=repo_rate_complex_df[col], name=col, line=dict(color=colors.get(col))))
    fig.update_layout(title="Visible Repo Rate Complex", yaxis_title='bps', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# Dollar Lending Complex
def plot_dollar_lending_complex(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    dvp_df = pd.DataFrame(requests.get(base_url + 'REPO-DVP_AR_OO-P').json(), columns=["date", "value"])
    gcf_df = pd.DataFrame(requests.get(base_url + 'REPO-GCF_AR_AG-P').json(), columns=["date", "value"])
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date", "value"])
    for df in [dvp_df, gcf_df, tri_df]:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index); srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    repo_rate_complex_df = merge_dfs([rrp, srf, sofr, dvp_df, gcf_df, tri_df, fed_funds, iorb])['2025-04-01':].dropna()
    repo_rate_complex_df.columns = ['RRP','SRF','SOFR','DVP','GCF','TRIPARTY','EFFR','IORB']
    colors = {'SOFR': '#0B2138','DVP': '#48DEE9','TRIPARTY': '#7EC0EE','GCF': '#F9D15B','SRF': '#F9C846','RRP': '#F39C12','EFFR': '#023e8a','IORB': '#808080'}
    fig = go.Figure()
    for col in repo_rate_complex_df.columns:
        fig.add_trace(go.Scatter(x=repo_rate_complex_df.index, y=repo_rate_complex_df[col], name=col, line=dict(color=colors.get(col))))
    fig.update_layout(title="Dollar Lending Complex", yaxis_title='bps', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# SOFR Floor & Ceiling
def plot_sofr_floor_ceiling(start, end):
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index); srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25
    sofr_floor_ceiling_merge = merge_dfs([sofr, rrp, srf])['2025-04-01':].dropna() * 100
    sofr_floor_ceiling_merge.columns = ['SOFR','RRP','SRF']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sofr_floor_ceiling_merge.index, y=sofr_floor_ceiling_merge['SOFR'], name='SOFR', line=dict(color='#07AFE3')))
    fig.add_trace(go.Scatter(x=sofr_floor_ceiling_merge.index, y=sofr_floor_ceiling_merge['SRF'], name='SRF', line=dict(color='#6ECFF6')))
    fig.add_trace(go.Scatter(x=sofr_floor_ceiling_merge.index, y=sofr_floor_ceiling_merge['RRP'], name='RRP', line=dict(color='#FFB400')))
    fig.update_layout(title="SOFR - Floor & Ceiling", yaxis_title='Basis Points', yaxis_range=[415,455], hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# Unsecured Lending Floor & Ceiling
def plot_unsecured_lending_floor_ceiling(start, end):
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    srf = pd.DataFrame(index=fed_funds.index); srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25
    unsecured_lending_merge = merge_dfs([fed_funds, iorb, srf, rrp])['2025-04-01':].dropna()*100
    unsecured_lending_merge.columns = ['EFFR','IORB','SRF','RRP']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=unsecured_lending_merge.index, y=unsecured_lending_merge['EFFR'], name='EFFR', line=dict(color='#6ECFF6')))
    fig.add_trace(go.Scatter(x=unsecured_lending_merge.index, y=unsecured_lending_merge['IORB'], name='IORB', line=dict(color='#07AFE3')))
    fig.add_trace(go.Scatter(x=unsecured_lending_merge.index, y=unsecured_lending_merge['SRF'], name='Discount Window', line=dict(color='#FFB400')))
    fig.add_trace(go.Scatter(x=unsecured_lending_merge.index, y=unsecured_lending_merge['RRP'], name='RRP', line=dict(color='#F57235')))
    fig.add_hline(y=20, line_dash='dash', line_color='navy')
    fig.update_layout(title="Unsecured Lending - Floor and Ceiling", yaxis_title='Basis Points', yaxis_range=[415,455], hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
