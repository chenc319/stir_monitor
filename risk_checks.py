### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- RISK CHECKS ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import datetime
from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import functools as ft
import requests
fred = Fred(api_key='6905137c26f03db5c8c09f70b7839150')

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
### -------------------------------------------- FED FUNDS - IORB -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

'''
Background
- Fed funds: overnight rate that banks pay to park their cash with each other 
- IORB: the interest the fed pays on excess reserves banks hold at the Fed 

Significance
- when the spread is positive, banks are scrambling for cash and there are problems with liquidity 
- when the spread is negative, their is often excess cash 

Disclaimers
- Before July 29th, IOER and IORR were replaced with a single rate, the IORB

'''

### FRED DATA PULL ###
iorb = pdr.DataReader('IORB', 'fred', start, end)
iorb.index = pd.to_datetime(iorb.index.values)
fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
fed_funds.index = pd.to_datetime(fed_funds.index.values)
sofr = pdr.DataReader('SOFR', 'fred', start, end)
sofr.index = pd.to_datetime(sofr.index.values)
sofr_1m = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
sofr_1m.index = pd.to_datetime(sofr_1m.index.values)
sofr_3m = pdr.DataReader('SOFR90DAYAVG', 'fred', start, end)
sofr_3m.index = pd.to_datetime(sofr_3m.index.values)
rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
rrp.index = pd.to_datetime(rrp.index.values)
srf = pd.DataFrame(index=sofr.index)
srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25

### CALCULATE DASH FOR CASH AND IN BPS ###
dash_for_cash_spread = iorb.join(fed_funds, how='inner', lsuffix='_IORB', rsuffix='_EFFR')
dash_for_cash_spread['Spread_bp'] = (dash_for_cash_spread['EFFR'] - dash_for_cash_spread['IORB']) * 100

### PLOT ###
plt.figure(figsize=(10,5))
plt.step(dash_for_cash_spread.index, dash_for_cash_spread['Spread_bp'], where='post', color='skyblue', alpha=0.85, linewidth=3)
plt.title('Monitoring the Dash For Cash\nFed Funds - IORB', fontsize=18, fontweight='bold', loc='left')
plt.ylabel('Basis Points', fontsize=13)
plt.xlabel('')
plt.grid(alpha=0.17)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- NEW SOFR SYSTEM --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

new_sofr_system = pd.concat([
    fed_funds.rename(columns={'EFFR': 'EFFR'}),
    sofr.rename(columns={'SOFR': 'SOFR'}),
    sofr_1m.rename(columns={'SOFR30DAYAVG': 'SOFR 1M'}),
    sofr_3m.rename(columns={'SOFR90DAYAVG': 'SOFR 3M'}),
    srf,
    rrp.rename(columns={'RRPONTSYAWARD': 'RRP'})
], axis=1)
new_sofr_system_bp = new_sofr_system * 100  # Convert to basis points
new_sofr_system_bp = new_sofr_system_bp['2025-04-01':].dropna()

### PLOT ###
plt.figure(figsize=(12,7))
plt.plot(new_sofr_system_bp.index, new_sofr_system_bp['EFFR'], label='EFFR', color='#9bdaf6')
plt.plot(new_sofr_system_bp.index, new_sofr_system_bp['SOFR 3M'], label='SOFR 3M', color='#4dc6c6')
plt.plot(new_sofr_system_bp.index, new_sofr_system_bp['SOFR 1M'], label='SOFR 1M', color='#356c82')
plt.plot(new_sofr_system_bp.index, new_sofr_system_bp['SOFR'], label='SOFR', color='#001f35', linewidth=2)
plt.plot(new_sofr_system_bp.index, new_sofr_system_bp['SRF'], label='SRF', color='#fbc430')
plt.plot(new_sofr_system_bp.index, new_sofr_system_bp['RRP'], label='RRP', color='#fdad23')

