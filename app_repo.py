# app_repo.py

import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from pandas_datareader import data as pdr

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right:
                        pd.merge(left, right, left_index=True, right_index=True, how='outer'),
                     array_of_dfs)

# --- 1. Proxy of % Without Central Clearing ---
def plot_proxy_percent_without_clearing(start, end, **kwargs):
    # NY Fed Primary Dealer Series
    def fetch_nyfed_json(url, colname):
        df = pd.DataFrame(requests.get(url).json()['pd']['timeseries'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        df['asofdate'] = pd.to_datetime(df['asofdate'])
        df = df.set_index('asofdate')[['value']].rename(columns={'value': colname})
        return df

    total_repo = fetch_nyfed_json('https://markets.newyorkfed.org/api/pd/get/PDSORA-UTSETTOT.json', 'pd_total_repo')
    nccbr_on = fetch_nyfed_json('https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSET.json', 'pd_nccbr_on')
    nccbr_l30 = fetch_nyfed_json('https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSETTAL30.json', 'pd_nccbr_l30')
    nccbr_g30 = fetch_nyfed_json('https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSETTAG30.json', 'pd_nccbr_g30')

    pd_merge = merge_dfs([total_repo, nccbr_on, nccbr_l30, nccbr_g30])
    pd_merge['pd_nccbr_total'] = pd_merge['pd_nccbr_on'] + pd_merge['pd_nccbr_l30'] + pd_merge['pd_nccbr_g30']
    pd_merge['nccbr_pct'] = pd_merge['pd_nccbr_total'] / pd_merge['pd_total_repo']
    pd_merge = pd_merge.dropna()
    if start and end:
        pd_merge = pd_merge[(pd_merge.index >= pd.to_datetime(start)) & (pd_merge.index <= pd.to_datetime(end))]

    # Venue-level Proxy: Tri-party, DVP, GCF - RRP
    def ofr_vol(mnemonic, col):
        url = f"https://data.financialresearch.gov/v1/series/timeseries?mnemonic={mnemonic}"
        df = pd.DataFrame(requests.get(url).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date').rename(columns={'value': col}) / 1e12

    tri = ofr_vol('REPO-TRI_TV_TOT-P', 'tri')
    dvp = ofr_vol('REPO-DVP_TV_TOT-P', 'dvp')
    gcf = ofr_vol('REPO-GCF_TV_TOT-P', 'gcf')
    rrp = pdr.DataReader('WLRRAL', 'fred', pd.to_datetime(start), pd.to_datetime(end)) / 1e6
    rrp.index = pd.to_datetime(rrp.index)
    rrp = rrp.rename(columns={'WLRRAL': 'RRP'})
    # Merge all and align
    tri_aligned = tri.reindex(rrp.index, method='ffill')
    dvp_aligned = dvp.reindex(rrp.index, method='ffill')
    gcf_aligned = gcf.reindex(rrp.index, method='ffill')
    venue_merge = merge_dfs([tri_aligned, dvp_aligned, gcf_aligned, rrp])
    venue_merge['all_repo'] = venue_merge[['tri','dvp','gcf','RRP']].sum(axis=1, skipna=True)
    venue_merge['black'] = (venue_merge['tri'] - venue_merge['RRP']) / (venue_merge['all_repo'] - venue_merge['RRP'])
    venue_merge = venue_merge.resample('W').last()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pd_merge.index, y=pd_merge['nccbr_pct']*100, mode='lines+markers',
                             name='% NCCBR (Primary Dealers)', line=dict(color="#f8b62d")))
    fig.add_trace(go.Scatter(x=venue_merge.index, y=venue_merge['black']*100, mode='lines+markers',
                             name="Tri-Party-RRP/(Tri-Party+DVP+GCF-RRP)", line=dict(color="#f8772d")))
    fig.update_layout(title="Proxy of % of Non Cleared Repos",
                     yaxis_title="%",
                     xaxis_title="Date",
                     hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# --- 2. Volume per Venue ---
def plot_volume_per_venue(start, end, **kwargs):
    # OFR volumes
    def ofr_vol(mnemonic, col):
        url = f"https://data.financialresearch.gov/v1/series/timeseries?mnemonic={mnemonic}"
        df = pd.DataFrame(requests.get(url).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date').rename(columns={'value': col}) / 1e12

    dvp = ofr_vol('REPO-DVP_TV_TOT-P','DVP')
    gcf = ofr_vol('REPO-GCF_TV_TOT-P','GCF')
    tri = ofr_vol('REPO-TRI_TV_TOT-P','TRIPARTY')
    rrp = pdr.DataReader('WLRRAL', 'fred', pd.to_datetime(start), pd.to_datetime(end)) / 1e6
    rrp.index = pd.to_datetime(rrp.index)
    rrp = rrp.rename(columns={'WLRRAL': 'RRP'})

    triparty_rrp = (tri - rrp).rename(columns={'TRIPARTY': 'Triparty-RRP'})
    volume_merge = merge_dfs([dvp, rrp, gcf, triparty_rrp]).dropna()
    if start and end:
        volume_merge = volume_merge[(volume_merge.index >= pd.to_datetime(start)) &
                                   (volume_merge.index <= pd.to_datetime(end))]

    fig = go.Figure()
    for col, color in zip(['DVP', 'RRP', 'GCF', 'Triparty-RRP'],
                          ["#f8b62d","#f8772d","#2f90c5","#67cbe7"]):
        fig.add_trace(go.Scatter(x=volume_merge.index, y=volume_merge[col], mode='lines+markers',
                                 name=col, line=dict(color=color)))
    fig.update_layout(title="Volume per Venue",
                     yaxis_title="Dollars (Trillions)",
                     xaxis_title="Date",
                     hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# --- 3. Investment of MMF by Asset ---
def plot_mmf_by_asset(start, end, **kwargs):
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
    fig.update_layout(title='Investment of MMF by Asset',
                     yaxis_title='% Allocation',
                     xaxis_title="Date",
                     hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# --- 4. 6M Volume Change ---
def plot_6m_volume_change(start, end, **kwargs):
    def ofr_vol(mnemonic, col):
        url = f"https://data.financialresearch.gov/v1/series/timeseries?mnemonic={mnemonic}"
        df = pd.DataFrame(requests.get(url).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date').rename(columns={'value': col}) / 1e12

    dvp = ofr_vol('REPO-DVP_TV_TOT-P','DVP')
    gcf = ofr_vol('REPO-GCF_TV_TOT-P','GCF')
    tri = ofr_vol('REPO-TRI_TV_TOT-P','TRIPARTY')
    rrp = pdr.DataReader('WLRRAL', 'fred', pd.to_datetime(start), pd.to_datetime(end)) / 1e6
    rrp.index = pd.to_datetime(rrp.index)
    rrp = rrp.rename(columns={'WLRRAL': 'RRP'})
    triparty_rrp = (tri - rrp).rename(columns={'TRIPARTY': 'Triparty-RRP'})
    merge = merge_dfs([dvp, rrp, gcf, triparty_rrp]).dropna()
    roc_6m = merge.resample('ME').last().diff(1)
    if start and end:
        roc_6m = roc_6m[(roc_6m.index >= pd.to_datetime(start)) & (roc_6m.index <= pd.to_datetime(end))]

    fig = go.Figure()
    for col, color in zip(['DVP', 'RRP', 'GCF', 'Triparty-RRP'],
                          ["#f8b62d", "#f8772d", "#2f90c5", "#67cbe7"]):
        fig.add_trace(go.Scatter(x=roc_6m.index, y=roc_6m[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Monthly Change in Volume per Venue",
                     yaxis_title="Dollars (Trillions)",
                     xaxis_title="Date",
                     hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. Volume Invested in MMF ---
def plot_volume_invested_in_mmf(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    mmf = pd.DataFrame(requests.get(base_url+'MMF-MMF_TOT-M').json(), columns=["date", "value"])
    mmf = mmf.set_index(pd.to_datetime(mmf['date']))[['value']].rename(columns={'value': 'MMF_TOTAL'}) / 1e12
    mmf = mmf.loc[(mmf.index >= pd.to_datetime(start)) & (mmf.index <= pd.to_datetime(end))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf.index, y=mmf['MMF_TOTAL'], line=dict(color='#67cbe7')))
    fig.update_layout(title="Volume Invested in MMF",
                     yaxis_title="Trillions",
                     xaxis_title="Date",
                     hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- 6. RRP vs. Foreign RRP ---
def plot_rrp_vs_foreign_rrp(start, end, **kwargs):
    from fredapi import Fred
    fred = Fred(api_key='6905137c26f03db5c8c09f70b7839150')
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    rrp.index = pd.to_datetime(rrp.index)
    rrp = rrp.rename(columns={'WLRRAL': 'RRP'})
    foreign_rrp = pd.DataFrame(fred.get_series('WREPOFOR', observation_start=start, observation_end=end) / 1e6)
    rrp_foreign = merge_dfs([rrp, foreign_rrp])
    rrp_foreign.columns = ['RRP','Foreign_RRP']
    rrp_foreign = rrp_foreign.dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rrp_foreign.index, y=rrp_foreign['RRP'], name='RRP', line=dict(color='#07AFE3')))
    fig.add_trace(go.Scatter(x=rrp_foreign.index, y=rrp_foreign['Foreign_RRP'], name='Foreign RRP', line=dict(color='#F57235')))
    fig.update_layout(title="RRP vs. Foreign RRP", yaxis_title="Trillions", xaxis_title="Date", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- 7. MMF Repo vs Non Repo ---
def plot_mmf_repo_vs_non_repo(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    repo = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_TOT-M').json(), columns=['date','value'])
    repo = repo.set_index(pd.to_datetime(repo['date']))[['value']].rename(columns={'value':'repo'}) / 1e12
    total = pd.DataFrame(requests.get(base_url+'MMF-MMF_TOT-M').json(), columns=['date','value'])
    total = total.set_index(pd.to_datetime(total['date']))[['value']].rename(columns={'value':'total'}) / 1e12
    merge = merge_dfs([repo, total])
    merge['non_repo'] = merge['total'] - merge['repo']
    merge = merge.loc[(merge.index >= pd.to_datetime(start)) & (merge.index <= pd.to_datetime(end))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['non_repo'], name="Non-Repo Allocation", line=dict(color="#f8b62d")))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['repo'], name="Repo Allocation", line=dict(color="#f8772d")))
    fig.update_layout(title="MMF Repo vs Non Repo", yaxis_title="Dollars", xaxis_title="Date", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- 8. Triparty Adjusted for RRP ---
def plot_triparty_adjusted_for_rrp(start, end, **kwargs):
    def ofr_vol(mnemonic, col):
        url = f"https://data.financialresearch.gov/v1/series/timeseries?mnemonic={mnemonic}"
        df = pd.DataFrame(requests.get(url).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date').rename(columns={'value': col}) / 1e12

    tri = ofr_vol('REPO-TRI_TV_TOT-P','TRIPARTY')
    dvp = ofr_vol('REPO-DVP_TV_TOT-P','DVP')
    rrp = pdr.DataReader('WLRRAL', 'fred', pd.to_datetime(start), pd.to_datetime(end)) / 1e6
    rrp.index = pd.to_datetime(rrp.index)
    rrp = rrp.rename(columns={'WLRRAL': 'RRP'})
    triparty_merge = merge_dfs([tri, rrp, dvp])
    triparty_merge['Triparty-RRP'] = triparty_merge['TRIPARTY'] - triparty_merge['RRP']
    triparty_merge['Residual Flows'] = triparty_merge['DVP'] - triparty_merge['Triparty-RRP']
    triparty_merge = triparty_merge.dropna()
    triparty_merge = triparty_merge.loc[(triparty_merge.index >= pd.to_datetime(start)) & (triparty_merge.index <= pd.to_datetime(end))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['Triparty-RRP'], name="Triparty-RRP", line=dict(color="#f8b62d")))
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['DVP'], name="DVP", line=dict(color="#f8772d")))
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['Residual Flows'], name="Residual Flow", line=dict(color="#2f90c5")))
    fig.update_layout(title="Tri-Party Adjusted for RRP",
                     yaxis_title="Trillions",
                     xaxis_title="Date",
                     hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- 9. MMF Allocation by Counterparty ---
def plot_mmf_allocation_by_counterparty(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    fc = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wFFI-M').json(), columns=['date','value'])
    fc = fc.set_index(pd.to_datetime(fc['date']))[['value']].rename(columns={'value':'Foreign'}) / 1e12
    fe = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wFR-M').json(), columns=['date','value'])
    fe = fe.set_index(pd.to_datetime(fe['date']))[['value']].rename(columns={'value':'Fed'}) / 1e12
    usf = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wDFI-M').json(), columns=['date','value'])
    usf = usf.set_index(pd.to_datetime(usf['date']))[['value']].rename(columns={'value':'US_Financial_Institutions'}) / 1e12
    ficc = pd.DataFrame(requests.get(base_url+'MMF-MMF_RP_wFICC-M').json(), columns=['date','value'])
    ficc = ficc.set_index(pd.to_datetime(ficc['date']))[['value']].rename(columns={'value':'FICC'}) / 1e12
    merge = merge_dfs([fc, fe, usf, ficc]).dropna()
    merge = merge.loc[(merge.index >= pd.to_datetime(start)) & (merge.index <= pd.to_datetime(end))]
    fig = go.Figure()
    for col, color in zip(['Foreign','Fed','US_Financial_Institutions','FICC'], ["#f8b62d","#f8772d","#2f90c5","#67cbe7"]):
        fig.add_trace(go.Scatter(x=merge.index, y=merge[col], name=col.replace('_',' '), line=dict(color=color)))
    fig.update_layout(title="Allocation of MMF by Counterparties",
                     yaxis_title="Trillions",
                     xaxis_title="Date",
                     hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
