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
### --------------------------------- MMF INVOLVEMENT IN TREASURY SECURITIES --------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_mmf_repo(start, end, **kwargs):
    mmf_repo_url = ('https://www.financialresearch.gov/money-market-funds'
                    '/data/repo_activity_collateral/data.json')
    mmf_repo_allocations = pd.DataFrame(requests.get(mmf_repo_url).json()['datatable']['values'],
                                        columns = ['Date','Other Repo','Agency Repo','Treasury Repo'])
    mmf_repo_allocations.index = pd.to_datetime(mmf_repo_allocations['Date'].values)
    mmf_repo_allocations.drop('Date', axis=1, inplace=True)
    mmf_repo_allocations = mmf_repo_allocations / 1e12
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
                             line=dict(color="#17354c", width=3)))
    fig.add_trace(go.Scatter(x=mmf_repo_allocations.index,
                             y=mmf_repo_allocations['Treasury Repo'],
                             mode='lines+markers',
                             name='Treasury Repo',
                             line=dict(color="#17354c", width=3)))
    fig.update_layout(
        title="MMF's Investments in Repo Markets",
        yaxis_title="$ (Trillions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)


### ---------------------------------------------------------------------------------------------------------- ###
### ------------- MONEY MARKET FUNDS INVOLVEMENTS IN ON repo SPECIFICALLY TO CAPTURE STIR ACTIVITY ------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_mmf_on_repo(start, end, **kwargs):
    mmf_involvement_on_repo = pd.DataFrame(requests.get('https://data.financialresearch.gov/'
                                          'v1/series/timeseries?mnemonic=MMF-MMF_RP_OO-M').json(),
                                          columns = ['Date','Values'])
    mmf_involvement_on_repo.index = pd.to_datetime(mmf_involvement_on_repo['Date'].values)
    mmf_involvement_on_repo.drop('Date', axis=1, inplace=True)
    mmf_involvement_on_rrp = mmf_involvement_on_repo / 1e12
    mmf_involvement_on_rrp = mmf_involvement_on_rrp[start:end]

    ### PLOT ###
    plt.figure(figsize=(10, 7))
    plt.plot(mmf_involvement_on_repo.index, mmf_involvement_on_repo['Values'],
             color='#9DDCF9', lw=2)  # light blue
    plt.ylabel("$ (Trillions)")
    plt.title("MMF's Investments in Overnight/Open Repo", fontsize=17, fontweight="bold")
    plt.tight_layout()
    plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mmf_involvement_on_repo.index,
                             y=mmf_involvement_on_repo['Values'],
                             mode='lines+markers',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="MMF's Investments in Overnight/Open Repo",
        yaxis_title="$ (Trillions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)