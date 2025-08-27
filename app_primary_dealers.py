### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- PRIMARY DEALERS --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- SPONSORED VOLUMES - THE SOLUTION? ------------------------------------ ###
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(sponsored_volume.index, sponsored_volume['DVP_TOTAL_AMOUNT'],
    #          label='DVP Sponsored', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(sponsored_volume.index, sponsored_volume['GC_TOTAL_AMOUNT'],
    #          label='GC Sponsored', color='#233852', lw=2)  # dark blue
    # plt.ylabel("Trillions")
    # plt.title("Sponsored Volumes - The Solutions?", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sponsored_volume.index, y=sponsored_volume['DVP_TOTAL_AMOUNT'], name='DVP Sponsored',
                             line=dict(color='#4CD0E9', width=2)))
    fig.add_trace(go.Scatter(x=sponsored_volume.index, y=sponsored_volume['GC_TOTAL_AMOUNT'], name='GC Sponsored',
                             line=dict(color='#233852', width=2)))
    fig.update_layout(
        title="Sponsored Volumes - The Solutions?",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SPONSORED VOLUMES -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sponsored_volumes(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'ficc_sponsored_repo_volume.pkl', 'rb') as file:
        ficc_sponsored_repo_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'ficc_sponsored_rrp_volume.pkl', 'rb') as file:
        ficc_sponsored_rrp_volume = pickle.load(file)

    merge = merge_dfs([ficc_sponsored_repo_volume, ficc_sponsored_rrp_volume])
    merge.columns = ['sponsored_repo', 'sponsored_rrp']
    merge = merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(merge.index, merge['sponsored_repo'],
    #          label='Repo Sponsored', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(merge.index, merge['sponsored_rrp'],
    #          label='RRP Sponsored', color='#233852', lw=2)  # dark blue
    # plt.ylabel("Trillions")
    # plt.title("Sponsored Volumes", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['sponsored_repo'], name='Repo Sponsored',
                             line=dict(color='#4CD0E9', width=2)))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['sponsored_rrp'], name='RRP Sponsored',
                             line=dict(color='#233852', width=2)))
    fig.update_layout(
        title="Sponsored Volumes",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- % OF DVP VOLUME THAT IS SPONSORED ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_pct_dvp_sponsored(start, end, path_to_csv="data/SponsoredVolume.csv", **kwargs):
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume = pickle.load(file)

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
    merge = merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(merge.index, merge['pct'],
    #          color='#4CD0E9', lw=2)  # cyan
    # plt.ylabel("%")
    # plt.title("% of DVP that is Sponsored", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['pct'] * 100,
                             name="% of DVP that is Sponsored", line=dict(color='#4CD0E9', width=2)))
    fig.update_layout(
        title="% of DVP that is Sponsored",
        yaxis_title="%",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ PRIMARY DEALERS NET POSITIONS BILLS VS BONDS ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_positions_bills_vs_bonds(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_positions.pkl', 'rb') as file:
        all_pd_bills_bonds_positions = pickle.load(file)
    all_pd_bills_bonds_positions = all_pd_bills_bonds_positions[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(13, 7))
    # plt.plot(all_pd.index, all_pd['bills'],
    #          label='Bills', color='#43c4e6', linewidth=2)
    # plt.plot(all_pd.index, all_pd['net_nominal_bonds'],
    #          label='Net Nominal Bonds', color='#262e39', linewidth=2)
    # plt.title("Primary Dealers Net Positions Bills VS Bonds", fontsize=20, fontweight="bold")
    # plt.ylabel("Billions")
    # plt.xlabel("")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True, which='major', linestyle='-', color='grey', alpha=0.3)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=all_pd_bills_bonds_positions.index,
                             y=all_pd_bills_bonds_positions['bills'], name="Bills",
                             line=dict(color='#43c4e6', width=2)))
    fig.add_trace(go.Scatter(x=all_pd_bills_bonds_positions.index,
                             y=all_pd_bills_bonds_positions['net_nominal_bonds'], name="Net Nominal Bonds",
                             line=dict(color='#262e39', width=2)))
    fig.update_layout(
        title="Primary Dealers Net Positions Bills VS Bonds",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------- PRIMARY DEALERS NET POSITIONS BY BOND TENOR ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_positions_by_bond_tenor(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_positions.pkl', 'rb') as file:
        all_pd_bills_bonds_positions = pickle.load(file)
    all_pd_bills_bonds_positions = all_pd_bills_bonds_positions[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(all_pd.index, all_pd['l2'],
    #          label='Bond <2Y', color='#9DDCF9')
    # plt.plot(all_pd.index, all_pd['g2l3'],
    #          label='Bond 2-3Y', color='#4CD0E9')
    # plt.plot(all_pd.index, all_pd['g3l6'],
    #          label='Bond 3-6Y', color='#233852')
    # plt.plot(all_pd.index, all_pd['g6l7'],
    #          label='Bond 6-7Y', color='#F5B820', linewidth=2)
    # plt.plot(all_pd.index, all_pd['g7l11'],
    #          label='Bond 7-10Y', color='#E69B93')
    # plt.ylabel("Billions")
    # plt.title("Primary Dealers Net Positions By Bond Tenor", fontsize=20, fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    tenors = [
        ('l2', 'Bond <2Y', '#9DDCF9'),
        ('g2l3', 'Bond 2-3Y', '#4CD0E9'),
        ('g3l6', 'Bond 3-6Y', '#233852'),
        ('g6l7', 'Bond 6-7Y', '#F5B820'),
        ('g7l11', 'Bond 7-10Y', '#E69B93'),
    ]
    for k, name, color in tenors:
        fig.add_trace(go.Scatter(x=all_pd_bills_bonds_positions.index,
                                 y=all_pd_bills_bonds_positions[k], name=name, line=dict(color=color, width=2)))
    fig.update_layout(
        title="Primary Dealers Net Positions By Bond Tenor",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------- PRIMARY DEALERS BOND NET POSITION CHANGE -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_change_by_bond_tenor(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_net_changes.pkl', 'rb') as file:
        all_pd_bills_bonds_net_changes = pickle.load(file)
    all_pd_bills_bonds_net_changes = all_pd_bills_bonds_net_changes[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(all_pd_change.index, all_pd_change['l2'],
    #          label='Bond <2Y', color='#9DDCF9')
    # plt.plot(all_pd_change.index, all_pd_change['g2l3'],
    #          label='Bond 2-3Y', color='#4CD0E9')
    # plt.plot(all_pd_change.index, all_pd_change['g3l6'],
    #          label='Bond 3-6Y', color='#233852')
    # plt.plot(all_pd_change.index, all_pd_change['g6l7'],
    #          label='Bond 6-7Y', color='#F5B820', linewidth=2)
    # plt.plot(all_pd_change.index, all_pd_change['g7l11'],
    #          label='Bond 7-10Y', color='#E69B93')
    # plt.ylabel("Billions")
    # plt.title("Primary Dealers Net Position Change By Bond Tenor", fontsize=20, fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    tenors = [
        ('l2', 'Bond <2Y', '#9DDCF9'),
        ('g2l3', 'Bond 2-3Y', '#4CD0E9'),
        ('g3l6', 'Bond 3-6Y', '#233852'),
        ('g6l7', 'Bond 6-7Y', '#F5B820'),
        ('g7l11', 'Bond 7-10Y', '#E69B93'),
    ]
    for k, name, color in tenors:
        fig.add_trace(go.Scatter(x=all_pd_bills_bonds_net_changes.index,
                                 y=all_pd_bills_bonds_net_changes[k], name=name, line=dict(color=color, width=2)))
    fig.update_layout(
        title="Primary Dealers Net Position Change By Bond Tenor",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
