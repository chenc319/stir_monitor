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

### SET DATES ###
start = datetime.datetime(2018, 1, 1)
end = datetime.datetime.today()

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
### ------------- MAPPING CORPORATE ENTITIES INVOLVEMENT IN SHADOW BANKING CHAIN OF JPMC, GS, MS ------------- ###
### ---------------------------------------------------------------------------------------------------------- ###







