### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- CROSS RATE ------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', '../data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True, how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------- IORB SPREADS ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_iorb_spreads(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'iorb.pkl', 'rb') as file:
        iorb = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)

    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)

    # Align index and scaling to bps
    for df in [sofr, iorb, dvp_df, gcf_df, tri_df]:
        df.index = pd.to_datetime(df.index)
    merged = merge_dfs([sofr, iorb, dvp_df, gcf_df, tri_df]).dropna() * 100
    merged.columns = ['SOFR','IORB','DVP','GCF','TRI']
    merged['SOFR-IORB'] = merged['SOFR'] - merged['IORB']
    merged['DVP-IORB'] = merged['DVP'] - merged['IORB']
    merged['GCF-IORB'] = merged['GCF'] - merged['IORB']
    merged['TRI-IORB'] = merged['TRI'] - merged['IORB']
    merged = merged.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(7, 6))
    # plt.plot(merged.index, merged['SOFR-IORB'],
    #          label='SOFR - IORB', color='#6ECFF6', linewidth=2)
    # plt.plot(merged.index, merged['DVP-IORB'],
    #          label='DVP - IORB', color='#07AFE3', linewidth=2)
    # plt.plot(merged.index, merged['GCF-IORB'],
    #          label='GCF - IORB', color='#FFB400', linewidth=2)
    # plt.plot(merged.index, merged['TRI-IORB'],
    #          label='Triparty - IORB', color='#F57235', linewidth=2)
    # plt.axhline(y=20, color='navy', linestyle='--', linewidth=1)
    # plt.ylabel('Basis Points')
    # plt.title('IORB Spreads', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged.index, y=merged['SOFR-IORB'],
                             name='SOFR - IORB', line=dict(color='#6ECFF6', width=2)))
    fig.add_trace(go.Scatter(x=merged.index, y=merged['DVP-IORB'],
                             name='DVP - IORB', line=dict(color='#07AFE3', width=2)))
    fig.add_trace(go.Scatter(x=merged.index, y=merged['GCF-IORB'],
                             name='GCF - IORB', line=dict(color='#FFB400', width=2)))
    fig.add_trace(go.Scatter(x=merged.index, y=merged['TRI-IORB'],
                             name='Triparty - IORB', line=dict(color='#F57235', width=2)))
    fig.add_hline(y=20, line_dash='dash', line_color='navy', line_width=1)
    fig.update_layout(
        title="IORB Spreads",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------- INTERDEALERS -TRIPARTY GCF - TRIPARTY ---------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_gcf_tri_spread(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'iorb.pkl', 'rb') as file:
        iorb = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)

    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)

    for df in [sofr, iorb, dvp_df, gcf_df, tri_df]:
        df.index = pd.to_datetime(df.index)
    merged = merge_dfs([sofr, iorb, dvp_df, gcf_df, tri_df]).dropna() * 100
    merged.columns = ['SOFR','IORB','DVP','GCF','TRI']
    merged = merged[str(start):str(end)]
    merged['GCF-TRI'] = merged['GCF'] - merged['TRI']

    # ### PLOT ###
    # plt.figure(figsize=(7, 6))
    # plt.plot(merged.index, merged['GCF-TRI'],
    #          label='GCF-TRI', color='#6ECFF6', linewidth=2)
    # plt.axhline(y=20, color='navy', linestyle='--', linewidth=1)
    # plt.ylabel('Basis Points')
    # plt.title('IORB Spreads', fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged.index, y=merged['GCF-TRI'],
                             name='GCF-TRI', line=dict(color='#6ECFF6', width=2)))
    fig.add_hline(y=20, line_dash='dash', line_color='navy', line_width=1)
    fig.update_layout(
        title="GCF - Triparty",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- TRIPARTY - TERM SPREAD ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_triparty_term_spread(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'term1w_df.pkl', 'rb') as file:
        term1w_df = pickle.load(file)

    tri_term_merge = merge_dfs([tri_df, term1w_df]).dropna().resample('W').last()
    tri_term_merge.columns = ['tri','dvp_30d']
    tri_term_merge['diff'] = (tri_term_merge['tri'] - tri_term_merge['dvp_30d'])
    tri_term_merge = tri_term_merge[str(start):str(end)] * 100

    # ### PLOT ###
    # plt.figure(figsize=(8, 6))
    # plt.plot(tri_term_merge.index, tri_term_merge['diff'],
    #          color='#48DEE9', label='Term Spread Proxy', linewidth=2)
    # plt.title('Tri Party Term Spread (ON vs. <30d', fontsize=16, fontweight='bold')
    # plt.ylabel('Basis Points')
    # plt.xlabel('')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(False)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tri_term_merge.index, y=tri_term_merge['diff'],
                             name='Term Spread Proxy', line=dict(color='#48DEE9', width=2)))
    fig.update_layout(
        title="Tri Party Term Spread (ON vs. <30d)",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- THE NEW SYSTEM ---------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sofr_effr_chart(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)
    sofr.index = pd.to_datetime(sofr.index)
    fed_funds.index = pd.to_datetime(fed_funds.index)
    sofr_effr_merge = merge_dfs([sofr, fed_funds]).dropna()
    sofr_effr_merge['sofr-effr'] = sofr_effr_merge['SOFR'] - sofr_effr_merge['EFFR']
    sofr_effr_merge['sofr-effr_ma'] = sofr_effr_merge['sofr-effr'].rolling(21).mean()
    sofr_effr_merge = sofr_effr_merge[str(start):str(end)] * 100

    # ### PLOT ###
    # plt.figure(figsize=(8, 6))
    # plt.plot(sofr_effr_merge.index, sofr_effr_merge['sofr-effr'],
    #          color='#48DEE9', label='SOFR-EFFR', linewidth=2)
    # plt.plot(sofr_effr_merge.index, sofr_effr_merge['sofr-effr_ma'],
    #          color='#0B2138', label='SOFR-EFFR 1 Month Index', linewidth=2)
    # plt.title('The New System', fontsize=16, fontweight='bold')
    # plt.ylabel('Basis Points')
    # plt.xlabel('')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(False)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sofr_effr_merge.index, y=sofr_effr_merge['sofr-effr'],
                             name='SOFR-EFFR',
                             line=dict(color='#48DEE9', width=2)))
    fig.add_trace(go.Scatter(x=sofr_effr_merge.index, y=sofr_effr_merge['sofr-effr_ma'],
                             name='SOFR-EFFR 1 Month MA',
                             line=dict(color='#0B2138', width=2)))
    fig.update_layout(
        title="The New System: SOFR-EFFR",
        yaxis_title="Basis Points",
        hovermode='x unified',
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- DOLLAR LENDING COMPLEX ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_dollar_lending_complex(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'iorb.pkl', 'rb') as file:
        iorb = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp.pkl', 'rb') as file:
        rrp = pickle.load(file)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
        sofr = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'rb') as file:
        tri_df = pickle.load(file)

    for df in [rrp, sofr, fed_funds, iorb]:
        df.index = pd.to_datetime(df.index)
    srf = pd.DataFrame(index=sofr.index)
    srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    repo_rate_complex_df = merge_dfs([rrp,srf,sofr,dvp_df,gcf_df,tri_df,fed_funds,iorb])['2025-04-01':str(end)]
    repo_rate_complex_df.columns = ['RRP','SRF','SOFR','DVP','GCF','TRIPARTY','EFFR','IORB']
    repo_rate_complex_df = repo_rate_complex_df.dropna() * 100

    colors = {
        'SOFR':     '#0B2138',
        'DVP':      '#48DEE9',
        'TRIPARTY': '#7EC0EE',
        'GCF':      '#F9D15B',
        'SRF':      '#F9C846',
        'RRP':      '#F39C12',
        'EFFR':     '#023e8a',
        'IORB':     '#808080',
    }

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['RRP'], lw=2, color=colors['RRP'], label="RRP")
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SRF'], lw=2, color=colors['SRF'], label="SRF",
    #          alpha=0.95)
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SOFR'], lw=2, color=colors['SOFR'], label="SOFR")
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['DVP'], lw=2, color=colors['DVP'], label="DVP")
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['GCF'], lw=2, color=colors['GCF'], label="GCF")
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['TRIPARTY'], lw=2, color=colors['TRIPARTY'],
    #          label="TRIPARTY")
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['EFFR'], lw=2, color=colors['EFFR'], label="EFFR")
    # plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['IORB'], lw=2, color=colors['TRIPARTY'], label="IORB")
    # plt.ylabel("bps")
    # plt.title("Visible Repo Rate", fontsize=20, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    for col in ['RRP','SRF','SOFR','DVP','GCF','TRIPARTY','EFFR','IORB']:
        fig.add_trace(go.Scatter(x=repo_rate_complex_df.index,
                                 y=repo_rate_complex_df[col],
                                 name=col, line=dict(color=colors.get(col, "#666"), width=2)))
    fig.update_layout(
        title="Visible Repo Rate",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- END OF QUARTER SPREADS ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_end_of_quarter_spreads(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'gc_df.pkl', 'rb') as file:
        gc_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)

    fed_funds.index = pd.to_datetime(fed_funds.index)
    quarter_spreads_merge = merge_dfs([gc_df, dvp_df, gcf_df, fed_funds]).resample('QE').last()
    quarter_spreads_merge.columns = ['gc','dvp','gcf','effr']
    quarter_spreads_merge = quarter_spreads_merge.loc[str(start):str(end)]
    quarter_spreads_merge['gc_effr'] = (quarter_spreads_merge['gc'] - quarter_spreads_merge['effr']) * 100
    quarter_spreads_merge['gc_dvp'] = (quarter_spreads_merge['gc'] - quarter_spreads_merge['dvp']) * 100
    quarter_spreads_merge['gc_gcf'] = (quarter_spreads_merge['gc'] - quarter_spreads_merge['gcf']) * 100
    quarter_spreads_merge = quarter_spreads_merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(quarter_spreads_merge.index, quarter_spreads_merge['gc_effr'],
    #          label='GC-EFFR', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(quarter_spreads_merge.index, quarter_spreads_merge['gc_dvp'],
    #          label='GC-DVP', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(quarter_spreads_merge.index, quarter_spreads_merge['gc_gcf'],
    #          label='GC-GCF', color='#233852', lw=2)  # dark blue
    # plt.ylabel("Basis Points")
    # plt.title("End of Quarter Spreads", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quarter_spreads_merge.index, y=quarter_spreads_merge['gc_effr'],
                             name="GC-EFFR", line=dict(color="#9DDCF9", width=2)))
    fig.add_trace(go.Scatter(x=quarter_spreads_merge.index, y=quarter_spreads_merge['gc_dvp'],
                             name="GC-DVP", line=dict(color="#4CD0E9", width=2)))
    fig.add_trace(go.Scatter(x=quarter_spreads_merge.index, y=quarter_spreads_merge['gc_gcf'],
                             name="GC-GCF", line=dict(color="#233852", width=2)))
    fig.update_layout(
        title="End of Quarter Spreads",
        yaxis_title="Basis Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- END OF MONTH SPREADS ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_end_of_month_spreads(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'gc_df.pkl', 'rb') as file:
        gc_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'rb') as file:
        dvp_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'rb') as file:
        gcf_df = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
        fed_funds = pickle.load(file)
    with open(Path(DATA_DIR) / 'rrp.pkl', 'rb') as file:
        rrp = pickle.load(file)
    monthly_spreads_merge = merge_dfs([gc_df, dvp_df, gcf_df, fed_funds, rrp]).resample('ME').last()
    monthly_spreads_merge.columns = ['gc','dvp','gcf','effr','rrp']
    monthly_spreads_merge = monthly_spreads_merge.loc[str(start):str(end)]
    monthly_spreads_merge['gc_effr'] = (monthly_spreads_merge['gc'] - monthly_spreads_merge['effr']) * 100
    monthly_spreads_merge['gc_dvp'] = (monthly_spreads_merge['gc'] - monthly_spreads_merge['dvp']) * 100
    monthly_spreads_merge['gc_gcf'] = (monthly_spreads_merge['gc'] - monthly_spreads_merge['gcf']) * 100
    monthly_spreads_merge['gc_rrp'] = (monthly_spreads_merge['gc'] - monthly_spreads_merge['rrp']) * 100
    monthly_spreads_merge = monthly_spreads_merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_effr'],
    #          label="GC-EFFR", color="#f8b62d", lw=2)
    # plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_dvp'],
    #          label="GC-DVP", color="#f8772d", lw=2)
    # plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_gcf'],
    #          label="GC-GCF", color="#2f90c5", lw=2)
    # plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_rrp'],
    #          label="GC-RRP", color="#67cbe7", lw=2)
    # plt.title("End of Month Spreads", fontsize=22, fontweight="bold")
    # plt.ylabel("Basis Points")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_effr'],
                             name="GC-EFFR", line=dict(color="#f8b62d", width=2)))
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_dvp'],
                             name="GC-DVP", line=dict(color="#f8772d", width=2)))
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_gcf'],
                             name="GC-GCF", line=dict(color="#2f90c5", width=2)))
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_rrp'],
                             name="GC-RRP", line=dict(color="#67cbe7", width=2)))
    fig.update_layout(
        title="End of Month Spreads",
        yaxis_title="Basis Points",
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

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- SOFR FLOOR AND CEILING ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

# def plot_sofr_floor_ceiling(start, end, **kwargs):
#     with open(Path(DATA_DIR) / 'rrp.pkl', 'rb') as file:
#         rrp = pickle.load(file)
#     with open(Path(DATA_DIR) / 'sofr.pkl', 'rb') as file:
#         sofr = pickle.load(file)
#     for df in [sofr, rrp]:
#         df.index = pd.to_datetime(df.index)
#     srf = pd.DataFrame(index=sofr.index)
#     srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25
#     sofr_floor_ceiling_merge = merge_dfs([sofr, rrp, srf])['2025-04-01':str(end)].dropna() * 100
#     sofr_floor_ceiling_merge.columns = ['SOFR','RRP','SRF']
#
#     # ### PLOT ###
#     # plt.figure(figsize=(7, 6))
#     # plt.plot(sofr_floor_ceiling_merge.index, sofr_floor_ceiling_merge['SOFR'],
#     #          label='SOFR', color='#07AFE3', linewidth=2)
#     # plt.plot(sofr_floor_ceiling_merge.index, sofr_floor_ceiling_merge['SRF'],
#     #          label='SRF', color='#6ECFF6', linewidth=2)
#     # plt.plot(sofr_floor_ceiling_merge.index, sofr_floor_ceiling_merge['RRP'],
#     #          label='RRP', color='#FFB400', linewidth=2)
#     # plt.ylabel('Basis Points')
#     # plt.title('SOFR- Floor and Ceiling', fontweight='bold')
#     # plt.ylim(415, 455)
#     # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
#     # plt.tight_layout()
#     # plt.show()
#
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=sofr_floor_ceiling_merge.index,
#                              y=sofr_floor_ceiling_merge['SOFR'],
#                              name='SOFR', line=dict(color='#07AFE3', width=2)))
#     fig.add_trace(go.Scatter(x=sofr_floor_ceiling_merge.index,
#                              y=sofr_floor_ceiling_merge['SRF'],
#                              name='SRF', line=dict(color='#6ECFF6', width=2)))
#     fig.add_trace(go.Scatter(x=sofr_floor_ceiling_merge.index,
#                              y=sofr_floor_ceiling_merge['RRP'],
#                              name='RRP', line=dict(color='#FFB400', width=2)))
#     fig.update_layout(
#         title='SOFR- Floor and Ceiling',
#         yaxis_title='Basis Points',
#         hovermode='x unified',
#         yaxis_range=[415, 455]
#     )
#     st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------- UNSECURED LENDING FLOOR AND CEILING ----------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

# def plot_unsecured_lending_floor_ceiling(start, end, **kwargs):
#     with open(Path(DATA_DIR) / 'rrp.pkl', 'rb') as file:
#         rrp = pickle.load(file)
#     with open(Path(DATA_DIR) / 'iorb.pkl', 'rb') as file:
#         iorb = pickle.load(file)
#     with open(Path(DATA_DIR) / 'fed_funds.pkl', 'rb') as file:
#         fed_funds = pickle.load(file)
#     for df in [fed_funds, iorb, rrp]:
#         df.index = pd.to_datetime(df.index)
#     srf = pd.DataFrame(index=fed_funds.index)
#     srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25
#     unsecured_lending_merge = merge_dfs([fed_funds, iorb, srf, rrp])['2025-04-01':str(end)].dropna() * 100
#     unsecured_lending_merge.columns = ['EFFR','IORB','SRF','RRP']
#
#     # ### PLOT ###
#     # plt.figure(figsize=(7, 6))
#     # plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['EFFR'],
#     #          label='EFFR', color='#6ECFF6', linewidth=2)
#     # plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['IORB'],
#     #          label='IORB', color='#07AFE3', linewidth=2)
#     # plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['SRF'],
#     #          label='Discount Window', color='#FFB400', linewidth=2)
#     # plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['RRP'],
#     #          label='RRP', color='#F57235', linewidth=2)
#     # plt.axhline(y=20, color='navy', linestyle='--', linewidth=1)
#     # plt.ylabel('Basis Points')
#     # plt.title('Unsecured Lending - Floor and Ceiling', fontweight='bold')
#     # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
#     # plt.tight_layout()
#     # plt.ylim(415, 455)
#     # plt.show()
#
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=unsecured_lending_merge.index,
#                              y=unsecured_lending_merge['EFFR'],
#                              name='EFFR', line=dict(color='#6ECFF6', width=2)))
#     fig.add_trace(go.Scatter(x=unsecured_lending_merge.index,
#                              y=unsecured_lending_merge['IORB'],
#                              name='IORB', line=dict(color='#07AFE3', width=2)))
#     fig.add_trace(go.Scatter(x=unsecured_lending_merge.index,
#                              y=unsecured_lending_merge['SRF'],
#                              name='Discount Window', line=dict(color='#FFB400', width=2)))
#     fig.add_trace(go.Scatter(x=unsecured_lending_merge.index,
#                              y=unsecured_lending_merge['RRP'],
#                              name='RRP', line=dict(color='#F57235', width=2)))
#     fig.add_hline(y=20, line_dash='dash', line_color='navy', line_width=1)
#     fig.update_layout(
#         title='Unsecured Lending - Floor and Ceiling',
#         yaxis_title='Basis Points',
#         hovermode='x unified',
#         yaxis_range=[415, 455]
#     )
#     st.plotly_chart(fig, use_container_width=True)
