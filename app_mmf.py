### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- MMF --------------------------------------------------- ###
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
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

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
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------- MMF INVOLVEMENT IN TREASURY SECURITIES --------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_mmf_repo(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_repo_allocations.pkl', 'rb') as file:
        mmf_repo_allocations = pickle.load(file)

    mmf_repo_allocations = mmf_repo_allocations[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(mmf_repo_allocations.index, mmf_repo_allocations['Other Repo'],
    #          label='Other Repo', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(mmf_repo_allocations.index, mmf_repo_allocations['Agency Repo'],
    #          label='Agency Repo', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(mmf_repo_allocations.index, mmf_repo_allocations['Treasury Repo'],
    #          label='Treasury Repo', color='#233852', lw=2)  # dark blue
    # plt.ylabel("$ (Trillions)")
    # plt.title("MMF's Investments in Repo Markets", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_repo_allocations.index,
                             y=mmf_repo_allocations['Other Repo'],
                             mode='lines+markers',
                             name='Other Repo',
                             line=dict(color="#46b5ca", width=3)))
    fig.add_trace(go.Scatter(x=mmf_repo_allocations.index,
                             y=mmf_repo_allocations['Agency Repo'],
                             mode='lines+markers',
                             name='Agency Repo',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=mmf_repo_allocations.index,
                             y=mmf_repo_allocations['Treasury Repo'],
                             mode='lines+markers',
                             name='Treasury Repo',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="MMF's Investments in Repo Markets",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------- MONEY MARKET FUNDS INVOLVEMENTS IN ON REPO SPECIFICALLY TO CAPTURE STIR ACTIVITY ----------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_mmf_on_repo(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_involvement_on_repo.pkl', 'rb') as file:
        mmf_involvement_on_repo = pickle.load(file)

    mmf_involvement_on_repo = mmf_involvement_on_repo[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(mmf_involvement_on_repo.index, mmf_involvement_on_repo['Values'],
    #          color='#9DDCF9', lw=2)  # light blue
    # plt.ylabel("$ (Trillions)")
    # plt.title("MMF's Investments in Overnight/Open Repo", fontsize=17, fontweight="bold")
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_involvement_on_repo.index,
                             y=mmf_involvement_on_repo['Values'],
                             mode='lines+markers',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="MMF's Investments in Overnight/Open Repo",
        yaxis_title="Dollars",
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
                                                     mmf_repo_non_repo_merge['mmf_total']) * 100
    mmf_repo_non_repo_merge['US_TS_Allocation'] = (mmf_repo_non_repo_merge['mmf_us_treasury_sec'] / \
                                                  mmf_repo_non_repo_merge['mmf_total']) * 100
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
        yaxis_title="%",
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
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ ASSET ALLOCATION MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_asset_allocation_mmf(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_fed.pkl', 'rb') as file:
        mmf_fed_repo = pickle.load(file)

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = (mmf_fed_repo_non_repo_merge['mmf_repo_total'] -
                                                       mmf_fed_repo_non_repo_merge['mmf_fed_repo'])
    mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge[str(start):str(end)].dropna()

    # Reuse MMF repo/non-repo from previous function for full merge
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_allocation = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_total.pkl', 'rb') as file:
        mmf_total_allocation = pickle.load(file)
    mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, mmf_total_allocation])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total']
    mmf_repo_non_repo_merge['non_repo'] = (mmf_repo_non_repo_merge['mmf_total'] -
                                           mmf_repo_non_repo_merge['mmf_repo'])
    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo_non_repo_merge, mmf_repo_non_repo_merge])[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(mmf_fed_repo_non_repo_merge.index, mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'],
    #          label="Non-Fed Repo", color="#9DDCF9", lw=2)
    # plt.plot(mmf_fed_repo_non_repo_merge.index, mmf_fed_repo_non_repo_merge['non_repo'],
    #          label="Non-Repo Allocation", color="#233852", lw=2)
    # plt.plot(mmf_fed_repo_non_repo_merge.index, mmf_fed_repo_non_repo_merge['mmf_repo'],
    #          label="Repo Allocation", color="#F5B820", lw=2)
    # plt.title("MMF Repo vs Nono Repo", fontsize=22, fontweight="bold")
    # plt.ylabel('Dollars')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_fed_repo_non_repo_merge.index,
                             y=mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'],
                             name="Non-Fed Repo", line=dict(color="#9DDCF9", width=2)))
    fig.add_trace(go.Scatter(x=mmf_fed_repo_non_repo_merge.index,
                             y=mmf_fed_repo_non_repo_merge['non_repo'],
                             name="Non-Repo Allocation", line=dict(color="#233852", width=2)))
    fig.add_trace(go.Scatter(x=mmf_fed_repo_non_repo_merge.index,
                             y=mmf_fed_repo_non_repo_merge['mmf_repo'],
                             name="Repo Allocation", line=dict(color="#F5B820", width=2)))
    fig.update_layout(
        title="Asset Allocation: MMF vs Repo/Non-Repo",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)