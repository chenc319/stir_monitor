# app_repo.py

import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from pandas_datareader import data as pdr
from fredapi import Fred

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

@st.cache_data(ttl=3600)
def get_pd_repo_data():
    def fetch(url, colname):
        df = pd.DataFrame(requests.get(url).json()['pd']['timeseries'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        df['asofdate'] = pd.to_datetime(df['asofdate'])
        df = df.set_index('asofdate')[['value']].rename(columns={'value': colname})
        return df
    total_repo = fetch('https://markets.newyorkfed.org/api/pd/get/PDSORA-UTSETTOT.json', 'pd_total_repo')
    nccbr_on = fetch('https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSET.json', 'pd_nccbr_on')
    nccbr_l30 = fetch('https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSETTAL30.json', 'pd_nccbr_l30')
    nccbr_g30 = fetch('https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSETTAG30.json', 'pd_nccbr_g30')
    return total_repo, nccbr_on, nccbr_l30, nccbr_g30

@st.cache_data(ttl=3600)
def get_ofr_time_series():
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    def pull(mnemonic, col, scale=1):
        df = pd.DataFrame(requests.get(base_url+mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').rename(columns={'value': col}) / scale
        return df
    tri = pull('REPO-TRI_TV_TOT-P', 'tri', 1e12)
    dvp = pull('REPO-DVP_TV_TOT-P', 'dvp', 1e12)
    gcf = pull('REPO-GCF_TV_TOT-P', 'gcf', 1e12)
    return tri, dvp, gcf

def get_rrp_series(start, end):
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    rrp.index = pd.to_datetime(rrp.index)
    return rrp.rename(columns={'WLRRAL': 'RRP'})

#-------------------------------------------------------
# Proxy non-cleared percent
#-------------------------------------------------------
def plot_proxy_percent_without_clearing(start, end):
    total_repo, nccbr_on, nccbr_l30, nccbr_g30 = get_pd_repo_data()
    pd_merge = merge_dfs([total_repo, nccbr_on, nccbr_l30, nccbr_g30])
    pd_merge['pd_nccbr_total'] = pd_merge['pd_nccbr_on'] + pd_merge['pd_nccbr_l30'] + pd_merge['pd_nccbr_g30']
    pd_merge['nccbr_pct'] = pd_merge['pd_nccbr_total'] / pd_merge['pd_total_repo']
    pd_merge = pd_merge.dropna()
    pd_merge = pd_merge[(pd_merge.index >= pd.to_datetime(start)) & (pd_merge.index <= pd.to_datetime(end))]

    tri, dvp, gcf = get_ofr_time_series()
    rrp = get_rrp_series(pd.to_datetime(start), pd.to_datetime(end))
    tri_aligned = tri.reindex(rrp.index, method='ffill').dropna()
    dvp_aligned = dvp.reindex(rrp.index, method='ffill').dropna()
    gcf_aligned = gcf.reindex(rrp.index, method='ffill').dropna()
    total_repo_vol = (tri_aligned['tri'] + dvp_aligned['dvp'] + gcf_aligned['gcf']
                      + pd_merge['pd_nccbr_total'].reindex(tri_aligned.index, method='ffill')/1e6).dropna()
    all_venues = merge_dfs([tri_aligned, dvp_aligned, gcf_aligned, rrp, total_repo_vol.to_frame('all_repo')]).dropna()
    all_venues['black'] = (all_venues['tri'] - all_venues['RRP']) / (all_venues['all_repo'] - all_venues['RRP'])
    all_venues = all_venues.resample('W').last()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pd_merge.index, y=pd_merge['nccbr_pct']*100,
                             name="% NCCBR PD", line=dict(color="#f8b62d")))
    fig.add_trace(go.Scatter(x=all_venues.index, y=all_venues['black']*100,
                             name="TriParty-RRP/(TriParty+DVP+GCF-RRP)", line=dict(color="#f8772d")))
    fig.update_layout(title="Proxy of % of Non Cleared Repos", yaxis_title="%", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_volume_per_venue(start, end):
    tri, dvp, gcf = get_ofr_time_series()
    rrp = get_rrp_series(start, end)
    merge = merge_dfs([dvp, rrp, gcf, (tri - rrp).rename(columns={'tri': 'Triparty-RRP'})]).dropna()
    fig = go.Figure()
    for col, color in zip(['dvp','RRP','gcf','Triparty-RRP'], ["#f8b62d","#f8772d","#2f90c5","#67cbe7"]):
        fig.add_trace(go.Scatter(x=merge.index, y=merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Volume per Venue", yaxis_title="Dollars (Trillions)", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_mmf_by_asset(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    repo = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_TOT-M').json(), columns=['date','value'])
    repo = repo.set_index(pd.to_datetime(repo['date']))[['value']].rename(columns={'value':'repo'}) / 1e12
    total = pd.DataFrame(requests.get(base_url+'MMF-MMF_TOT-M').json(), columns=['date','value'])
    total = total.set_index(pd.to_datetime(total['date']))[['value']].rename(columns={'value':'total'}) / 1e12
    ts = pd.DataFrame(requests.get(base_url+'MMF-MMF_T_TOT-M').json(), columns=['date','value'])
    ts = ts.set_index(pd.to_datetime(ts['date']))[['value']].rename(columns={'value':'ts'}) / 1e12
    merge = merge_dfs([repo, total, ts])
    merge['US_Repo_Allocation'] = merge['repo'] / merge['total']
    merge['US_TS_Allocation'] = merge['ts'] / merge['total']
    merge = merge.loc[(merge.index >= pd.to_datetime(start)) & (merge.index <= pd.to_datetime(end))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['US_TS_Allocation'], name='U.S. Treasury Sec.', line=dict(color='#29B6D9')))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['US_Repo_Allocation'], name='U.S. Treasury Repo', line=dict(color='#272f37')))
    fig.update_layout(title='Investment of MMF by Asset', yaxis_title='% Allocation', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_6m_volume_change(start, end):
    tri, dvp, gcf = get_ofr_time_series()
    rrp = get_rrp_series(start, end)
    merge = merge_dfs([dvp, rrp, gcf, (tri - rrp).rename(columns={'tri': 'Triparty-RRP'})]).dropna()
    roc_6m = merge.resample('ME').last().diff(1)
    fig = go.Figure()
    for col, color in zip(['dvp','RRP','gcf','Triparty-RRP'], ["#f8b62d", "#f8772d", "#2f90c5", "#67cbe7"]):
        fig.add_trace(go.Scatter(x=roc_6m.index, y=roc_6m[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Monthly Change in Volume per Venue", yaxis_title="Dollars (Trillions)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_volume_invested_in_mmf(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    mmf = pd.DataFrame(requests.get(base_url+'MMF-MMF_TOT-M').json(), columns=["date", "value"])
    mmf = mmf.set_index(pd.to_datetime(mmf['date']))[['value']].rename(columns={'value': 'MMF_TOTAL'}) / 1e12
    mmf = mmf['2021-01-01':]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf.index, y=mmf['MMF_TOTAL'], line=dict(color='#67cbe7')))
    fig.update_layout(title="Volume Invested in MMF", yaxis_title="Trillions", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_rrp_vs_foreign_rrp(start, end):
    fred = Fred(api_key='6905137c26f03db5c8c09f70b7839150')
    rrp = get_rrp_series(start, end)
    foreign_rrp = pd.DataFrame(fred.get_series('WREPOFOR', observation_start=start, observation_end=end) / 1e6)
    rrp_foreign = merge_dfs([rrp, foreign_rrp])
    rrp_foreign.columns = ['RRP','Foreign_RRP']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rrp_foreign.index, y=rrp_foreign['RRP'], name='RRP', line=dict(color='#07AFE3')))
    fig.add_trace(go.Scatter(x=rrp_foreign.index, y=rrp_foreign['Foreign_RRP'], name='Foreign RRP', line=dict(color='#F57235')))
    fig.update_layout(title="RRP vs. Foreign RRP", yaxis_title="Trillions", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_mmf_repo_vs_non_repo(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    repo = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_TOT-M').json(), columns=['date','value'])
    repo = repo.set_index(pd.to_datetime(repo['date']))[['value']].rename(columns={'value':'repo'}) / 1e12
    total = pd.DataFrame(requests.get(base_url+'MMF-MMF_TOT-M').json(), columns=['date','value'])
    total = total.set_index(pd.to_datetime(total['date']))[['value']].rename(columns={'value':'total'}) / 1e12
    merge = merge_dfs([repo, total])
    merge['non_repo'] = merge['total'] - merge['repo']
    merge = merge['2019-01-01':]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['non_repo'], name="Non-Repo Allocation", line=dict(color="#f8b62d")))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['repo'], name="Repo Allocation", line=dict(color="#f8772d")))
    fig.update_layout(title="MMF Repo vs Non Repo", yaxis_title="Dollars", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_triparty_adjusted_for_rrp(start, end):
    tri, dvp, _ = get_ofr_time_series()
    rrp = get_rrp_series(start, end)
    triparty_merge = merge_dfs([tri, rrp, dvp])
    triparty_merge.columns = ['tri','rrp','dvp']
    triparty_merge['triparty-rrp'] = triparty_merge['tri'] - triparty_merge['rrp']
    triparty_merge['residual_flows'] = triparty_merge['dvp'] - triparty_merge['triparty-rrp']
    triparty_merge = triparty_merge.dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['triparty-rrp'], name="Triparty-RRP", line=dict(color="#f8b62d")))
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['dvp'], name="DVP", line=dict(color="#f8772d")))
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['residual_flows'], name="Residual Flow", line=dict(color="#2f90c5")))
    fig.update_layout(title="Tri-Party Adjusted for RRP", yaxis_title="Trillions", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
def plot_mmf_allocation_by_counterparty(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    fc = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wFFI-M').json(), columns=['date','value'])
    fc = fc.set_index(pd.to_datetime(fc['date']))[['value']].rename(columns={'value':'foreign'}) / 1e12
    fe = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wFR-M').json(), columns=['date','value'])
    fe = fe.set_index(pd.to_datetime(fe['date']))[['value']].rename(columns={'value':'fed'}) / 1e12
    usf = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wDFI-M').json(), columns=['date','value'])
    usf = usf.set_index(pd.to_datetime(usf['date']))[['value']].rename(columns={'value':'us_inst'}) / 1e12
    ficc = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wFICC-M').json(), columns=['date','value'])
    ficc = ficc.set_index(pd.to_datetime(ficc['date']))[['value']].rename(columns={'value':'ficc'}) / 1e12
    merge = merge_dfs([fc, fe, usf, ficc]).dropna()['2020-12-01':]
    fig = go.Figure()
    for col, color in zip(['foreign','fed','us_inst','ficc'], ["#f8b62d","#f8772d","#2f90c5","#67cbe7"]):
        fig.add_trace(go.Scatter(x=merge.index, y=merge[col], name=col.replace('_',' ').title(), line=dict(color=color)))
    fig.update_layout(title="Allocation of MMF by Counterparties", yaxis_title="Trillions", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
