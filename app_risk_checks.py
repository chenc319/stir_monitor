# risk_checks.py

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
def plot_dash_for_cash_spread(start, end):
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    dash_spread = iorb.join(fed_funds, how='inner', lsuffix='_IORB', rsuffix='_EFFR')
    dash_spread['Spread_bp'] = (dash_spread['EFFR'] - dash_spread['IORB']) * 100
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.step(dash_spread.index, dash_spread['Spread_bp'], where='post', color='skyblue',
            alpha=0.85, linewidth=3)
    ax.set_title('Monitoring the Dash For Cash\nFed Funds - IORB', fontsize=18, fontweight='bold', loc='left')
    ax.set_ylabel('Basis Points', fontsize=13)
    ax.grid(alpha=0.17)
    st.pyplot(fig)
    plt.close(fig)

# 2. NEW SOFR SYSTEM
def plot_new_sofr_system(start, end):
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
    ], axis=1)
    df_bp = new_sofr_system * 100
    df_bp = df_bp.loc[start:end].dropna()
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_bp.index, df_bp['EFFR'], label='EFFR', color='#9bdaf6')
    ax.plot(df_bp.index, df_bp['SOFR 3M'], label='SOFR 3M', color='#4dc6c6')
    ax.plot(df_bp.index, df_bp['SOFR 1M'], label='SOFR 1M', color='#356c82')
    ax.plot(df_bp.index, df_bp['SOFR'], label='SOFR', color='#001f35', linewidth=2)
    ax.plot(df_bp.index, df_bp['SRF'], label='SRF', color='#fbc430')
    ax.plot(df_bp.index, df_bp['RRP'], label='RRP', color='#fdad23')
    ax.set_ylabel("Basis Points")
    ax.set_title("The New SOFR System", fontsize=20, fontweight='bold')
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

