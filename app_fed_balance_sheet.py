### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- FED BALANCE SHEET -------------------------------------------- ###
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
from plotly.subplots import make_subplots
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'), array_of_dfs)

asset_colors = {
    'securities_outright': '#5FB3FF',   # Vivid sky blue (QE, stable)
    'lending_portfolio':   '#2DCDB2',   # Bright teal/mint (portfolio)
    'treasuries':          '#FFC145',   # Sun gold (Treasury)
    'mbs':                 '#FF6969',   # Approachable coral (MBS)
    'permanent_lending':   '#54C6EB',   # Aqua blue (permanent lending)
    'temporary_lending':   '#FFD166',   # Citrus yellow-orange (temp lending)
    'srf':                 '#6FE7DD',   # Lively turquoise (repo facility)
    'discount_window':     '#8D8DFF',   # Periwinkle (DW lending)
    'fx_swap_line':        '#A685E2',   # Pleasant purple (FX swaps)
    'ppp':                 '#FF8FAB',   # Bright pink (PPP)
    'ms':                  '#FFA952',   # Peach (Main Street)
}

liab_colors = {
    'currency':         '#F9DB6D',   # Warm gold (currency)
    'rrp':              '#3CB1CD',   # Vivid blue (RRP)
    'foreign_repo':     '#85F4FA',   # Electric cyan (foreign repo)
    'reserves':         '#21A179',   # Strong green (reserves)
    'tga':              '#B084CC',   # Violet (TGA)
    'gse_dmfu':         '#FFB685',   # Soft orange (GSE/DMFU)
    'total_reserves':   '#21A179',   # Match reserves
    'total_rrp':        '#3CB1CD',   # Match RRP
}

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- ASSETS ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_balance_sheet_assets(start, end, **kwargs):
    ### ASSETS ###
    with open(Path(DATA_DIR) / 'fed_assets_securities_outright.pkl', 'rb') as file:
        fed_assets_securities_outright = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_treasury_securities.pkl', 'rb') as file:
        fed_assets_treasury_securities = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_notes_and_bonds.pkl', 'rb') as file:
        fed_assets_notes_and_bonds = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_mbs.pkl', 'rb') as file:
        fed_assets_mbs = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_total.pkl', 'rb') as file:
        fed_assets_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_total.pkl', 'rb') as file:
        fed_assets_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_srf.pkl', 'rb') as file:
        fed_assets_srf = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_dw_primary.pkl', 'rb') as file:
        fed_assets_dw_primary = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_dw_secondary.pkl', 'rb') as file:
        fed_assets_dw_secondary = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_dw_seasonal.pkl', 'rb') as file:
        fed_assets_dw_seasonal = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_fx_swap_line.pkl', 'rb') as file:
        fed_assets_fx_swap_line = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_main_street.pkl', 'rb') as file:
        fed_assets_main_street = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_ppp_facility.pkl', 'rb') as file:
        fed_assets_ppp_facility = pickle.load(file)

    fed_assets_merge = merge_dfs([fed_assets_securities_outright,
                                  fed_assets_treasury_securities,
                                  fed_assets_notes_and_bonds,
                                  fed_assets_mbs,
                                  fed_assets_srf,
                                  fed_assets_dw_primary,
                                  fed_assets_dw_secondary,
                                  fed_assets_dw_seasonal,
                                  fed_assets_fx_swap_line,
                                  fed_assets_main_street,
                                  fed_assets_ppp_facility,
                                  fed_assets_total]).dropna()
    fed_assets_merge.index = pd.to_datetime(fed_assets_merge.index.values)
    fed_assets_merge.columns = ['securities_outright',
                                'treasuries',
                                'notes_bonds',
                                'mbs',
                                'srf',
                                'dw_primary',
                                'dw_secondary',
                                'dw_seasonal',
                                'fx_swap_line',
                                'ms',
                                'ppp',
                                'total']
    fed_assets_merge['discount_window'] = (fed_assets_merge['dw_primary']+
                                           fed_assets_merge['dw_secondary']+
                                           fed_assets_merge['dw_seasonal'])
    fed_assets_merge['permanent_lending'] = (fed_assets_merge['srf']+
                                             fed_assets_merge['discount_window']+
                                             fed_assets_merge['fx_swap_line'])
    fed_assets_merge['temporary_lending'] = (fed_assets_merge['ms']+
                                             fed_assets_merge['ppp'])
    fed_assets_merge['lending_portfolio'] = (fed_assets_merge['permanent_lending'] +
                                             fed_assets_merge['temporary_lending'])
    fed_assets_merge_diff = fed_assets_merge.diff(1).dropna()
    fed_assets_merge_diff_mean = fed_assets_merge_diff.mean(axis=0)
    fed_assets_merge_diff_std = fed_assets_merge_diff.std(axis=0)
    fed_assets_merge_diff_z = (fed_assets_merge_diff - fed_assets_merge_diff_mean) / fed_assets_merge_diff_std

    fed_assets_merge = fed_assets_merge[start:end]
    fed_assets_merge_diff = fed_assets_merge_diff[start:end]
    fed_assets_merge_diff_z = fed_assets_merge_diff_z[start:end]

    ### PLOT ###
    fig = go.Figure()
    cols = ['securities_outright', 'lending_portfolio']
    labels = [
        'QE Securities',
        'Lending Portfolio',
    ]
    colors = [asset_colors['securities_outright'], asset_colors['lending_portfolio']]
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=fed_assets_merge.index, y=fed_assets_merge[col],
                                 mode='lines+markers',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Assets: Summary",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    st.title("'QE Securities'")
    fig = go.Figure()
    cols = ['treasuries', 'mbs']
    labels = [
        'Treasury',
        'MBS',
    ]
    colors = [asset_colors['treasuries'],
              asset_colors['mbs']]
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_assets_merge.index,
                y=fed_assets_merge[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="QE Securities: Weekly Averages",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_assets_merge_diff.index,
                y=fed_assets_merge_diff[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="QE Securities: Weekly Changes",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_assets_merge_diff_z.index,
                y=fed_assets_merge_diff_z[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="QE Securities: Weekly Changes Z-Scored",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    st.title("'Lending Portfolio'")
    fig = go.Figure()
    cols = ['permanent_lending', 'temporary_lending']
    labels = [
        'Permanent Lending Portfolio',
        'Temporary Lending Portfolio',
    ]
    colors = [asset_colors['permanent_lending'], asset_colors['temporary_lending']]
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_assets_merge.index,
                y=fed_assets_merge[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Lending Portfolio: Weekly Averages",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = ['srf', 'discount_window','fx_swap_line']
    labels = [
        'SRF',
        'Discount Window',
        'FX Swap Line',
    ]
    colors = [asset_colors['srf'], asset_colors['discount_window'], asset_colors['fx_swap_line']]
    fig = make_subplots(rows=1, cols=3, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 3 + 1
        col_position = i % 3 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_assets_merge.index,
                y=fed_assets_merge[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Permanent Lending Portfolio: Weekly Averages",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = ['ppp', 'ms']
    labels = [
        'PPP Liquidity Facility (Direct Lending)',
        'Main Street Lending Facility (Indirect Lending)',
    ]
    colors = [asset_colors['ppp'], asset_colors['ms']]
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_assets_merge.index,
                y=fed_assets_merge[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Temporary Lending Portfolio: Weekly Averages",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- LIABILITIES ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_balance_sheet_liabilities(start, end, **kwargs):
    ### LIABILITIES ###
    with open(Path(DATA_DIR) / 'fed_liabilities_currency.pkl', 'rb') as file:
        fed_liabilities_currency = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_foreign_repo.pkl', 'rb') as file:
        fed_liabilities_foreign_repo = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_rrp.pkl', 'rb') as file:
        fed_liabilities_rrp = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_reserves.pkl', 'rb') as file:
        fed_liabilities_reserves = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_tga.pkl', 'rb') as file:
        fed_liabilities_tga = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_gse_dmfu.pkl', 'rb') as file:
        fed_liabilities_gse_dmfu = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_total.pkl', 'rb') as file:
        fed_liabilities_total = pickle.load(file)
    fed_liabilities_merge = merge_dfs([fed_liabilities_currency,
                                       fed_liabilities_rrp,
                                       fed_liabilities_foreign_repo,
                                       fed_liabilities_reserves,
                                       fed_liabilities_tga,
                                       fed_liabilities_gse_dmfu,
                                       fed_liabilities_total]).dropna()
    fed_liabilities_merge.index = pd.to_datetime(fed_liabilities_merge.index.values)
    fed_liabilities_merge.columns = ['currency','rrp','foreign_repo',
                                     'reserves','tga','gse_dmfu','total']
    fed_liabilities_merge['others'] = (fed_liabilities_merge['total']-
                                       fed_liabilities_merge['currency'] -
                                       fed_liabilities_merge['rrp']-
                                       fed_liabilities_merge['foreign_repo']-
                                       fed_liabilities_merge['reserves']-
                                       fed_liabilities_merge['tga']-
                                       fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['rrp_total'] = fed_liabilities_merge['rrp'] + fed_liabilities_merge['foreign_repo']
    fed_liabilities_merge['reserves_total'] = (fed_liabilities_merge['reserves'] +
                                               fed_liabilities_merge['tga'] +
                                               fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['total_reserves'] = (fed_liabilities_merge['reserves'] +
                                               fed_liabilities_merge['tga'] +
                                               fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['total_rrp'] = (fed_liabilities_merge['rrp'] + fed_liabilities_merge['foreign_repo'])
    fed_liabilities_merge_diff = fed_liabilities_merge.diff(1).dropna()

    fed_liabilities_merge_diff_mean = fed_liabilities_merge_diff.mean(axis=0)
    fed_liabilities_merge_diff_std = fed_liabilities_merge_diff.std(axis=0)
    fed_liabilities_merge_diff_z = (fed_liabilities_merge_diff -
                                    fed_liabilities_merge_diff_mean) / fed_liabilities_merge_diff_std

    fed_liabilities_merge = fed_liabilities_merge[start:end]
    fed_liabilities_merge_diff = fed_liabilities_merge_diff[start:end]
    fed_liabilities_merge_diff_z = fed_liabilities_merge_diff_z[start:end]

    ### PLOT ###
    fig = go.Figure()
    cols = ['currency', 'total_reserves', 'total_rrp']
    labels = [
        'Currency',
        'Total Reserves',
        'Total RRP'
    ]
    colors = [liab_colors['currency'], liab_colors['total_reserves'],liab_colors['total_rrp']]
    for col, color, label in zip(cols,colors,labels):
        fig.add_trace(go.Scatter(x=fed_liabilities_merge.index, y=fed_liabilities_merge[col],
                                 mode='lines+markers',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Liabilities: Summary",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = ['currency', 'rrp', 'foreign_repo', 'reserves', 'tga', 'gse_dmfu']
    labels = [
        'Currency',
        'RRP Facility',
        'Foreign RP Facility',
        'DI Reserves',
        'TGA',
        'GSE/DMFU'
    ]
    colors = [liab_colors['currency'],
              liab_colors['rrp'],
              liab_colors['foreign_repo'],
              liab_colors['reserves'],
              liab_colors['tga'],
              liab_colors['gse_dmfu']]
    for col, color, label in zip(cols,colors,labels):
        fig.add_trace(go.Scatter(x=fed_liabilities_merge.index, y=fed_liabilities_merge[col],
                                 mode='lines+markers',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Liabilities: Components",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=3, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_liabilities_merge.index,
                y=fed_liabilities_merge[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Liabilities: Weekly Averages",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=3, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_liabilities_merge_diff.index,
                y=fed_liabilities_merge_diff[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Liabilities: Weekly Change",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = make_subplots(rows=3, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=fed_liabilities_merge_diff_z.index,
                y=fed_liabilities_merge_diff_z[col],
                mode='lines+markers',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Liabilities: Weekly Change Z-Scored",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
