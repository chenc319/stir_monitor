### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- REPO --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left,
                                                  right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'),array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------- PROXY OF PERCENT WITHOUT CENTRAL CLEARING -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_proxy_percent_without_clearing(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'pd_total_repo.pkl', 'rb') as file:
        pd_total_repo = pickle.load(file)
    with open(Path(DATA_DIR) / 'pd_nccbr_repo_on.pkl', 'rb') as file:
        pd_nccbr_repo_on = pickle.load(file)
    with open(Path(DATA_DIR) / 'pd_nccbr_repo_terml30.pkl', 'rb') as file:
        pd_nccbr_repo_terml30 = pickle.load(file)
    with open(Path(DATA_DIR) / 'pd_nccbr_repo_termg30.pkl', 'rb') as file:
        pd_nccbr_repo_termg30 = pickle.load(file)

    pd_nccbr_proxy_merge = merge_dfs([pd_total_repo,
                                      pd_nccbr_repo_on,
                                      pd_nccbr_repo_terml30,
                                      pd_nccbr_repo_termg30])
    pd_nccbr_proxy_merge['pd_nccbr_total'] = (pd_nccbr_proxy_merge['pd_nccbr_on'] +
                                              pd_nccbr_proxy_merge['pd_nccbr_l30'] +
                                              pd_nccbr_proxy_merge['pd_nccbr_g30'])
    pd_nccbr_proxy_merge['nccbr_pct'] = (pd_nccbr_proxy_merge['pd_nccbr_total'] /
                                         pd_nccbr_proxy_merge['pd_total_repo'])
    pd_nccbr_proxy_merge = pd_nccbr_proxy_merge.dropna()

    ### OFR DATA PULLS ###
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'rb') as file:
        gcf_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)

    rrp_volume.columns = ['rrp']
    repo_total_merge = merge_dfs(
        [gcf_volume_df,
         dvp_volume_df,
         tri_volume_df,
         pd.DataFrame(pd_nccbr_proxy_merge['pd_nccbr_total'])]).dropna()
    total_repo_volume = pd.DataFrame(repo_total_merge.sum(axis=1))
    total_repo_volume.columns = ['Repo']

    black_proxy = merge_dfs([tri_volume_df, rrp_volume, dvp_volume_df, gcf_volume_df, total_repo_volume])
    black_proxy.columns = ['tri', 'rrp', 'dvp', 'gcf', 'all_repo']
    black_proxy = black_proxy.resample('W').last().dropna()
    black_proxy['black'] = (black_proxy['tri'] -
                            black_proxy['rrp']) / (black_proxy['all_repo'] - black_proxy['rrp'])

    nccbr_proxy_merge = merge_dfs([pd_nccbr_proxy_merge['nccbr_pct'], black_proxy['black']])
    nccbr_proxy_merge['black'] = nccbr_proxy_merge['black'].ffill()
    nccbr_proxy_merge = nccbr_proxy_merge.dropna()

    nccbr_proxy_merge = nccbr_proxy_merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(nccbr_proxy_merge.index, nccbr_proxy_merge['nccbr_pct'] * 100,
    #          label="(% of NCCBR of Primary Dealers)", color="#f8b62d", lw=2)
    # plt.plot(nccbr_proxy_merge.index, nccbr_proxy_merge['black'] * 100,
    #          label="Tri Party-RRP / (Tri Party+DVP+GCF-RRP)", color="#f8772d", lw=2)
    # plt.title("Proxy of % of Non Cleared Repos", fontsize=22, fontweight="bold")
    # plt.ylabel("%")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.18), ncol=1)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nccbr_proxy_merge.index,
        y=nccbr_proxy_merge['nccbr_pct']*100,
        mode='lines+markers',
        name='% of NCCBR of Primary Dealers',
        line=dict(color='#29B6D9', width=2)))
    fig.add_trace(go.Scatter(
        x=nccbr_proxy_merge.index,
        y=nccbr_proxy_merge['black']*100,
        mode='lines+markers',
        name='Tri Party-RRP / (Tri Party+DVP+GCF-RRP)',
        line=dict(color='#272f37', width=2)))
    fig.update_layout(
        title="Proxy of % of Non Cleared Repos",
        yaxis_title="%",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- VOLUME PER VENUE --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_volume_per_venue(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'rb') as file:
        gcf_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)

    rrp_volume.columns = ['rrp']
    triparty_rrp_merge = merge_dfs([tri_volume_df, rrp_volume]).dropna()
    triparty_rrp_diff = pd.DataFrame(triparty_rrp_merge.iloc[:, 0] - triparty_rrp_merge.iloc[:, 1])
    triparty_rrp_diff.columns = ['Triparty-RRP']
    volume_venue_merge_df = merge_dfs([dvp_volume_df,
                                       rrp_volume,
                                       gcf_volume_df,
                                       triparty_rrp_diff]).loc[str(start):str(end)].dropna()
    volume_venue_merge_df.columns = ['DVP', 'RRP', 'GCF', 'Triparty-RRP']

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['DVP'],
    #          label="DVP", color="#f8b62d", lw=2)
    # plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['RRP'],
    #          label="RRP", color="#f8772d", lw=2)
    # plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['GCF'],
    #          label="GCF", color="#2f90c5", lw=2)
    # plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['Triparty-RRP'],
    #          label="Triparty-RRP", color="#67cbe7", lw=2)
    # plt.title("Volume per Venue", fontsize=22, fontweight="bold")
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col, color in zip(volume_venue_merge_df.columns,
                          ['#f8b62d', '#f8772d', '#2f90c5', '#67cbe7']):
        fig.add_trace(go.Scatter(x=volume_venue_merge_df.index, y=volume_venue_merge_df[col],
                                 mode='lines+markers', name=col, line=dict(color=color)))
    fig.update_layout(
        title="Volume per Venue",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- INVESTMENT OF MMF BY ASSET ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_mmf_by_asset(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_total.pkl', 'rb') as file:
        mmf_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_us_ts.pkl', 'rb') as file:
        mmf_us_ts = pickle.load(file)

    mmf_repo_non_repo_merge = merge_dfs([mmf_repo, mmf_total, mmf_us_ts])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total', 'mmf_us_treasury_sec']
    mmf_repo_non_repo_merge['non_repo'] = (mmf_repo_non_repo_merge['mmf_total'] -
                                           mmf_repo_non_repo_merge['mmf_repo'])
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge.loc[str(start):str(end)]
    mmf_repo_non_repo_merge['US_Repo_Allocation'] = (mmf_repo_non_repo_merge['mmf_repo'] /
                                                     mmf_repo_non_repo_merge['mmf_total'])
    mmf_repo_non_repo_merge['US_TS_Allocation'] = mmf_repo_non_repo_merge['mmf_us_treasury_sec'] / \
                                                  mmf_repo_non_repo_merge['mmf_total']
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge.dropna()

    # ### PLOT ###
    # plt.figure(figsize=(8, 6))
    # plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['US_TS_Allocation'],
    #          label='U.S. Treasury Sec.', color='#29B6D9', lw=2)
    # plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['US_Repo_Allocation'],
    #          label='U.S. Treasury Repo', color='#272f37', lw=2)
    # plt.title('Investment of MMF by Asset', fontsize=18, fontweight='bold', pad=18)
    # plt.ylabel('% Allocation')
    # plt.yticks(fontsize=11)
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(alpha=0.3)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mmf_repo_non_repo_merge.index,
        y=mmf_repo_non_repo_merge['US_TS_Allocation'],
        mode='lines+markers', name='U.S. Treasury Sec.', line=dict(color='#29B6D9', width=2)))
    fig.add_trace(go.Scatter(
        x=mmf_repo_non_repo_merge.index,
        y=mmf_repo_non_repo_merge['US_Repo_Allocation'],
        mode='lines+markers', name='U.S. Treasury Repo', line=dict(color='#272f37', width=2)))
    fig.update_layout(
        title="Investment of MMF by Asset",
        yaxis_title="% Allocation",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- 6M VOLUME CHANGE --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_6m_volume_change(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'rb') as file:
        gcf_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)

    triparty_rrp_merge = merge_dfs([tri_volume_df, rrp_volume]).dropna()
    triparty_rrp_diff = pd.DataFrame(triparty_rrp_merge.iloc[:, 0] - triparty_rrp_merge.iloc[:, 1])
    triparty_rrp_diff.columns = ['Triparty-RRP']

    volume_venue_merge_df = merge_dfs([dvp_volume_df,
                                       rrp_volume,
                                       gcf_volume_df,
                                       triparty_rrp_diff]).loc[str(start):str(end)].dropna()
    volume_venue_merge_df.columns = ['DVP', 'RRP', 'GCF', 'Triparty-RRP']

    roc_6m_volume = volume_venue_merge_df.resample('ME').last().diff(1)
    roc_6m_volume = roc_6m_volume.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(roc_6m_volume.index, roc_6m_volume['DVP'],
    #          label="DVP", color="#f8b62d", lw=2)
    # plt.plot(roc_6m_volume.index, roc_6m_volume['RRP'],
    #          label="RRP", color="#f8772d", lw=2)
    # plt.plot(roc_6m_volume.index, roc_6m_volume['GCF'],
    #          label="GCF", color="#2f90c5", lw=2)
    # plt.plot(roc_6m_volume.index, roc_6m_volume['Triparty-RRP'],
    #          label="Triparty-RRP", color="#67cbe7", lw=2)
    # plt.title("Monthly Change in Volume per Venue", fontsize=22, fontweight="bold")
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col, color in zip(roc_6m_volume.columns, ['#f8b62d', '#f8772d', '#2f90c5', '#67cbe7']):
        fig.add_trace(go.Scatter(x=roc_6m_volume.index, y=roc_6m_volume[col],
                                 mode='lines+markers', name=col, line=dict(color=color)))
    fig.update_layout(
        title="Monthly Change in Volume per Venue",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- VOLUME INVESTED IN MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_volume_invested_in_mmf(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_all_volume.pkl', 'rb') as file:
        mmf_all_volume = pickle.load(file)

    mmf = mmf_all_volume.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(mmf.index, mmf['MMF_TOTAL'],
    #          color="#67cbe7", lw=2)
    # plt.title("Volume Invested in MMF", fontsize=22, fontweight="bold")
    # plt.ylabel("Trillions")
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mmf.index, y=mmf['MMF_TOTAL'],
        mode='lines+markers', line=dict(color="#67cbe7", width=2)))
    fig.update_layout(
        title="Volume Invested in MMF",
        yaxis_title="Trillions",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)


### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- RRP AND FOREIGN RRP -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_rrp_vs_foreign_rrp(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'foreign_rrp.pkl', 'rb') as file:
        foreign_rrp = pickle.load(file)

    rrp_volume.index = pd.to_datetime(rrp_volume.index)
    foreign_rrp.index = pd.to_datetime(foreign_rrp.index)
    merge = merge_dfs([rrp_volume, foreign_rrp]).dropna()
    merge.columns = ['RRP', 'Foreign_RRP']
    merge = merge.loc[str(start):str(end)]

    # ### PLOT DATA ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(merge.index, merge['RRP'],
    #          label="RRP", color="#07AFE3", lw=2)
    # plt.plot(merge.index, merge['Foreign_RRP'],
    #          label="Foreign RRP", color="#F57235", lw=2)
    # plt.title("RRP vs. Foreign RRP", fontsize=22, fontweight="bold")
    # plt.ylabel("%")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['RRP'],
                             mode='lines+markers', name="RRP", line=dict(color="#07AFE3", width=2)))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['Foreign_RRP'],
                             mode='lines+markers', name="Foreign RRP", line=dict(color="#F57235", width=2)))
    fig.update_layout(
        title="RRP vs. Foreign RRP",
        yaxis_title="Trillions",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- MMF REPO VS NON REPO ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_mmf_repo_vs_non_repo(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_total.pkl', 'rb') as file:
        mmf_total = pickle.load(file)

    mmf_repo_non_repo_merge = merge_dfs([mmf_repo, mmf_total])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total']
    mmf_repo_non_repo_merge['non_repo'] = mmf_repo_non_repo_merge['mmf_total'] - mmf_repo_non_repo_merge['mmf_repo']
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['non_repo'],
    #          label="Non-Repo Allocation", color="#f8b62d", lw=2)
    # plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['mmf_repo'],
    #          label="Repo Allocation", color="#f8772d", lw=2)
    #
    # plt.title("MMF Repo vs Nono Repo", fontsize=22, fontweight="bold")
    # plt.ylabel('Dollars')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_repo_non_repo_merge.index, y=mmf_repo_non_repo_merge['non_repo'],
                             mode='lines+markers', name="Non-Repo Allocation", line=dict(color="#f8b62d", width=2)))
    fig.add_trace(go.Scatter(x=mmf_repo_non_repo_merge.index, y=mmf_repo_non_repo_merge['mmf_repo'],
                             mode='lines+markers', name="Repo Allocation", line=dict(color="#f8772d", width=2)))
    fig.update_layout(
        title="MMF Repo vs Non Repo",
        yaxis_title="Dollars",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- TRIPARTY ADJUSTED FOR RRP ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_triparty_adjusted_for_rrp(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)

    triparty_merge = merge_dfs([tri_volume_df, rrp_volume, dvp_volume_df])
    triparty_merge.columns = ['tri', 'rrp', 'dvp']
    triparty_merge['triparty-rrp'] = triparty_merge['tri'] - triparty_merge['rrp']
    triparty_merge['residual_flows'] = triparty_merge['dvp'] - triparty_merge['triparty-rrp']
    triparty_merge = triparty_merge.loc[str(start):str(end)].dropna()

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(triparty_merge.index, triparty_merge['triparty-rrp'],
    #          label="Triparty-RRP", color="#f8b62d", lw=2)
    # plt.plot(triparty_merge.index, triparty_merge['dvp'],
    #          label="DVP", color="#f8772d", lw=2)
    # plt.plot(triparty_merge.index, triparty_merge['residual_flows'],
    #          label="Residual Flow", color="#2f90c5", lw=2)
    # plt.title("Tri-Party Adjusted for RRP", fontsize=22, fontweight="bold")
    # plt.ylabel("Trillions")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['triparty-rrp'],
                             mode='lines+markers', name="Triparty-RRP", line=dict(color="#f8b62d", width=2)))
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['dvp'],
                             mode='lines+markers', name="DVP", line=dict(color="#f8772d", width=2)))
    fig.add_trace(go.Scatter(x=triparty_merge.index, y=triparty_merge['residual_flows'],
                             mode='lines+markers', name="Residual Flow", line=dict(color="#2f90c5", width=2)))
    fig.update_layout(
        title="Tri-Party Adjusted for RRP",
        yaxis_title="Trillions",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ MMF ALLOCATION BY COUNTERPARTY -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_mmf_allocation_by_counterparty(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_foreign.pkl', 'rb') as file:
        mmf_foreign = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_fed.pkl', 'rb') as file:
        mmf_fed = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_us_inst.pkl', 'rb') as file:
        mmf_us_inst = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_ficc.pkl', 'rb') as file:
        mmf_ficc = pickle.load(file)

    mmf_allocations_merge = merge_dfs([mmf_foreign,
                                       mmf_fed,
                                       mmf_us_inst,
                                       mmf_ficc]).loc[str(start):str(end)].dropna()
    mmf_allocations_merge.columns = ['foreign', 'fed', 'us_inst', 'ficc']

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['foreign'],
    #          label="Foreign", color="#f8b62d", lw=2)
    # plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['fed'],
    #          label="Fed", color="#f8772d", lw=2)
    # plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['us_inst'],
    #          label="US Financial Institutions", color="#2f90c5", lw=2)
    # plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['ficc'],
    #          label="FICC", color="#67cbe7", lw=2)
    # plt.title("Allocation of MMF by Counterparties", fontsize=22, fontweight="bold")
    # plt.ylabel("Trillions")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col, color in zip(mmf_allocations_merge.columns,
                          ['#f8b62d', '#f8772d', '#2f90c5', '#67cbe7']):
        fig.add_trace(go.Scatter(x=mmf_allocations_merge.index, y=mmf_allocations_merge[col],
                                 mode='lines+markers', name=col.replace("_", " ").title(), line=dict(color=color)))
    fig.update_layout(
        title="Allocation of MMF by Counterparties",
        yaxis_title="Trillions",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
