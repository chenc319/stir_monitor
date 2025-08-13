# app_risk_checks.py

import pandas as pd
import matplotlib.pyplot as plt
import functools as ft
import requests
from pandas_datareader import data as pdr
import streamlit as st

# Utility function to merge multiple DataFrames
def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

# 1. DASH FOR CASH SPREAD
def plot_dash_for_cash_spread(start, end, show_legend=True, log_y=False, zoom_days=0):
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    dash_spread = iorb.join(fed_funds, how='inner', lsuffix='_IORB', rsuffix='_EFFR')
    dash_spread['Spread_bp'] = (dash_spread['EFFR'] - dash_spread['IORB']) * 100
    if zoom_days > 0:
        dash_spread = dash_spread.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.step(dash_spread.index, dash_spread['Spread_bp'], where='post',
            color='skyblue', alpha=0.85, linewidth=3)
    ax.set_title('Monitoring the Dash For Cash\nFed Funds - IORB', fontsize=18, fontweight='bold', loc='left')
    ax.set_ylabel('Basis Points', fontsize=13)
    if log_y:
        ax.set_yscale('log')
    ax.grid(alpha=0.17)
    if show_legend:
        ax.legend(["EFFR - IORB"])
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 2. NEW SOFR SYSTEM
def plot_new_sofr_system(start, end, show_legend=True, log_y=False, zoom_days=0):
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    sofr_1m = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
    sofr_3m = pdr.DataReader('SOFR90DAYAVG', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index)
    srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    new_sofr_system = pd.concat([
        fed_funds.rename(columns={'EFFR': 'EFFR'}),
        sofr.rename(columns={'SOFR': 'SOFR'}),
        sofr_1m.rename(columns={'SOFR30DAYAVG': 'SOFR 1M'}),
        sofr_3m.rename(columns={'SOFR90DAYAVG': 'SOFR 3M'}),
        srf,
        rrp.rename(columns={'RRPONTSYAWARD': 'RRP'})
    ], axis=1) * 100
    df_bp = new_sofr_system.loc['2025-04-01':].dropna()
    if zoom_days > 0:
        df_bp = df_bp.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_bp.index, df_bp['EFFR'], label='EFFR', color='#9bdaf6')
    ax.plot(df_bp.index, df_bp['SOFR 3M'], label='SOFR 3M', color='#4dc6c6')
    ax.plot(df_bp.index, df_bp['SOFR 1M'], label='SOFR 1M', color='#356c82')
    ax.plot(df_bp.index, df_bp['SOFR'], label='SOFR', color='#001f35', linewidth=2)
    ax.plot(df_bp.index, df_bp['SRF'], label='SRF', color='#fbc430')
    ax.plot(df_bp.index, df_bp['RRP'], label='RRP', color='#fdad23')
    ax.set_ylabel("Basis Points")
    ax.set_title("The New SOFR System", fontsize=20, fontweight='bold')
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 3. VISIBLE REPO RATE COMPLEX
def plot_repo_rate_complex(start, end, show_legend=True, log_y=False, zoom_days=0):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    def ofr_to_df(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')

    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index); srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    dvp_df = ofr_to_df('REPO-DVP_AR_OO-P')
    gcf_df = ofr_to_df('REPO-GCF_AR_AG-P')
    tri_df = ofr_to_df('REPO-TRI_AR_OO-P')
    repo_df = merge_dfs([rrp, srf, sofr, dvp_df, gcf_df, tri_df]).loc['2025-04-01':].dropna()
    repo_df.columns = ['RRP', 'SRF', 'SOFR', 'DVP', 'GCF', 'TRIPARTY']
    if zoom_days > 0:
        repo_df = repo_df.iloc[-zoom_days:]
    colors = {'SOFR': '#0B2138', 'DVP': '#48DEE9', 'TRIPARTY': '#7EC0EE', 'GCF': '#F9D15B', 'SRF': '#F9C846', 'RRP': '#F39C12'}
    fig, ax = plt.subplots(figsize=(12, 7))
    for c in repo_df.columns:
        ax.plot(repo_df.index, repo_df[c], label=c, lw=2, color=colors.get(c, None))
    ax.set_ylabel("Basis Points")
    ax.set_title("Visible Repo Rate Complex", fontsize=20, fontweight="bold")
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 4. SOFR DISTRIBUTION
def plot_sofr_distribution(start, end, show_legend=True, log_y=False, zoom_days=0):
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    sofr1 = pdr.DataReader('SOFR1', 'fred', start, end)
    sofr25 = pdr.DataReader('SOFR25', 'fred', start, end)
    sofr75 = pdr.DataReader('SOFR75', 'fred', start, end)
    sofr99 = pdr.DataReader('SOFR99', 'fred', start, end)
    df = merge_dfs([sofr, sofr1, sofr25, sofr75, sofr99]).loc['2025-04-01':].dropna()
    if zoom_days > 0:
        df = df.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(df.index, df['SOFR'], label='SOFR', color='#9DDCF9', lw=2)
    ax.plot(df.index, df['SOFR1'], label='SOFR 1%', color='#4CD0E9', lw=2)
    ax.plot(df.index, df['SOFR25'], label='SOFR 25%', color='#233852', lw=2)
    ax.plot(df.index, df['SOFR75'], label='SOFR 75%', color='#F5B820', lw=2)
    ax.plot(df.index, df['SOFR99'], label='SOFR 99%', color='#E69B93', lw=2)
    ax.set_ylabel("Basis Points")
    ax.set_title("SOFR Distribution", fontsize=17, fontweight="bold")
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 5. FED BALANCE SHEET
def plot_fed_balance_sheet(start, end, show_legend=True, log_y=False, zoom_days=0):
    treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    df = merge_dfs([treasury, mbs]).loc[start:end].dropna()
    df.columns = ['SOMA Treasury', 'SOMA MBS']
    if zoom_days > 0:
        df = df.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df.index, df['SOMA Treasury'], color="#46b5ca", lw=3, label='SOMA Treasury')
    ax.plot(df.index, df['SOMA MBS'], color="#17354c", lw=3, label='SOMA MBS')
    ax.set_title("FED Balance Sheet", fontsize=22, fontweight="bold")
    ax.set_ylabel("Dollars (Trillions)")
    ax.set_ylim(1, 6.5)
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=2)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 6. MONITORING RESERVES
def plot_monitoring_reserves(start, end, show_legend=True, log_y=False, zoom_days=0):
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    rrp_on = pdr.DataReader('RRPONTSYD', 'fred', start, end) / 1e3
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    tri_volume_df = pd.DataFrame(requests.get('https://data.financialresearch.gov/v1/series/timeseries?mnemonic=REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
    tri_volume_df['date'] = pd.to_datetime(tri_volume_df['date'])
    tri_volume_df.set_index('date', inplace=True)
    tri_volume_df = tri_volume_df / 1e12
    triparty_rrp_merge = merge_dfs([tri_volume_df, rrp]).dropna()
    tri_repo_diff = pd.DataFrame(triparty_rrp_merge.iloc[:, 0] - triparty_rrp_merge.iloc[:, 1], columns=['Triparty - RRP'])
    df = merge_dfs([reserves, tga, rrp, tri_repo_diff, rrp_on]).loc[start:end].dropna()
    df.columns = ['Bank Reserves', 'TGA', 'RRP', 'Triparty - RRP', 'RRP ON']
    if zoom_days > 0:
        df = df.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(12, 7))
    for col, color, lw in [
        ('Bank Reserves', "#aad8ef", 3),
        ('TGA', "#4da3d7", 2),
        ('RRP', "#17293c", 2),
        ('Triparty - RRP', "#f5c23e", 2),
        ('RRP ON', "#f5b9ad", 2)
    ]:
        ax.plot(df.index, df[col], label=col, color=color, lw=lw)
    ax.set_title("Monitoring reserves", fontsize=22, fontweight="bold")
    ax.set_ylabel("Dollars (Trillions)")
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 7. FED ACTION VS RESERVE RESPONSE
def plot_fed_action_vs_reserve_response(start, end, show_legend=True, log_y=False, zoom_days=0):
    fed_action = pdr.DataReader('WALCL', 'fred', start, end) / 1e6
    reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    df = merge_dfs([fed_action, reserves_volume])
    df.columns = ['Fed Action', 'Reserve Response']
    df = df.resample('ME').last().diff(1).loc[start:end].dropna()
    if zoom_days > 0:
        df = df.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df.index, df['Fed Action'], label='Fed Action', color='#30b0c1', linewidth=2)
    ax.plot(df.index, df['Reserve Response'], label='Reserve Response', color='#17293c', linewidth=2)
    ax.set_ylabel('30-Day Change (Trillions of $)')
    ax.set_title('FED Action Vs Reserve Response')
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# 8. FED ACTION VS RESERVE RESPONSE V2
def plot_fed_action_vs_reserve_response_v2(start, end, show_legend=True, log_y=False, zoom_days=0):
    fed_action = pdr.DataReader('WALCL', 'fred', start, end) / 1e6
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    reserve_response_v2_merge = merge_dfs([rrp, tga_volume]).resample('ME').last()
    reserve_response_v2 = pd.DataFrame(reserve_response_v2_merge.sum(axis=1).diff(1))
    df = merge_dfs([fed_action.resample('ME').last().diff(1), reserve_response_v2])
    df.columns = ['Fed Action', 'RRP + TGA']
    df = df.loc[start:end].dropna()
    if zoom_days > 0:
        df = df.iloc[-zoom_days:]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df.index, df['Fed Action'], label='Fed Action', color='#30b0c1', linewidth=2)
    ax.plot(df.index, df['RRP + TGA'], label='RRP + TGA', color='#17293c', linewidth=2)
    ax.set_ylabel('30-Day Change (Trillions of $)')
    ax.set_title('FED Action Vs Reserve Response')
    if log_y:
        ax.set_yscale('log')
    if show_legend:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
