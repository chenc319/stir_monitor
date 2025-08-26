### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------- FED OPERATION ---------------------------------------------- ###
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
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ PLOT SOMA HOLDINGS -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_soma_holdings(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'soma_holdings.pkl', 'rb') as file:
        soma_holdings = pickle.load(file)
    df = soma_holdings.loc[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df.index,
    #          df['mbs'] / 1e12,
    #          label='MBS', color='#aad8ef', linewidth=2)
    # plt.plot(df.index,
    #          df['notesbonds'] / 1e12,
    #          label='Notes/Bonds', color='#4da3d7', linewidth=2)
    # plt.ylabel('Dollar (Trillions)')
    # plt.title('Fed Balance Sheet: Notes/Bonds & MBS')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['notesbonds'],
                             mode='lines+markers',
                             name='Notes/Bonds',
                             line=dict(color='#aad8ef', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['mbs'],
                             mode='lines+markers',
                             name='MBS',
                             line=dict(color='#4da3d7', width=2)))
    fig.update_layout(
        title="Fed Balance Sheet: Notes/Bonds & MBS",
        yaxis_title="Dollar (Trillions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(df.index,
    #          df['tips'] / 1e9,
    #          label='TIPS', color='#aad8ef', linewidth=2)
    # plt.plot(df.index,
    #          df['frn'] / 1e9,
    #          label='FRN', color='#4da3d7', linewidth=2)
    # plt.plot(df.index,
    #          df['tipsInflationCompensation'] / 1e9,
    #          label='tipsInflationCompensation', color='green', linewidth=2)
    # plt.plot(df.index,
    #          df['bills'] / 1e9,
    #          label='Bills', color='#17293c', linewidth=2)
    # plt.plot(df.index,
    #          df['agencies'] / 1e9,
    #          label='Agencies', color='#f5c23e', linewidth=2)
    # plt.plot(df.index,
    #          df['cmbs'] / 1e9,
    #          label='CMBS', color='#f5b9ad', linewidth=2)
    # plt.ylabel('Dollar (Billions)')
    # plt.title('Fed SOMA Holdings')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['tips'],
                             mode='lines+markers',
                             name='TIPS',
                             line=dict(color='#aad8ef', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['frn'],
                             mode='lines+markers',
                             name='FRN',
                             line=dict(color='#2f90c5', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['tipsInflationCompensation'],
                             mode='lines+markers',
                             name='Inflation Compensation',
                             line=dict(color='#17293c', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['bills'],
                             mode='lines+markers',
                             name='Bills',
                             line=dict(color='#f5c23e', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['agencies'],
                             mode='lines+markers',
                             name='Agencies',
                             line=dict(color='#f5b9ad', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['cmbs'],
                             mode='lines+markers',
                             name='CMBS',
                             line=dict(color='#4da3d7', width=2)))
    fig.update_layout(
        title="Fed Balance Sheet: TIPS, FRN, Inflation Compensation,"
              "Bills, Agencies, CMBS",
        yaxis_title="Dollar (Billions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- PLOT REPO FED OPERATIONS ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_repo_operations(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'repo_fed_df.pkl', 'rb') as file:
        repo_fed_df = pickle.load(file)

    repo_fed_df['treasury_amt'] = 0
    repo_fed_df['agency_amt'] = 0
    repo_fed_df['mbs_amt'] = 0
    for row in repo_fed_df.index:
        repo_fed_df.loc[row,'treasury_amt'] = repo_fed_df.loc[row,'details'][0]['amtAccepted']
        repo_fed_df.loc[row, 'agency_amt'] = repo_fed_df.loc[row, 'details'][1]['amtAccepted']
        repo_fed_df.loc[row, 'mbs_amt'] = repo_fed_df.loc[row, 'details'][2]['amtAccepted']
    repo_mbs_df = repo_fed_df.groupby('operationDate', as_index=False)['mbs_amt'].sum()
    repo_mbs_df.index = pd.to_datetime(repo_mbs_df['operationDate'].values)
    repo_mbs_df.drop('operationDate', axis=1, inplace=True)
    repo_treasury_df = repo_fed_df.groupby('operationDate', as_index=False)['treasury_amt'].sum()
    repo_treasury_df.index = pd.to_datetime(repo_treasury_df['operationDate'].values)
    repo_treasury_df.drop('operationDate', axis=1, inplace=True)
    repo_agency_df = repo_fed_df.groupby('operationDate', as_index=False)['agency_amt'].sum()
    repo_agency_df.index = pd.to_datetime(repo_agency_df['operationDate'].values)
    repo_agency_df.drop('operationDate', axis=1, inplace=True)
    repo_agency_df = repo_agency_df.loc[start:end]
    repo_treasury_df = repo_treasury_df.loc[start:end]
    repo_mbs_df = repo_mbs_df.loc[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(repo_treasury_df.index,
    #          repo_treasury_df['treasury_amt'] / 1e9,
    #          label='Treasury', color='#aad8ef', linewidth=2)
    # plt.ylabel('Dollar (Trillions)')
    # plt.ylim(0,1)
    # plt.title('Standing Repo Facility Operations')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=repo_treasury_df.index,
                             y=repo_treasury_df['treasury_amt'],
                             mode='lines+markers',
                             name='Treasury',
                             line=dict(color='#aad8ef', width=2)))
    fig.update_layout(
        title="SRF: Treasury",
        yaxis_title="Dollar (Trillions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(repo_mbs_df.index,
    #          repo_mbs_df['mbs_amt'] / 1e6,
    #          label='MBS', color='#4da3d7', linewidth=2)
    # plt.ylabel('Dollar (Millions)')
    # plt.title('Standing Repo Facility Operations')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=repo_mbs_df.index,
                             y=repo_mbs_df['mbs_amt'],
                             mode='lines+markers',
                             name='MBS',
                             line=dict(color='#f5c23e', width=2)))
    fig.update_layout(
        title="SRF: MBS",
        yaxis_title="Dollar (Millions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(repo_agency_df.index,
    #          repo_agency_df['agency_amt'] / 1e6,
    #          label='Agency', color='green', linewidth=2)
    # plt.ylabel('Dollar (Millions)')
    # plt.title('Standing Repo Facility Operations')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=repo_agency_df.index,
                             y=repo_agency_df['agency_amt'],
                             mode='lines+markers',
                             name='Agency',
                             line=dict(color='#17293c', width=2)))
    fig.update_layout(
        title="SRF: Agency",
        yaxis_title="Dollar (Millions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- PLOT ON RRP FED OPERATIONS ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_rrp_operations(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'rrp_fed_df.pkl', 'rb') as file:
        rrp_fed_df = pickle.load(file)

    rrp_fed_df['rate'] = 0
    for row in rrp_fed_df.index:
        details = rrp_fed_df.loc[row,'details'][0]
        rrp_fed_df.loc[row,'rate'] = details['percentAwardRate']

    rrp_fed_df.columns
    rrp_fed_df.index = pd.to_datetime(rrp_fed_df['operationDate'].values)
    rrp_fed_df = rrp_fed_df[::-1]

    ctpy_rrp_fed_df = pd.DataFrame(rrp_fed_df['acceptedCpty'])
    amount_rrp_fed_df = pd.DataFrame(rrp_fed_df['totalAmtAccepted'])
    rate_rrp_fed_df = pd.DataFrame(rrp_fed_df['rate'])
    ctpy_rrp_fed_df = ctpy_rrp_fed_df.loc[start:end]
    amount_rrp_fed_df = amount_rrp_fed_df.loc[start:end]
    rate_rrp_fed_df = rate_rrp_fed_df.loc[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(amount_rrp_fed_df.index,
    #          amount_rrp_fed_df['totalAmtAccepted'] / 1e12,
    #          label='Daily Fed Repo Operations', color='#aad8ef', linewidth=2)
    # plt.ylabel('Dollar (Trillions)')
    # plt.title('Standing Repo Facility Operations')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=amount_rrp_fed_df.index,
                             y=amount_rrp_fed_df['totalAmtAccepted'],
                             mode='lines+markers',
                             name='ONRRP Accepted',
                             line=dict(color='#aad8ef', width=2)))
    fig.update_layout(
        title="ONRRP Facility: Amount Accepted",
        yaxis_title="Dollar (Trillions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # plt.figure(figsize=(12, 7))
    # plt.plot(ctpy_rrp_fed_df.index,
    #          ctpy_rrp_fed_df['acceptedCpty'],
    #          label='Daily Counterparty', color='#aad8ef', linewidth=2)
    # plt.ylabel('# of Counterparties')
    # plt.title('ONRRP Counterparty Participation')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ctpy_rrp_fed_df.index,
                             y=ctpy_rrp_fed_df['acceptedCpty'],
                             mode='lines+markers',
                             name='Ctpy Participation',
                             line=dict(color='#f5c23e', width=2)))
    fig.update_layout(
        title="ONRRP Facility: Counterparty Participation",
        yaxis_title="# of Counterparties",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # plt.figure(figsize=(12, 7))
    # plt.plot(rate_rrp_fed_df.index,
    #          rate_rrp_fed_df['rate'],
    #          color='#aad8ef', linewidth=2)
    # plt.ylabel('%')
    # plt.title('ONRRP Daily Accepted Rate')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rate_rrp_fed_df.index,
                             y=rate_rrp_fed_df['rate'],
                             mode='lines+markers',
                             name='Ctpy Participation',
                             line=dict(color='#17293c', width=2)))
    fig.update_layout(
        title="ONRRP Facility: Accepted Rates",
        yaxis_title="%",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
