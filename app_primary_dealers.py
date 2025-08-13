import pandas as pd
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go

def merge_dfs(array_of_dfs):
    """Merge a list of DataFrames on index (outer join)."""
    if not array_of_dfs:
        return pd.DataFrame()
    return ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ SPONSORED VOLUMES - THE SOLUTION? ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sponsored_volumes_solution(start, end, path_to_csv="data/SponsoredVolume.csv", **kwargs):
    sponsored_volume = pd.read_csv(path_to_csv).dropna()
    sponsored_volume = sponsored_volume.iloc[::-1].reset_index(drop=True)
    sponsored_volume.index = pd.to_datetime(sponsored_volume['BUSINESS_DATE'].values)
    sponsored_volume = sponsored_volume.drop('BUSINESS_DATE', axis=1)
    sponsored_volume['DVP_TOTAL_AMOUNT'] = (
        sponsored_volume['DVP_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
    sponsored_volume['GC_TOTAL_AMOUNT'] = (
        sponsored_volume['GC_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
    sponsored_volume = sponsored_volume.sort_index()
    sponsored_volume = sponsored_volume.loc[str(start):str(end)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sponsored_volume.index, y=sponsored_volume['DVP_TOTAL_AMOUNT'], name='DVP Sponsored',
                             line=dict(color='#4CD0E9', width=2)))
    fig.add_trace(go.Scatter(x=sponsored_volume.index, y=sponsored_volume['GC_TOTAL_AMOUNT'], name='GC Sponsored',
                             line=dict(color='#233852', width=2)))
    fig.update_layout(
        title="Sponsored Volumes - The Solutions?",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SPONSORED VOLUMES -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sponsored_volumes(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/hf/v1/series/full?mnemonic='

    repo_json = requests.get(base_url + 'FICC-SPONSORED_REPO_VOL').json()
    repo_vol = pd.DataFrame(repo_json['FICC-SPONSORED_REPO_VOL']['timeseries']['aggregation'], columns=["date", "Value"])
    repo_vol['date'] = pd.to_datetime(repo_vol['date'])
    repo_vol.set_index('date', inplace=True)
    repo_vol = repo_vol.sort_index().loc[str(start):str(end)]

    rrp_json = requests.get(base_url + 'FICC-SPONSORED_REVREPO_VOL').json()
    rrp_vol = pd.DataFrame(rrp_json['FICC-SPONSORED_REVREPO_VOL']['timeseries']['aggregation'], columns=["date", "Value"])
    rrp_vol['date'] = pd.to_datetime(rrp_vol['date'])
    rrp_vol.set_index('date', inplace=True)
    rrp_vol = rrp_vol.sort_index().loc[str(start):str(end)]

    merge = merge_dfs([repo_vol, rrp_vol])
    merge.columns = ['sponsored_repo', 'sponsored_rrp']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['sponsored_repo'], name='Repo Sponsored',
                             line=dict(color='#4CD0E9', width=2)))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['sponsored_rrp'], name='RRP Sponsored',
                             line=dict(color='#233852', width=2)))
    fig.update_layout(
        title="Sponsored Volumes",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------ % OF DVP VOLUME THAT IS SPONSORED ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_pct_dvp_sponsored(start, end, path_to_csv="data/SponsoredVolume.csv", **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    dvp_volume = pd.DataFrame(requests.get(base_url + 'REPO-DVP_TV_TOT-P').json(), columns=["date", "value"])
    dvp_volume['date'] = pd.to_datetime(dvp_volume['date'])
    dvp_volume.set_index('date', inplace=True)
    dvp_volume = dvp_volume.sort_index().loc[str(start):str(end)]

    sponsored_volume = pd.read_csv(path_to_csv).dropna()
    sponsored_volume = sponsored_volume.iloc[::-1].reset_index(drop=True)
    sponsored_volume.index = pd.to_datetime(sponsored_volume['BUSINESS_DATE'].values)
    sponsored_volume = sponsored_volume.drop('BUSINESS_DATE', axis=1)
    sponsored_volume['DVP_TOTAL_AMOUNT'] = (
        sponsored_volume['DVP_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
    sponsored_volume = sponsored_volume.sort_index().loc[str(start):str(end)]
    dvp_sponsored_vol = pd.DataFrame(sponsored_volume['DVP_TOTAL_AMOUNT'])

    merge = merge_dfs([dvp_sponsored_vol, dvp_volume]).dropna()
    merge.columns = ['dvp_sponsored', 'total_dvp']
    merge['pct'] = merge['dvp_sponsored'] / merge['total_dvp']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['pct'] * 100,
                             name="% of DVP that is Sponsored", line=dict(color='#4CD0E9', width=2)))
    fig.update_layout(
        title="% of DVP that is Sponsored",
        yaxis_title="Percent",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------- PRIMARY DEALERS NET POSITIONS: BILLS VS BONDS, BOND TENORS, TENOR CHANGE ----------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_positions_bills_vs_bonds(start, end, **kwargs):
    urls = [
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-B.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21.json'
    ]
    names = ['bills','l2','g2l3','g3l6','g6l7','g7l11','g11l21','g21']
    all_pd = pd.DataFrame()
    for idx in range(len(urls)):
        pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
        pos['value'] = pd.to_numeric(pos['value'], errors='coerce') / 1e3
        pos.dropna(subset=['value'], inplace=True)
        pos['asofdate'] = pd.to_datetime(pos['asofdate'])
        pos.set_index('asofdate', inplace=True)
        pos = pos[['value']]
        pos.columns = [names[idx]]
        pos = pos.sort_index()
        all_pd = merge_dfs([all_pd, pos])
    all_pd = all_pd.sort_index().loc[str(start):str(end)]
    all_pd['net_nominal_bonds'] = (
        all_pd['l2'] + all_pd['g2l3'] + all_pd['g3l6'] + all_pd['g6l7'] + all_pd['g7l11']
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=all_pd.index, y=all_pd['bills'], name="Bills",
                             line=dict(color='#43c4e6', width=2)))
    fig.add_trace(go.Scatter(x=all_pd.index, y=all_pd['net_nominal_bonds'], name="Net Nominal Bonds",
                             line=dict(color='#262e39', width=2)))
    fig.update_layout(
        title="Primary Dealers Net Positions Bills VS Bonds",
        yaxis_title="Billions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_net_positions_by_bond_tenor(start, end, **kwargs):
    urls = [
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-B.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21.json'
    ]
    names = ['bills','l2','g2l3','g3l6','g6l7','g7l11','g11l21','g21']
    all_pd = pd.DataFrame()
    for idx in range(len(urls)):
        pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
        pos['value'] = pd.to_numeric(pos['value'], errors='coerce') / 1e3
        pos.dropna(subset=['value'], inplace=True)
        pos['asofdate'] = pd.to_datetime(pos['asofdate'])
        pos.set_index('asofdate', inplace=True)
        pos = pos[['value']]
        pos.columns = [names[idx]]
        pos = pos.sort_index()
        all_pd = merge_dfs([all_pd, pos])
    all_pd = all_pd.sort_index().loc[str(start):str(end)]

    fig = go.Figure()
    tenors = [
        ('l2', 'Bond <2Y', '#9DDCF9'),
        ('g2l3', 'Bond 2-3Y', '#4CD0E9'),
        ('g3l6', 'Bond 3-6Y', '#233852'),
        ('g6l7', 'Bond 6-7Y', '#F5B820'),
        ('g7l11', 'Bond 7-10Y', '#E69B93'),
    ]
    for k, name, color in tenors:
        fig.add_trace(go.Scatter(x=all_pd.index, y=all_pd[k], name=name, line=dict(color=color, width=2)))
    fig.update_layout(
        title="Primary Dealers Net Positions By Bond Tenor",
        yaxis_title="Billions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_net_change_by_bond_tenor(start, end, **kwargs):
    urls = [
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-BC.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21C.json'
    ]
    names = ['bills','l2','g2l3','g3l6','g6l7','g7l11','g11l21','g21']
    all_pd_change = pd.DataFrame()
    for idx in range(len(urls)):
        pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
        pos['value'] = pd.to_numeric(pos['value'], errors='coerce')
        pos.dropna(subset=['value'], inplace=True)
        pos['asofdate'] = pd.to_datetime(pos['asofdate'])
        pos.set_index('asofdate', inplace=True)
        pos = pos[['value']]
        pos.columns = [names[idx]]
        pos = pos.sort_index()
        all_pd_change = merge_dfs([all_pd_change, pos])
    all_pd_change = all_pd_change.sort_index().loc[str(start):str(end)].dropna()

    fig = go.Figure()
    tenors = [
        ('l2', 'Bond <2Y', '#9DDCF9'),
        ('g2l3', 'Bond 2-3Y', '#4CD0E9'),
        ('g3l6', 'Bond 3-6Y', '#233852'),
        ('g6l7', 'Bond 6-7Y', '#F5B820'),
        ('g7l11', 'Bond 7-10Y', '#E69B93'),
    ]
    for k, name, color in tenors:
        fig.add_trace(go.Scatter(x=all_pd_change.index, y=all_pd_change[k], name=name, line=dict(color=color, width=2)))
    fig.update_layout(
        title="Primary Dealers Net Position Change By Bond Tenor",
        yaxis_title="Billions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)
