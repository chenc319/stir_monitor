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
from io import StringIO
from pandas_datareader import data as pdr

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
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=mmf_repo_allocations.index,
                             y=mmf_repo_allocations['Treasury Repo'],
                             mode='lines+markers',
                             name='Treasury Repo',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="MMF's Investments in Repo Markets",
        yaxis_title="$ (Trillions)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------- MONEY MARKET FUNDS INVOLVEMENTS IN ON REPO SPECIFICALLY TO CAPTURE STIR ACTIVITY ----------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_mmf_on_repo(start, end, **kwargs):
    mmf_involvement_on_repo = pd.DataFrame(requests.get('https://data.financialresearch.gov/'
                                          'v1/series/timeseries?mnemonic=MMF-MMF_RP_OO-M').json(),
                                          columns = ['Date','Values'])
    mmf_involvement_on_repo.index = pd.to_datetime(mmf_involvement_on_repo['Date'].values)
    mmf_involvement_on_repo.drop('Date', axis=1, inplace=True)
    mmf_involvement_on_repo = mmf_involvement_on_repo[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(mmf_involvement_on_repo.index, mmf_involvement_on_repo['Values'],
    #          color='#9DDCF9', lw=2)  # light blue
    # plt.ylabel("$ (Trillions)")
    # plt.title("MMF's Investments in Overnight/Open Repo", fontsize=17, fontweight="bold")
    # plt.tight_layout()
    # plt.show()

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

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- PRIVATE INVESTMENT FUNDS ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_private_investments(start, end, **kwargs):
    url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=60000"
    response = requests.get(url)
    cftc_all_futures = pd.read_csv(StringIO(response.text))
    cftc_all_futures.columns
    cftc_all_futures.index = pd.to_datetime(cftc_all_futures['report_date_as_yyyy_mm_dd'].values)
    cftc_all_futures.drop('report_date_as_yyyy_mm_dd',axis=1)

    fed_funds_futures = cftc_all_futures[
        cftc_all_futures['contract_market_name'] == 'FED FUNDS']
    fed_funds_futures = fed_funds_futures.sort_index()
    sofr3m_futures = cftc_all_futures[
        cftc_all_futures['contract_market_name'] == 'SOFR-3M']
    sofr3m_futures = sofr3m_futures.sort_index()
    sofr1m_futures = cftc_all_futures[
        cftc_all_futures['contract_market_name'] == 'SOFR-1M']
    sofr1m_futures = sofr1m_futures.sort_index()

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(fed_funds_futures.index,
    #          fed_funds_futures['lev_money_positions_long'],
    #          color='#9DDCF9', lw=2)
    # plt.plot(sofr3m_futures.index,
    #          sofr3m_futures['lev_money_positions_long'],
    #          color='#4CD0E9', lw=2)
    # plt.plot(sofr1m_futures.index,
    #          sofr1m_futures['lev_money_positions_long'],
    #          color='#233852', lw=2)
    # plt.ylabel("$ (Trillions)")
    # plt.title("MMF's Investments in Overnight/Open Repo", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    long_merge_df = merge_dfs([fed_funds_futures['lev_money_positions_long']*5000000,
                               sofr3m_futures['lev_money_positions_long']*2500,
                               sofr1m_futures['lev_money_positions_long']*4167]).dropna()
    long_merge_df.columns = ['fedfunds', 'sofr3m', 'sofr1m']
    long_merge_df = long_merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=long_merge_df.index,
                             y=long_merge_df['fedfunds'],
                             mode='lines+markers',
                             name='Fed Funds',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="Private Investments Long Positions - Fed Funds",
        yaxis_title="$",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    short_merge_df = merge_dfs([fed_funds_futures['lev_money_positions_short']*5000000,
                                sofr3m_futures['lev_money_positions_short']*2500,
                                sofr1m_futures['lev_money_positions_short']*4167]).dropna()
    short_merge_df.columns = ['fedfunds', 'sofr3m', 'sofr1m']
    short_merge_df = short_merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=short_merge_df.index,
                             y=short_merge_df['fedfunds'],
                             mode='lines+markers',
                             name='Fed Funds',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="Private Investments Short Positions - Fed Funds",
        yaxis_title="$",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    net_merge_df = long_merge_df - short_merge_df
    net_merge_df = net_merge_df[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=net_merge_df.index,
                             y=net_merge_df['fedfunds'],
                             mode='lines+markers',
                             name='Fed Funds',
                             line=dict(color="#46b5ca", width=3)))
    fig.update_layout(
        title="Private Investments Net Positions - Fed Funds",
        yaxis_title="$",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=long_merge_df.index,
                             y=long_merge_df['sofr1m'],
                             mode='lines+markers',
                             name='SOFR 1M',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=long_merge_df.index,
                             y=long_merge_df['sofr3m'],
                             mode='lines+markers',
                             name='SOFR 3M',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="Private Investments Long Positions - SOFR",
        yaxis_title="$",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=short_merge_df.index,
                             y=short_merge_df['sofr1m'],
                             mode='lines+markers',
                             name='SOFR 1M',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=short_merge_df.index,
                             y=short_merge_df['sofr3m'],
                             mode='lines+markers',
                             name='SOFR 3M',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="Private Investments Short Positions - SOFR",
        yaxis_title="$",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=net_merge_df.index,
                             y=net_merge_df['sofr1m'],
                             mode='lines+markers',
                             name='SOFR 1M',
                             line=dict(color="#4CD0E9", width=3)))
    fig.add_trace(go.Scatter(x=net_merge_df.index,
                             y=net_merge_df['sofr3m'],
                             mode='lines+markers',
                             name='SOFR 3M',
                             line=dict(color="#233852", width=3)))
    fig.update_layout(
        title="Private Investments Net Positions - SOFR",
        yaxis_title="$",
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
#                              mode='lines+markers',
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
    mmf_repo = pdr.DataReader('BOGZ1FL632051000Q',
                              'fred', start, end) * 1e6
    brokers_dealers_repo = pdr.DataReader('BOGZ1FL662051003Q',
                                          'fred', start, end) * 1e6
    nonfinancial_corporations = pdr.DataReader('SRPSABSNNCB',
                                          'fred', start, end) * 1e9
    hedge_funds = pdr.DataReader('BOGZ1FL622051003Q',
                                          'fred', start, end) * 1e6
    us_chartered_depository_inst = pdr.DataReader('BOGZ1FL762051005Q',
                                          'fred', start, end) * 1e6
    all_sectors = pdr.DataReader('BOGZ1FL892050005Q',
                                 'fred', start, end) * 1e6


    merge_df = merge_dfs([mmf_repo,brokers_dealers_repo])


### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- SHADOW BANK LIABILITIES ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_shadow_bank_liabilities(start, end, **kwargs):
    ### OFR DATA PULLS ###
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    all_repo_venus = ['REPO-TRI_TV_TOT-P',
                      'REPO-DVP_TV_TOT-P',
                      'REPO-GCF_TV_TOT-P']
    repo_merge_df = pd.DataFrame()
    for x in all_repo_venus:
        volume_df = pd.DataFrame(requests.get(base_url + x).json(), columns=["date", "value"])
        volume_df['date'] = pd.to_datetime(volume_df['date'])
        volume_df.index = volume_df['date'].values
        volume_df.drop('date', axis=1, inplace=True)
        repo_merge_df = merge_dfs([repo_merge_df,volume_df])
    repo_merge_df.columns = ['tri','dvp','gcf']
    total_repo = pd.DataFrame(repo_merge_df.sum(axis=1),
                              columns = ['total_repo'])

    ### FRED DATA PULLS ###
    brokers_dealers_repo = pdr.DataReader('BOGZ1FL662151003Q',
                                          'fred', start, end) * 1e6
    hedge_funds = pdr.DataReader('BOGZ1FL622151005Q',
                                 'fred', start, end) * 1e6
    reit = pdr.DataReader('BOGZ1FL642151073Q',
                          'fred', start, end) * 1e6
    all_sectors = pdr.DataReader('BOGZ1FL892150005Q',
                                 'fred', start, end) * 1e6
    other_financial_corporations = pdr.DataReader('BOGZ1FL812150005Q',
                                        'fred', start, end) * 1e6
    # private_depository_inst = pdr.DataReader('BOGZ1FL702150005Q',
    #                                          'fred', start, end) * 1e6
    # monetary_authority = pdr.DataReader('BOGZ1FL712151103Q',
    #                                     'fred', start, end) * 1e6
    # us_chartered_institutions = pdr.DataReader('BOGZ1FL762151003Q',
    #                                     'fred', start, end) * 1e6

    merge_df = merge_dfs([brokers_dealers_repo,
                          hedge_funds,
                          reit,
                          total_repo]).dropna()
    merge_df.columns = ['Broker/Dealer','HFs','REITs','Total Repo']

    merge_df['bd_pct'] = merge_df['Broker/Dealer'] / merge_df['Total Repo']
    merge_df['hf_pct'] = merge_df['HFs'] / merge_df['Total Repo']
    merge_df['reit_pct'] = merge_df['REITs'] / merge_df['Total Repo']

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
                             mode='lines+markers',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['HFs'],
                             mode='lines+markers',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['REITs'],
                             mode='lines+markers',
                             name='REITs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['Other Financial Corps'],
                             mode='lines+markers',
                             name='Other Financial Corps',
                             line=dict(color="#F9D15B", width=3)))
    fig.update_layout(
        title="Shadow Banks: Repo Liabilities",
        yaxis_title="$",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['bd_pct'],
                             mode='lines+markers',
                             name='Broker/Dealer',
                             line=dict(color="#0B2138", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['hf_pct'],
                             mode='lines+markers',
                             name='HFs',
                             line=dict(color="#48DEE9", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['reit_pct'],
                             mode='lines+markers',
                             name='REITs',
                             line=dict(color="#7EC0EE", width=3)))
    fig.add_trace(go.Scatter(x=merge_df.index,
                             y=merge_df['others_pct'],
                             mode='lines+markers',
                             name='Other Financial Corps',
                             line=dict(color="#F9D15B", width=3)))
    fig.update_layout(
        title="Shadow Banks: Repo Liabilities",
        yaxis_title="% of Total Repo",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)