plt.ylabel("Basis Points")
plt.title("The New SOFR System", fontsize=20, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- VISIBLE REPO RATE COMPLEX ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### OFR DATA PULLS ###
base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
dvp_mnemonic = 'REPO-DVP_AR_OO-P'
gcf_mnemonic = 'REPO-GCF_AR_AG-P'
tri_mnemonic = 'REPO-TRI_AR_OO-P'

dvp_df = pd.DataFrame(requests.get(base_url + dvp_mnemonic).json(), columns=["date", "value"])
dvp_df['date'] = pd.to_datetime(dvp_df['date'])
dvp_df.index = dvp_df['date'].values
dvp_df.drop('date', axis=1, inplace=True)

gcf_df = pd.DataFrame(requests.get(base_url + gcf_mnemonic).json(), columns=["date", "value"])
gcf_df['date'] = pd.to_datetime(gcf_df['date'])
gcf_df.index = gcf_df['date'].values
gcf_df.drop('date', axis=1, inplace=True)

tri_df = pd.DataFrame(requests.get(base_url + tri_mnemonic).json(), columns=["date", "value"])
tri_df['date'] = pd.to_datetime(tri_df['date'])
tri_df.index = tri_df['date'].values
tri_df.drop('date', axis=1, inplace=True)

###  MERGE DFS ###
repo_rate_complex_df = merge_dfs([rrp,srf,sofr,dvp_df,gcf_df,tri_df])['2025-04-01':]
repo_rate_complex_df.columns = ['RRP','SRF','SOFR','DVP','GCF','TRIPARTY']
repo_rate_complex_df = repo_rate_complex_df.dropna()

### PLOT ###
colors = {
    'SOFR':     '#0B2138',
    'DVP':      '#48DEE9',
    'TRIPARTY': '#7EC0EE',
    'GCF':      '#F9D15B',
    'SRF':      '#F9C846',
    'RRP':      '#F39C12',
}
plt.figure(figsize=(12,7))
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['RRP'],
         lw=2, color=colors['RRP'], label="RRP")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SRF'],
         lw=2, color=colors['SRF'], label="SRF", alpha=0.95)
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SOFR'],
         lw=2, color=colors['SOFR'], label="SOFR")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['DVP'],
         lw=2, color=colors['DVP'], label="DVP")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['GCF'],
         lw=2, color=colors['GCF'], label="GCF")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['TRIPARTY'],
         lw=2, color=colors['TRIPARTY'], label="TRIPARTY")
