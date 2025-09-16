### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------- SYSTEM MAPPING --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pandas_datareader import data as pdr
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

### FUNCTIONS ###
def merge_dfs(array_of_dfs):
    new_df = ft.reduce(lambda left,
                              right: pd.merge(left,
                                                    right,
                                                    left_index=True,
                                                    right_index=True,
                                                    how='outer'), array_of_dfs)
    return(new_df)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SHADOW BANK SUMMARY ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_summary(start, end, **kwargs):
    ### OFR DATA PULLS ###
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'rb') as file:
        gcf_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    repo_merge_df = merge_dfs([tri_volume_df, dvp_volume_df, gcf_volume_df])
    repo_merge_df.columns = ['tri', 'dvp', 'gcf']
    total_repo = pd.DataFrame(repo_merge_df.sum(axis=1),
                              columns=['total_repo'])
    with open(Path(DATA_DIR) / 'reit_liabilities.pkl', 'rb') as file:
        reit_liabilities = pickle.load(file)
    with open(Path(DATA_DIR) / 'brokers_dealers_repo_liabilities.pkl', 'rb') as file:
        brokers_dealers_repo_liabilities = pickle.load(file)
    with open(Path(DATA_DIR) / 'hedge_funds_liabilities.pkl', 'rb') as file:
        hedge_funds_liabilities = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_assets.pkl', 'rb') as file:
        mmf_assets = pickle.load(file)

    merge_df = merge_dfs([brokers_dealers_repo_liabilities,
                          reit_liabilities,
                          mmf_assets,
                          hedge_funds_liabilities,
                          total_repo])

    merge_df.columns = ['Broker/Dealer','REITs', 'MMFs', 'HFs','Total Repo']
    merge_df['Total Repo'] = merge_df['Total Repo'].ffill()
    merge_df = merge_df.dropna()

    merge_df['bd_pct'] = merge_df['Broker/Dealer'] / merge_df['Total Repo']
    merge_df['hf_pct'] = merge_df['HFs'] / merge_df['Total Repo']
    merge_df['mmf_pct'] = merge_df['MMFs'] / merge_df['Total Repo']
    merge_df['reit_pct'] = merge_df['REITs'] / merge_df['Total Repo']

    merge_df = merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['Broker/Dealer'],
                             mode='lines',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['HFs'],
                             mode='lines',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['MMFs'],
                             mode='lines',
                             name='MMFs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['REITs'],
                             mode='lines',
                             name='REITs',
                             line=dict(color="#aad8ef", width=3)))
    fig.update_layout(
        title="Shadow Banks Components",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['bd_pct'] * 100,
                             mode='lines',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['hf_pct'] * 100,
                             mode='lines',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['mmf_pct'] * 100,
                             mode='lines',
                             name='MMFs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['reit_pct'] * 100,
                             mode='lines',
                             name='REITs',
                             line=dict(color="#aad8ef", width=3)))
    fig.update_layout(
        title="Shadow Banks Components",
        yaxis_title="% of Total Repo",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------- PRIVATE REAL ESTATE INVESTMENT FUNDS ---------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

# def plot_shadow_bank_reit(start, end, **kwargs):
#     abcp = pdr.DataReader('ABCOMP',
#                           'fred', start, end) * 1e9
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=abcp.index,
#                              y=abcp['ABCOMP'],
#                              mode='lines',
#                              name='ABCOMP',
#                              line=dict(color="#46b5ca", width=3)))
#     fig.update_layout(
#         title="Asset-Backed Commercial Paper Volume",
#         yaxis_title="$",
#         hovermode='x unified'
#     )
#     st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SHADOW BANK ASSETS ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_assets(start, end, **kwargs):
    ### OFR DATA PULLS ###
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'rb') as file:
        gcf_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    repo_merge_df = merge_dfs([tri_volume_df, dvp_volume_df, gcf_volume_df])
    repo_merge_df.columns = ['tri', 'dvp', 'gcf']
    total_repo = pd.DataFrame(repo_merge_df.sum(axis=1),
                              columns=['total_repo'])
    with open(Path(DATA_DIR) / 'brokers_dealers_repo_assets.pkl', 'rb') as file:
        brokers_dealers_repo_assets = pickle.load(file)
    with open(Path(DATA_DIR) / 'hedge_funds_assets.pkl', 'rb') as file:
        hedge_funds_assets = pickle.load(file)
    with open(Path(DATA_DIR) / 'mmf_assets.pkl', 'rb') as file:
        mmf_assets = pickle.load(file)

    merge_df = merge_dfs([brokers_dealers_repo_assets,
                          hedge_funds_assets,
                          mmf_assets,
                          total_repo])

    merge_df.columns = ['Broker/Dealer', 'HFs', 'MMFs', 'Total Repo']
    merge_df['Total Repo'] = merge_df['Total Repo'].ffill()
    merge_df = merge_df.dropna()
    merge_df['bd_pct'] = merge_df['Broker/Dealer'] / merge_df['Total Repo']
    merge_df['hf_pct'] = merge_df['HFs'] / merge_df['Total Repo']
    merge_df['mmf_pct'] = merge_df['MMFs'] / merge_df['Total Repo']

    merge_df = merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['Broker/Dealer'],
                             mode='lines',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['HFs'],
                             mode='lines',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['MMFs'],
                             mode='lines',
                             name='REITs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.update_layout(
        title="Shadow Banks: Repo Assets",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['bd_pct'] * 100,
                             mode='lines',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['hf_pct'] * 100,
                             mode='lines',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['mmf_pct'] * 100,
                             mode='lines',
                             name='MMFs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.update_layout(
        title="Shadow Banks: Repo Assets",
        yaxis_title="% of Total Repo",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)


### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- SHADOW BANK LIABILITIES ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_liabilities(start, end, **kwargs):
    ### OFR DATA PULLS ###
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'rb') as file:
        gcf_volume_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'rb') as file:
        tri_volume_df = pickle.load(file)
    repo_merge_df = merge_dfs([tri_volume_df,dvp_volume_df,gcf_volume_df])
    repo_merge_df.columns = ['tri','dvp','gcf']
    total_repo = pd.DataFrame(repo_merge_df.sum(axis=1),
                              columns = ['total_repo'])

    ### FRED DATA PULLS ###
    with open(Path(DATA_DIR) / 'brokers_dealers_repo_liabilities.pkl', 'rb') as file:
        brokers_dealers_repo_liabilities = pickle.load(file)
    with open(Path(DATA_DIR) / 'hedge_funds_liabilities.pkl', 'rb') as file:
        hedge_funds_liabilities = pickle.load(file)
    with open(Path(DATA_DIR) / 'reit_liabilities.pkl', 'rb') as file:
        reit_liabilities = pickle.load(file)

    merge_df = merge_dfs([brokers_dealers_repo_liabilities,
                          hedge_funds_liabilities,
                          reit_liabilities,
                          total_repo])
    merge_df.columns = ['Broker/Dealer','HFs','REITs','Total Repo']
    merge_df['Total Repo'] = merge_df['Total Repo'].ffill()
    merge_df = merge_df.dropna()
    merge_df['bd_pct'] = merge_df['Broker/Dealer'] / merge_df['Total Repo']
    merge_df['hf_pct'] = merge_df['HFs'] / merge_df['Total Repo']
    merge_df['reit_pct'] = merge_df['REITs'] / merge_df['Total Repo']

    merge_df = merge_df[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(merge_df.index, merge_df['Broker/Dealer'],
    #          label='Broker/Dealer', color='#0B2138')
    # plt.plot(merge_df.index, merge_df['HFs'],
    #          label='HFs', color='#48DEE9')
    # plt.plot(merge_df.index,
    #          merge_df['REITs'],
    #          label='REITs', color='#7EC0EE')
    # plt.ylabel("$")
    # plt.title("Shadow Banks: Repo Liabilities", fontsize=20, fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['Broker/Dealer'],
                             mode='lines',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['HFs'],
                             mode='lines',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['REITs'],
                             mode='lines',
                             name='REITs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.update_layout(
        title="Shadow Banks: Repo Liabilities",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['bd_pct'] * 100,
                             mode='lines',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['hf_pct'] * 100,
                             mode='lines',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['reit_pct'] * 100,
                             mode='lines',
                             name='REITs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.update_layout(
        title="Shadow Banks: Repo Liabilities",
        yaxis_title="% of Total Repo",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)





