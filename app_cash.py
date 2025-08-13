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

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------------- TGA -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_tga(start, end, **kwargs):
    tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    tga_volume.index = pd.to_datetime(tga_volume.index)
    tga_volume.columns = ['tga_volume']
    tga_roc = tga_volume.resample('W').last().diff(1)
    tga_roc.columns = ['TGA ROC']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tga_volume.index, y=tga_volume['tga_volume'],
                             name='TGA Volume', line=dict(color='#07AFE3', width=2)))
    fig.update_layout(
        title="TGA",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=tga_roc.index, y=tga_roc['TGA ROC'],
                              name='TGA Weekly ROC', line=dict(color='#07AFE3', width=2)))
    fig2.update_layout(
        title="TGA Weekly Rate of Change",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig2, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------------- RRP -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_rrp(start, end, **kwargs):
    rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    rrp_volume.index = pd.to_datetime(rrp_volume.index)
    rrp_volume.columns = ['rrp_volume']
    rrp_roc = rrp_volume.resample('W').last().diff(1)
    rrp_roc.columns = ['RRP ROC']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rrp_volume.index, y=rrp_volume['rrp_volume'],
                             name='RRP Volume', line=dict(color='#07AFE3', width=2)))
    fig.update_layout(
        title="RRP",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=rrp_roc.index, y=rrp_roc['RRP ROC'],
                              name='RRP Weekly ROC', line=dict(color='#07AFE3', width=2)))
    fig2.update_layout(
        title="RRP Weekly Rate of Change",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig2, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- TOTAL BANKING RESERVES ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_reserves(start, end, **kwargs):
    reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    reserves_volume.index = pd.to_datetime(reserves_volume.index)
    reserves_volume.columns = ['reserves_volume']
    reserves_roc = reserves_volume.resample('W').last().diff(1)
    reserves_roc.columns = ['reserves_roc']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reserves_volume.index, y=reserves_volume['reserves_volume'],
                             name='Reserves', line=dict(color='#07AFE3', width=2)))
    fig.update_layout(
        title="Reserves",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=reserves_roc.index, y=reserves_roc['reserves_roc'],
                              name='Reserves Weekly ROC', line=dict(color='#07AFE3', width=2)))
    fig2.update_layout(
        title="Reserves Weekly Rate of Change",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig2, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ MMF REPO VS NON REPO ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_mmf_repo_vs_non_repo(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

    def ofr_get(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df / 1e12
        return df

    mmf_repo_allocation = ofr_get('MMF-MMF_RP_TOT-M')
    mmf_total_allocation = ofr_get('MMF-MMF_TOT-M')

    mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, mmf_total_allocation])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total']
    mmf_repo_non_repo_merge['non_repo'] = mmf_repo_non_repo_merge['mmf_total'] - mmf_repo_non_repo_merge['mmf_repo']
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_repo_non_repo_merge.index, y=mmf_repo_non_repo_merge['non_repo'],
                             name="Non-Repo Allocation", line=dict(color="#f8b62d", width=2)))
    fig.add_trace(go.Scatter(x=mmf_repo_non_repo_merge.index, y=mmf_repo_non_repo_merge['mmf_repo'],
                             name="Repo Allocation", line=dict(color="#f8772d", width=2)))
    fig.update_layout(
        title="MMF Repo vs Non Repo",
        yaxis_title="Dollars",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ ASSET ALLOCATION MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_asset_allocation_mmf(start, end, **kwargs):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

    def ofr_get(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df / 1e12
        return df

    mmf_repo_total = ofr_get('MMF-MMF_RP_TOT-M')
    mmf_fed_repo = ofr_get('MMF-MMF_RP_wFR-M')

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = mmf_fed_repo_non_repo_merge['mmf_repo_total'] - mmf_fed_repo_non_repo_merge['mmf_fed_repo']
    mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    # Reuse MMF repo/non-repo from previous function for full merge
    mmf_repo_allocation = ofr_get('MMF-MMF_RP_TOT-M')
    mmf_total_allocation = ofr_get('MMF-MMF_TOT-M')
    mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, mmf_total_allocation])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total']
    mmf_repo_non_repo_merge['non_repo'] = mmf_repo_non_repo_merge['mmf_total'] - mmf_repo_non_repo_merge['mmf_repo']
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo_non_repo_merge, mmf_repo_non_repo_merge])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_fed_repo_non_repo_merge.index, y=mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'],
                             name="Non-Fed Repo", line=dict(color="#9DDCF9", width=2)))
    fig.add_trace(go.Scatter(x=mmf_fed_repo_non_repo_merge.index, y=mmf_fed_repo_non_repo_merge['non_repo'],
                             name="Non-Repo Allocation", line=dict(color="#233852", width=2)))
    fig.add_trace(go.Scatter(x=mmf_fed_repo_non_repo_merge.index, y=mmf_fed_repo_non_repo_merge['mmf_repo'],
                             name="Repo Allocation", line=dict(color="#F5B820", width=2)))
    fig.update_layout(
        title="Asset Allocation: MMF vs Repo/Non-Repo",
        yaxis_title="Dollars",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------- RESERVES NON FED REPO + RESERVES + RRP (AGGREGATE) --------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_reserves_non_fed_repo_rrp(start, end, **kwargs):
    # reuse previous results for slower requests
    tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    tga_volume.index = pd.to_datetime(tga_volume.index)
    tga_volume.columns = ['tga_volume']
    rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    rrp_volume.index = pd.to_datetime(rrp_volume.index)
    rrp_volume.columns = ['rrp_volume']
    reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    reserves_volume.index = pd.to_datetime(reserves_volume.index)
    reserves_volume.columns = ['reserves_volume']

    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    def ofr_get(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df / 1e12
        return df
    mmf_repo_total = ofr_get('MMF-MMF_RP_TOT-M')
    mmf_fed_repo = ofr_get('MMF-MMF_RP_wFR-M')

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = mmf_fed_repo_non_repo_merge['mmf_repo_total'] - mmf_fed_repo_non_repo_merge['mmf_fed_repo']
    mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    reserve_liabilities_merge = merge_dfs([
        tga_volume.resample('ME').last(),
        rrp_volume.resample('ME').last(),
        reserves_volume.resample('ME').last(),
        mmf_fed_repo_non_repo_merge.resample('ME').last()
    ]).dropna()
    reserve_liabilities_merge['reserves_non_repo_rrp'] = (
        reserve_liabilities_merge['rrp_volume'] +
        reserve_liabilities_merge['reserves_volume'] +
        reserve_liabilities_merge['mmf_non_fed_repo']
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reserve_liabilities_merge.index, y=reserve_liabilities_merge['reserves_non_repo_rrp'],
                             name="Non Fed Repo + Reserves + RRP", line=dict(color="#9DDCF9", width=2)))
    fig.update_layout(
        title="Non Fed Repo + Reserves + RRP",
        yaxis_title="Dollars",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- RESERVES LIABILITIES OF THE SYSTEM ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_reserves_liabilities_system(start, end, **kwargs):
    # reuse results from previous function for performance
    tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    tga_volume.index = pd.to_datetime(tga_volume.index)
    tga_volume.columns = ['tga_volume']
    rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    rrp_volume.index = pd.to_datetime(rrp_volume.index)
    rrp_volume.columns = ['rrp_volume']
    reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    reserves_volume.index = pd.to_datetime(reserves_volume.index)
    reserves_volume.columns = ['reserves_volume']

    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    def ofr_get(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df / 1e12
        return df
    mmf_repo_total = ofr_get('MMF-MMF_RP_TOT-M')
    mmf_fed_repo = ofr_get('MMF-MMF_RP_wFR-M')

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = mmf_fed_repo_non_repo_merge['mmf_repo_total'] - mmf_fed_repo_non_repo_merge['mmf_fed_repo']
    mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    reserve_liabilities_merge = merge_dfs([
        tga_volume.resample('ME').last(),
        rrp_volume.resample('ME').last(),
        reserves_volume.resample('ME').last(),
        mmf_fed_repo_non_repo_merge.resample('ME').last()
    ]).dropna()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reserve_liabilities_merge.index, y=reserve_liabilities_merge['mmf_non_fed_repo'],
                             name="Non-Fed Repo", line=dict(color="#9DDCF9", width=2)))
    fig.add_trace(go.Scatter(x=reserve_liabilities_merge.index, y=reserve_liabilities_merge['tga_volume'],
                             name="TGA", line=dict(color="#233852", width=2)))
    fig.add_trace(go.Scatter(x=reserve_liabilities_merge.index, y=reserve_liabilities_merge['reserves_volume'],
                             name="Reserves", line=dict(color="#F5B820", width=2)))
    fig.add_trace(go.Scatter(x=reserve_liabilities_merge.index, y=reserve_liabilities_merge['rrp_volume'],
                             name="RRP", line=dict(color="#E69B93", width=2)))
    fig.update_layout(
        title="Reserves Liabilities of the System",
        yaxis_title="Dollars",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)
