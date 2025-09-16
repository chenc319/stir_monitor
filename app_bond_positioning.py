### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ FUTURES ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
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
### -------------------------------------- FUTURES LEVERAGE MONEY SHORT -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_futures_leverage_money_short(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'rb') as file:
        cftc_all_futures = pickle.load(file)
    bonds_cftc_subset = cftc_all_futures[
        cftc_all_futures['contract_market_name'].isin([
            'UST 2Y NOTE', 'UST 5Y NOTE', 'UST 10Y NOTE', 'ULTRA UST 10Y'
        ])
    ]
    bonds_future_leverage_money_short = bonds_cftc_subset[[
        'commodity_name','contract_market_name','report_date_as_yyyy_mm_dd','lev_money_positions_short','contract_units'
    ]].copy()
    bonds_future_leverage_money_short['report_date_as_yyyy_mm_dd'] = pd.to_datetime(
        bonds_future_leverage_money_short['report_date_as_yyyy_mm_dd']
    )
    pivot = bonds_future_leverage_money_short.pivot_table(
        index='report_date_as_yyyy_mm_dd',
        columns='commodity_name',
        values='lev_money_positions_short',
        aggfunc='sum'
    )
    pivot = pivot.loc[str(start):str(end)]
    pivot['T-NOTES, 1-2 YEAR'] = pivot['T-NOTES, 1-2 YEAR'] * 200000
    pivot['T-NOTES, 4-6 YEAR'] = pivot['T-NOTES, 4-6 YEAR'] * 100000
    pivot['T-NOTES, 6.5-10 YEAR'] = pivot['T-NOTES, 6.5-10 YEAR'] * 100000


    # ### PLOT ###
    # plt.figure(figsize=(12, 6))
    # for col in pivot.columns:
    #     plt.plot(pivot.index, pivot[col], label=col)
    # plt.title("Leverage Money Short Positions by Treasury Futures Bucket", fontsize=15)
    # plt.xlabel("Date")
    # plt.ylabel("Leverage Money Short Positions")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col in pivot.columns:
        fig.add_trace(go.Scatter(x=pivot.index, y=pivot[col], name=col))
    fig.update_layout(
        title="Leverage Money Short Positions by Treasury Futures Bucket",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- IS THE STABILITY LOWER ROC --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_stability_lower_roc(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp.pkl', 'rb') as file:
        rrp = pickle.load(file)
    with open(Path(DATA_DIR) / 'gc_df.pkl', 'rb') as file:
        gc_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)

    combined_data = merge_dfs([sofr, rrp, gc_df, fed_funds, tri_df, dvp_df])
    combined_data.columns = ['SOFR','ON_RRP_Rate','BGCR','Fed_Funds','TGCR','DVP']
    clean_data = combined_data.dropna(subset=['SOFR','BGCR','TGCR','ON_RRP_Rate','Fed_Funds','DVP'])

    clean_data['Private_Repo_Avg'] = (clean_data['DVP'] + clean_data['TGCR']) / 2
    clean_data['Fed_Facility_Spread'] = clean_data['ON_RRP_Rate'] - clean_data['SOFR']
    clean_data['Private_Repo_Spread'] = clean_data['Private_Repo_Avg'] - clean_data['SOFR']
    clean_data['Fed_Facility_MA30'] = clean_data['Fed_Facility_Spread'].rolling(30).mean()
    clean_data['Private_Repo_MA30'] = clean_data['Private_Repo_Spread'].rolling(30).mean()
    clean_data['Fed_Facility_Z'] = (
        (clean_data['Fed_Facility_MA30'] - clean_data['Fed_Facility_MA30'].mean())
        / clean_data['Fed_Facility_MA30'].std()
    )
    clean_data['Private_Repo_Z'] = (
        (clean_data['Private_Repo_MA30'] - clean_data['Private_Repo_MA30'].mean())
        / clean_data['Private_Repo_MA30'].std()
    )
    plot_data = clean_data.dropna(subset=['Fed_Facility_Z','Private_Repo_Z'])
    plot_data = plot_data.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(plot_data.index, plot_data['Fed_Facility_Z'],
    #          label="Fed Facility to Repo Spreads", color="#1f77b4", lw=2)
    # plt.plot(plot_data.index, plot_data['Private_Repo_Z'],
    #          label="Private Repo Spreads", color="#2E3A59", lw=2)
    # for y_val in [-2, -1, 1, 2]:
    #     plt.axhline(y=y_val, color='gray', linestyle='--', alpha=0.6, linewidth=1)
    # plt.title("Is the Stability Lower\nRate of Change", fontsize=22, fontweight="bold")
    # plt.ylabel("Z-Score")
    # plt.ylim(-5, 5)
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True, alpha=0.3)
    # plt.figtext(0.02, 0.02, 'Fonte: FED, MacroDispatch. Note: Calculations on a 30 MA Difference',
    #             fontsize=9, color='gray')
    # plt.figtext(0.95, 0.02, 'ie', fontsize=14, color='steelblue',
    #             fontweight='bold', ha='right')
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Fed_Facility_Z'],
                             name="Fed Facility to Repo Spreads", line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Private_Repo_Z'],
                             name="Private Repo Spreads", line=dict(color="#2E3A59", width=2)))
    for y_val in [-2, -1, 1, 2]:
        fig.add_hline(y=y_val, line_color='gray', line_dash='dash', opacity=0.6)
    fig.update_layout(
        title="Is the Stability Lower\nRate of Change",
        yaxis_title="Z-Score",
        hovermode='x unified',
        yaxis_range=[-5, 5]
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- HOW DID LEVELS CHANGE ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_how_did_levels_change(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp.pkl', 'rb') as file:
        rrp = pickle.load(file)
    with open(Path(DATA_DIR) / 'gc_df.pkl', 'rb') as file:
        gc_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)

    combined_data = merge_dfs([sofr, rrp, gc_df, fed_funds, tri_df, dvp_df])
    combined_data.columns = ['SOFR','ON_RRP_Rate','BGCR','Fed_Funds','TGCR','DVP']
    clean_data = combined_data.dropna(subset=['SOFR','BGCR','TGCR','ON_RRP_Rate','Fed_Funds','DVP'])

    clean_data['Private_Repo_Avg'] = (clean_data['DVP'] + clean_data['TGCR']) / 2
    clean_data['Fed_Facility_Spread'] = clean_data['ON_RRP_Rate'] - clean_data['SOFR']
    clean_data['Private_Repo_Spread'] = clean_data['Private_Repo_Avg'] - clean_data['SOFR']
    clean_data['Fed_Facility_static_Z'] = (
        (clean_data['Fed_Facility_Spread'] - clean_data['Fed_Facility_Spread'].mean()) /
        clean_data['Fed_Facility_Spread'].std()
    )
    clean_data['Private_Repo_static_Z'] = (
        (clean_data['Private_Repo_Spread'] - clean_data['Private_Repo_Spread'].mean()) /
        clean_data['Private_Repo_Spread'].std()
    )
    plot_static_data = clean_data.dropna(subset=['Fed_Facility_static_Z','Private_Repo_static_Z'])
    plot_static_data = plot_static_data.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(plot_static_data.index, plot_static_data['Fed_Facility_static_Z'],
    #          label="Fed Facility to Repo Spreads", color="#1f77b4", lw=2)
    # plt.plot(plot_static_data.index, plot_static_data['Private_Repo_static_Z'],
    #          label="Private Repo Spreads", color="#2E3A59", lw=2)
    # for y_val in [-2, -1, 1, 2]:
    #     plt.axhline(y=y_val, color='gray', linestyle='--', alpha=0.6, linewidth=1)
    # plt.title("Is the Stability Lower\nRate of Change", fontsize=22, fontweight="bold")
    # plt.ylabel("Z-Score")
    # plt.ylim(-5, 5)
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True, alpha=0.3)
    # plt.figtext(0.95, 0.02, 'ie', fontsize=14, color='steelblue',
    #             fontweight='bold', ha='right')
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_static_data.index, y=plot_static_data['Fed_Facility_static_Z'],
                             name="Fed Facility to Repo Spreads", line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=plot_static_data.index, y=plot_static_data['Private_Repo_static_Z'],
                             name="Private Repo Spreads", line=dict(color="#2E3A59", width=2)))
    for y_val in [-2, -1, 1, 2]:
        fig.add_hline(y=y_val, line_color='gray', line_dash='dash', opacity=0.6)
    fig.update_layout(
        title="Is the Stability Lower\nRate of Change",
        yaxis_title="Z-Score",
        hovermode='x unified',
        yaxis_range=[-5,5],
    )
    st.plotly_chart(fig, use_container_width=True)