plt.ylabel("bps")
plt.title("Visible Repo Rate Complex", fontsize=20, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SOFR DISTRIBUTION -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### LOAD DATA ###
sofr1 = pdr.DataReader('SOFR1', 'fred', start, end)
sofr1.index = pd.to_datetime(sofr1.index.values)
sofr25 = pdr.DataReader('SOFR25', 'fred', start, end)
sofr25.index = pd.to_datetime(sofr25.index.values)
sofr75 = pdr.DataReader('SOFR75', 'fred', start, end)
sofr75.index = pd.to_datetime(sofr75.index.values)
sofr99 = pdr.DataReader('SOFR99', 'fred', start, end)
sofr99.index = pd.to_datetime(sofr99.index.values)
sofr_distribution_df = merge_dfs([sofr,sofr1,sofr25,sofr75,sofr99])['2025-04-01':].dropna()

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(sofr_distribution_df.index, sofr_distribution_df['SOFR'],
         label='SOFR', color='#9DDCF9', lw=2)  # light blue
plt.plot(sofr_distribution_df.index, sofr_distribution_df['SOFR1'],
         label='SOFR 1%', color='#4CD0E9', lw=2)  # cyan
plt.plot(sofr_distribution_df.index, sofr_distribution_df['SOFR25'],
         label='SOFR 25%', color='#233852', lw=2)  # dark blue
plt.plot(sofr_distribution_df.index, sofr_distribution_df['SOFR75'],
         label='SOFR 75%', color='#F5B820', lw=2)  # yellow/orange
plt.plot(sofr_distribution_df.index, sofr_distribution_df['SOFR99'],
         label='SOFR 99%', color='#E69B93', lw=2)  # salmon/pink
plt.ylabel("Bps")
plt.title("SOFR Distribution", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- FED BALANCE SHEET -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6
treasury.index = pd.to_datetime(treasury.index.values)
mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
mbs.index = pd.to_datetime(mbs.index.values)

fed_balance_sheet_merge = merge_dfs([treasury,mbs])
fed_balance_sheet_merge.columns = ['SOMA Treasury','SOMA MBS']

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(fed_balance_sheet_merge.index, fed_balance_sheet_merge['SOMA Treasury'],
         color="#46b5ca", lw=3, label='SOMA Treasury')
plt.plot(fed_balance_sheet_merge.index, fed_balance_sheet_merge['SOMA MBS'],
         color="#17354c", lw=3, label='SOMA MBS')
plt.title("FED Balance Sheet", fontsize=22, fontweight="bold")
plt.ylabel("Dollars")
plt.ylim(1, 6.5)
plt.yticks(range(1, 7), [f"{x}T" for x in range(1, 7)])
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ MONITORING RESERVES ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ALL IN TRILLIONS ###
reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
reserves_volume.index = pd.to_datetime(reserves_volume.index.values)
tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
tga_volume.index = pd.to_datetime(tga_volume.index.values)
rrp_on_volume = pdr.DataReader('RRPONTSYD', 'fred', start, end) / 1e3
rrp_on_volume.index = pd.to_datetime(rrp_on_volume.index.values)
rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
rrp_volume.index = pd.to_datetime(rrp_volume.index.values)

tri_volume_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
tri_volume_df['date'] = pd.to_datetime(tri_volume_df['date'])
tri_volume_df.index = tri_volume_df['date'].values
tri_volume_df.drop('date', axis=1, inplace=True)
tri_volume_df = pd.DataFrame(tri_volume_df / 1e12)

triparty_rrp_merge = merge_dfs([tri_volume_df,rrp_volume]).dropna()
tri_repo_diff = pd.DataFrame(triparty_rrp_merge.iloc[:,0] - triparty_rrp_merge.iloc[:,1])
tri_repo_diff.columns = ['Triparty - RRP']

reserve_monitor_df = merge_dfs([reserves_volume,tga_volume,rrp_volume,tri_repo_diff,rrp_on_volume]).dropna()
reserve_monitor_df.columns = ['Bank Reserves','TGA','RRP','Triparty - RRP','RRP ON']

# Plot
plt.figure(figsize=(12, 7))
plt.plot(reserve_monitor_df.index, reserve_monitor_df['Bank Reserves'],
         label="Bank Reserves", color="#aad8ef", lw=3)
plt.plot(reserve_monitor_df.index, reserve_monitor_df['TGA'],
         label="TGA",           color="#4da3d7", lw=2)
plt.plot(reserve_monitor_df.index, reserve_monitor_df['RRP'],
         label="RRP",           color="#17293c", lw=2)
plt.plot(reserve_monitor_df.index, reserve_monitor_df['Triparty - RRP'],
         label="Triparty - RRP", color="#f5c23e", lw=2)
plt.plot(reserve_monitor_df.index, reserve_monitor_df['RRP ON'],
         label="RRP ON",        color="#f5b9ad", lw=2)

plt.title("Monitoring reserves", fontsize=22, fontweight="bold")
plt.ylabel("Dollars (Trillions)")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ FED ACTION VS RESERVE RESPONSE -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### RESERVE RESPONSE ###
shadow_bank_reserves = pdr.DataReader('WSHOMCB', 'fred', start, end) / 1e6
shadow_bank_reserves.index = pd.to_datetime(shadow_bank_reserves.index.values)

reserve_response_merge = merge_dfs([shadow_bank_reserves,reserves_volume])
reserve_response_merge.index = reserve_response_merge.index.values
reserve_response_merge.columns = ['bank','shadow_bank']
reserve_response = pd.DataFrame(reserve_response_merge['bank'].resample('M').last() +
                                reserve_response_merge['shadow_bank'].resample('M').last()).diff(1)

### FED ACTION ###
fed_balance_sheet_volume = pdr.DataReader('WALCL', 'fred', start, end) / 1e3
fed_balance_sheet_volume.index = pd.to_datetime(fed_balance_sheet_volume.index.values)


total_fed_balance_sheet = pd.DataFrame(fed_balance_sheet_merge['SOMA Treasury'] + fed_balance_sheet_merge['SOMA MBS'])
fed_action_merge = merge_dfs([total_fed_balance_sheet,rrp_volume,tga_volume])
fed_action_merge.columns = ['fed_balance_sheet','RRP','TGA']
fed_action = pd.DataFrame((fed_action_merge['fed_balance_sheet'] -
                           fed_action_merge['RRP'] -
                           fed_action_merge['TGA']).resample('ME').last().diff(1))

fed_action_vs_reserve_response = merge_dfs([fed_action,reserve_response])
fed_action_vs_reserve_response.columns = ['Fed Balance Sheet - RRP - TGA','Bank + Shadow Bank Reserves']

### PLOT ###
plt.figure(figsize=(12,7))
plt.plot(fed_action_vs_reserve_response.index,
         fed_action_vs_reserve_response['Bank + Shadow Bank Reserves'],
         label='Bank + Shadow Bank Reserves', color='#30b0c1', linewidth=2)
plt.plot(fed_action_vs_reserve_response.index,
         fed_action_vs_reserve_response['Fed Balance Sheet - RRP - TGA'],
         label='FED Balance Sheet - RRP - TGA', color='#17293c', linewidth=2)
plt.ylabel('30-Day Change (Trillions of $)')
plt.title('FED Action Vs Reserve Response (Monthly)')
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ FED ACTION VS RESERVE RESPONSE -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### AGGREGATE DATA ###
fed_action_v2_merge = merge_dfs([total_fed_balance_sheet.resample('ME').last(),
                                 reserves_volume.resample('ME').last(),
                                 shadow_bank_reserves.resample('ME').last()])
reserve_response_v2_merge = merge_dfs([rrp,tga_volume]).resample('ME').last()

fed_action_v2 = pd.DataFrame(fed_action_v2_merge.iloc[:,0] -
                             (fed_action_v2_merge.iloc[:,1] + fed_action_v2_merge.iloc[:,2])).diff(1)
reserve_response_v2 = pd.DataFrame(reserve_response_v2_merge.sum(axis=1).diff(1))

fed_action_vs_reserve_response_v2 = merge_dfs([fed_action_v2,reserve_response_v2])
fed_action_vs_reserve_response_v2.columns = ['Fed Balance Sheet - (Bank + Shadow Bank Reserves)',
                                             'RRP + TGA']

### PLOT ###
plt.figure(figsize=(12,7))
plt.plot(fed_action_vs_reserve_response_v2.index,
         fed_action_vs_reserve_response_v2['Fed Balance Sheet - (Bank + Shadow Bank Reserves)'],
         label='Fed Balance Sheet - (Bank + Shadow Bank Reserves)', color='#30b0c1', linewidth=2)
plt.plot(fed_action_vs_reserve_response_v2.index,
         fed_action_vs_reserve_response_v2['RRP + TGA'],
         label='RRP + TGA', color='#17293c', linewidth=2)
plt.ylabel('30-Day Change (Trillions of $)')
plt.title('FED Action Vs Reserve Response (Monthly)')
plt.legend()
plt.tight_layout()
plt.show()