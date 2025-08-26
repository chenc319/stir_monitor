### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- CASH -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import requests
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
### --------------------------------------------------- TGA -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_tga(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'tga.pkl', 'rb') as file:
        tga_volume = pickle.load(file)
    tga_volume.columns = ['tga_volume']
    tga_roc = tga_volume.resample('W').last().diff(1)
    tga_roc.columns = ['TGA ROC']

    # ### PLOT ###
    # plt.figure(figsize=(7, 6))
    # plt.plot(tga_volume.index, tga_volume['tga_volume'],
    #          label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
    # plt.title('TGA', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()
    #
    # plt.figure(figsize=(7, 6))
    # plt.plot(tga_roc.index, tga_roc['TGA ROC'],
    #          label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
    # plt.title('TGA', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)
    rrp_volume.columns = ['rrp_volume']
    rrp_roc = rrp_volume.resample('W').last().diff(1)
    rrp_roc.columns = ['RRP ROC']

    # ### PLOT ###
    # plt.figure(figsize=(7, 6))
    # plt.plot(rrp_volume.index, rrp_volume['rrp_volume'],
    #          label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
    # plt.title('TGA', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()
    #
    # plt.figure(figsize=(7, 6))
    # plt.plot(rrp_roc.index, rrp_roc['RRP ROC'],
    #          label='RRP Weekly ROC', color='#07AFE3', linewidth=2)
    # plt.title('RRP', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
    with open(Path(DATA_DIR) / 'reserves.pkl', 'rb') as file:
        reserves_volume = pickle.load(file)
    reserves_volume.index = pd.to_datetime(reserves_volume.index)
    reserves_volume.columns = ['reserves_volume']
    reserves_roc = reserves_volume.resample('W').last().diff(1)
    reserves_roc.columns = ['reserves_roc']

    # ### PLOT ###
    # plt.figure(figsize=(7, 6))
    # plt.plot(reserves_volume.index, reserves_volume['reserves_volume'],
    #          label='Reserves', color='#07AFE3', linewidth=2)
    # plt.title('Reserves', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()
    #
    # plt.figure(figsize=(7, 6))
    # plt.plot(reserves_roc.index, reserves_roc['reserves_roc'],
    #          label='Reserves Weekly ROC', color='#07AFE3', linewidth=2)
    # plt.title('Reserves', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_allocation = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_total.pkl', 'rb') as file:
        mmf_total_allocation = pickle.load(file)

    mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, mmf_total_allocation])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total']
    mmf_repo_non_repo_merge['non_repo'] = (mmf_repo_non_repo_merge['mmf_total'] -
                                           mmf_repo_non_repo_merge['mmf_repo'])
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge['2019-01-01':str(end)].dropna()

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
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_fed.pkl', 'rb') as file:
        mmf_fed_repo = pickle.load(file)

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = (mmf_fed_repo_non_repo_merge['mmf_repo_total'] -
                                                       mmf_fed_repo_non_repo_merge['mmf_fed_repo'])
    mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    # Reuse MMF repo/non-repo from previous function for full merge
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_allocation = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_total.pkl', 'rb') as file:
        mmf_total_allocation = pickle.load(file)
    mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, mmf_total_allocation])
    mmf_repo_non_repo_merge.columns = ['mmf_repo', 'mmf_total']
    mmf_repo_non_repo_merge['non_repo'] = (mmf_repo_non_repo_merge['mmf_total'] -
                                           mmf_repo_non_repo_merge['mmf_repo'])
    mmf_repo_non_repo_merge = mmf_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo_non_repo_merge, mmf_repo_non_repo_merge])

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
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------- RESERVES NON FED REPO + RESERRVES + RRP -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_reserves_non_fed_repo_rrp(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'tga.pkl', 'rb') as file:
        tga_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'reserves.pkl', 'rb') as file:
        reserves_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)
    tga_volume.index = pd.to_datetime(tga_volume.index)
    tga_volume.columns = ['tga_volume']
    rrp_volume.index = pd.to_datetime(rrp_volume.index)
    rrp_volume.columns = ['rrp_volume']
    reserves_volume.index = pd.to_datetime(reserves_volume.index)
    reserves_volume.columns = ['reserves_volume']

    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_fed.pkl', 'rb') as file:
        mmf_fed_repo = pickle.load(file)

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = (mmf_fed_repo_non_repo_merge['mmf_repo_total'] -
                                                       mmf_fed_repo_non_repo_merge['mmf_fed_repo'])
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

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['reserves_non_repo_rrp'],
    #          color="#9DDCF9", lw=2)
    # plt.title("Non Fed Repo + Reserves + RRP", fontsize=22, fontweight="bold")
    # plt.ylabel('Dollars')
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reserve_liabilities_merge.index,
                             y=reserve_liabilities_merge['reserves_non_repo_rrp'],
                             name="Non Fed Repo + Reserves + RRP", line=dict(color="#9DDCF9", width=2)))
    fig.update_layout(
        title="Non Fed Repo + Reserves + RRP",
        yaxis_title="Dollars",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- RESERVES LIABILITIES OF THE SYSTEM ----------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_reserves_liabilities_system(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'tga.pkl', 'rb') as file:
        tga_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'reserves.pkl', 'rb') as file:
        reserves_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'rb') as file:
        rrp_volume = pickle.load(file)
    tga_volume.index = pd.to_datetime(tga_volume.index)
    tga_volume.columns = ['tga_volume']
    rrp_volume.index = pd.to_datetime(rrp_volume.index)
    rrp_volume.columns = ['rrp_volume']
    reserves_volume.index = pd.to_datetime(reserves_volume.index)
    reserves_volume.columns = ['reserves_volume']

    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'rb') as file:
        mmf_repo_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_fed.pkl', 'rb') as file:
        mmf_fed_repo = pickle.load(file)

    mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
    mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo', 'mmf_repo_total']
    mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = (mmf_fed_repo_non_repo_merge['mmf_repo_total'] -
                                                       mmf_fed_repo_non_repo_merge['mmf_fed_repo'])
    mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge['2019-01-01':str(end)].dropna()

    reserve_liabilities_merge = merge_dfs([
        tga_volume.resample('ME').last(),
        rrp_volume.resample('ME').last(),
        reserves_volume.resample('ME').last(),
        mmf_fed_repo_non_repo_merge.resample('ME').last()
    ]).dropna()

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['mmf_non_fed_repo'],
    #          label="Non-Fed Repo", color="#9DDCF9", lw=2)
    # plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['tga_volume'],
    #          label="TGA", color="#233852", lw=2)
    # plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['reserves_volume'],
    #          label="Reserves", color="#F5B820", lw=2)
    # plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['rrp_volume'],
    #          label="RRP", color="#E69B93", lw=2)
    # plt.title("Reserves Liabilities of the System", fontsize=22, fontweight="bold")
    # plt.ylabel('Dollars')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