# 3. VISIBLE REPO RATE COMPLEX
def plot_repo_rate_complex(start, end):
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    dvp_mnemonic = 'REPO-DVP_AR_OO-P'
    gcf_mnemonic = 'REPO-GCF_AR_AG-P'
    tri_mnemonic = 'REPO-TRI_AR_OO-P'
    def ofr_to_df(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    srf = pd.DataFrame(index=sofr.index)
    srf['SRF'] = rrp['RRPONTSYAWARD'] + 0.25
    dvp_df = ofr_to_df(dvp_mnemonic)
    gcf_df = ofr_to_df(gcf_mnemonic)
    tri_df = ofr_to_df(tri_mnemonic)
    repo_df = merge_dfs([rrp, srf, sofr, dvp_df, gcf_df, tri_df])
    repo_df = repo_df.loc[start:end].dropna()
    repo_df.columns = ['RRP', 'SRF', 'SOFR', 'DVP', 'GCF', 'TRIPARTY']
    colors = {
        'SOFR': '#0B2138', 'DVP': '#48DEE9', 'TRIPARTY': '#7EC0EE',
        'GCF': '#F9D15B', 'SRF': '#F9C846', 'RRP': '#F39C12'
    }
    fig, ax = plt.subplots(figsize=(12, 7))
    for c in repo_df.columns:
        ax.plot(repo_df.index, repo_df[c], label=c, lw=2, color=colors.get(c, None))
    ax.set_ylabel("bps")
    ax.set_title("Visible Repo Rate Complex", fontsize=20, fontweight="bold")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

# 4. SOFR DISTRIBUTION
def plot_sofr_distribution(start, end):
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    sofr1 = pdr.DataReader('SOFR1', 'fred', start, end)
    sofr25 = pdr.DataReader('SOFR25', 'fred', start, end)
    sofr75 = pdr.DataReader('SOFR75', 'fred', start, end)
    sofr99 = pdr.DataReader('SOFR99', 'fred', start, end)
    df = merge_dfs([sofr, sofr1, sofr25, sofr75, sofr99]).loc[start:end].dropna()
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(df.index, df['SOFR'], label='SOFR', color='#9DDCF9', lw=2)
    ax.plot(df.index, df['SOFR1'], label='SOFR 1%', color='#4CD0E9', lw=2)
    ax.plot(df.index, df['SOFR25'], label='SOFR 25%', color='#233852', lw=2)
    ax.plot(df.index, df['SOFR75'], label='SOFR 75%', color='#F5B820', lw=2)
    ax.plot(df.index, df['SOFR99'], label='SOFR 99%', color='#E69B93', lw=2)
    ax.set_ylabel("Bps")
    ax.set_title("SOFR Distribution", fontsize=17, fontweight="bold")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

# 5. FED BALANCE SHEET
def plot_fed_balance_sheet(start, end):
    treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    fed_balance_sheet_merge = merge_dfs([treasury,mbs]).loc[start:end].dropna()
    fed_balance_sheet_merge.columns = ['SOMA Treasury','SOMA MBS']
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(fed_balance_sheet_merge.index, fed_balance_sheet_merge['SOMA Treasury'], color="#46b5ca", lw=3, label='SOMA Treasury')
    ax.plot(fed_balance_sheet_merge.index, fed_balance_sheet_merge['SOMA MBS'], color="#17354c", lw=3, label='SOMA MBS')
    ax.set_title("FED Balance Sheet", fontsize=22, fontweight="bold")
    ax.set_ylabel("Dollars")
    ax.set_ylim(1, 6.5)
    ax.set_yticks(range(1, 7))
    ax.set_yticklabels([f"{x}T" for x in range(1, 7)])
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

# 6. MONITORING RESERVES
def plot_monitoring_reserves(start, end):
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
    rrp_on = pdr.DataReader('RRPONTSYD', 'fred', start, end) / 1e3
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    tri_volume_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
    tri_volume_df['date'] = pd.to_datetime(tri_volume_df['date'])
    tri_volume_df.set_index('date', inplace=True)
    tri_volume_df = tri_volume_df / 1e12
    triparty_rrp_merge = merge_dfs([tri_volume_df,rrp]).dropna()
    tri_repo_diff = pd.DataFrame(triparty_rrp_merge.iloc[:,0] - triparty_rrp_merge.iloc[:,1])
    tri_repo_diff.columns = ['Triparty - RRP']
    reserve_monitor_df = merge_dfs([reserves,tga,rrp,tri_repo_diff,rrp_on]).loc[start:end].dropna()
    reserve_monitor_df.columns = ['Bank Reserves','TGA','RRP','Triparty - RRP','RRP ON']
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(reserve_monitor_df.index, reserve_monitor_df['Bank Reserves'], label="Bank Reserves", color="#aad8ef", lw=3)
    ax.plot(reserve_monitor_df.index, reserve_monitor_df['TGA'], label="TGA", color="#4da3d7", lw=2)
    ax.plot(reserve_monitor_df.index, reserve_monitor_df['RRP'], label="RRP", color="#17293c", lw=2)
    ax.plot(reserve_monitor_df.index, reserve_monitor_df['Triparty - RRP'], label="Triparty - RRP", color="#f5c23e", lw=2)
    ax.plot(reserve_monitor_df.index, reserve_monitor_df['RRP ON'], label="RRP ON", color="#f5b9ad", lw=2)
    ax.set_title("Monitoring reserves", fontsize=22, fontweight="bold")
    ax.set_ylabel("Dollars (Trillions)")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

# 7. FED ACTION VS RESERVE RESPONSE V1
def plot_fed_action_vs_reserve_response(start, end):
    shadow_bank_reserves = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    fed_balance_sheet_merge = merge_dfs([treasury,mbs]).dropna()
    total_fed_balance_sheet = pd.DataFrame(fed_balance_sheet_merge.iloc[:,0] + fed_balance_sheet_merge.iloc[:,1])
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3

    reserve_response_merge = merge_dfs([shadow_bank_reserves, reserves])
    reserve_response_merge.columns = ['bank', 'shadow_bank']
    reserve_response = pd.DataFrame(reserve_response_merge['bank'].resample('M').last() + reserve_response_merge['shadow_bank'].resample('M').last()).diff(1)

    fed_action_merge = merge_dfs([total_fed_balance_sheet,rrp,tga]).dropna()
    fed_action_merge.columns = ['fed_balance_sheet','RRP','TGA']
    fed_action = pd.DataFrame((fed_action_merge['fed_balance_sheet'] - fed_action_merge['RRP'] - fed_action_merge['TGA']).resample('ME').last().diff(1))

    fed_action_vs_reserve_response = merge_dfs([fed_action,reserve_response])
    fed_action_vs_reserve_response.columns = ['Fed Balance Sheet - RRP - TGA','Bank + Shadow Bank Reserves']
    df = fed_action_vs_reserve_response.loc[start:end].dropna()
    fig, ax = plt.subplots(figsize=(12,7))
    ax.plot(df.index, df['Bank + Shadow Bank Reserves'], label='Bank + Shadow Bank Reserves', color='#30b0c1', linewidth=2)
    ax.plot(df.index, df['Fed Balance Sheet - RRP - TGA'], label='FED Balance Sheet - RRP - TGA', color='#17293c', linewidth=2)
    ax.set_ylabel('30-Day Change (Trillions of $)')
    ax.set_title('FED Action Vs Reserve Response (Monthly)')
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

# 8. FED ACTION VS RESERVE RESPONSE V2
def plot_fed_action_vs_reserve_response_v2(start, end):
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
    shadow_bank_reserves = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
    fed_balance_sheet_merge = merge_dfs([treasury,mbs]).dropna()
    total_fed_balance_sheet = pd.DataFrame(fed_balance_sheet_merge.iloc[:,0] + fed_balance_sheet_merge.iloc[:,1])
    rrp = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3

    fed_action_v2_merge = merge_dfs([
        total_fed_balance_sheet.resample('ME').last(),
        reserves.resample('ME').last(),
        shadow_bank_reserves.resample('ME').last()
    ]).dropna()
    reserve_response_v2_merge = merge_dfs([rrp,tga]).resample('ME').last().dropna()
    fed_action_v2 = pd.DataFrame(fed_action_v2_merge.iloc[:,0] - (fed_action_v2_merge.iloc[:,1] + fed_action_v2_merge.iloc[:,2])).diff(1)
    reserve_response_v2 = pd.DataFrame(reserve_response_v2_merge.sum(axis=1).diff(1))
    fed_action_vs_reserve_response_v2 = merge_dfs([fed_action_v2, reserve_response_v2])
    fed_action_vs_reserve_response_v2.columns = ['Fed Balance Sheet - (Bank + Shadow Bank Reserves)', 'RRP + TGA']
    df = fed_action_vs_reserve_response_v2.loc[start:end].dropna()
    fig, ax = plt.subplots(figsize=(12,7))
    ax.plot(df.index, df['Fed Balance Sheet - (Bank + Shadow Bank Reserves)'], label='Fed Balance Sheet - (Bank + Shadow Bank Reserves)', color='#30b0c1', linewidth=2)
    ax.plot(df.index, df['RRP + TGA'], label='RRP + TGA', color='#17293c', linewidth=2)
    ax.set_ylabel('30-Day Change (Trillions of $)')
    ax.set_title('FED Action Vs Reserve Response (Monthly)')
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
