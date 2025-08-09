### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- CROSS RATE ------------------------------------------------ ###
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
### --------------------------------------------- IORB SPREADS ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULLS ###
iorb = pdr.DataReader('IORB', 'fred', start, end)
iorb.index = pd.to_datetime(iorb.index.values)
fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
fed_funds.index = pd.to_datetime(fed_funds.index.values)
sofr = pdr.DataReader('SOFR', 'fred', start, end)
sofr.index = pd.to_datetime(sofr.index.values)
sofr_1m = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
sofr_1m.index = pd.to_datetime(sofr_1m.index.values)

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

iorb_spreads_merge = merge_dfs([sofr,iorb,dvp_df,gcf_df,tri_df]).dropna() * 100
iorb_spreads_merge.columns = ['SOFR','IORB','DVP','GCF','TRI']
iorb_spreads_merge['SOFR-IORB'] = iorb_spreads_merge['SOFR'] - iorb_spreads_merge['IORB']
iorb_spreads_merge['DVP-IORB'] = iorb_spreads_merge['DVP'] - iorb_spreads_merge['IORB']
iorb_spreads_merge['GCF-IORB'] = iorb_spreads_merge['GCF'] - iorb_spreads_merge['IORB']
iorb_spreads_merge['TRI-IORB'] = iorb_spreads_merge['TRI'] - iorb_spreads_merge['IORB']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(iorb_spreads_merge.index, iorb_spreads_merge['SOFR-IORB'],
         label='SOFR - IORB', color='#6ECFF6', linewidth=2)
plt.plot(iorb_spreads_merge.index, iorb_spreads_merge['DVP-IORB'],
         label='DVP - IORB', color='#07AFE3', linewidth=2)
plt.plot(iorb_spreads_merge.index, iorb_spreads_merge['GCF-IORB'],
         label='GCF - IORB', color='#FFB400', linewidth=2)
plt.plot(iorb_spreads_merge.index, iorb_spreads_merge['TRI-IORB'],
         label='Triparty - IORB', color='#F57235', linewidth=2)
plt.axhline(y=20, color='navy', linestyle='--', linewidth=1)
plt.ylabel('Basis Points')
plt.title('IORB Spreads', fontweight='bold')
plt.legend(loc='best')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------- INTERDEALERS -TRIPARTY GCF - TRIPARTY ---------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
iorb_spreads_merge = iorb_spreads_merge['2022-01-01':]
iorb_spreads_merge['GCF-TRI'] = iorb_spreads_merge['GCF'] - iorb_spreads_merge['TRI']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(iorb_spreads_merge.index, iorb_spreads_merge['GCF-TRI'],
         label='GCF-TRI', color='#6ECFF6', linewidth=2)
plt.axhline(y=20, color='navy', linestyle='--', linewidth=1)
plt.ylabel('Basis Points')
plt.title('IORB Spreads', fontweight='bold')
plt.legend(loc='best')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- TRIPARTY - TERM SPREAD ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###


term1w_mnemonic = 'REPO-TRI_AR_1W-P'  # Example: 1 week term spread
term1w_df = pd.DataFrame(requests.get(base_url + term1w_mnemonic).json(), columns=["date", "value"])
term1w_df['date'] = pd.to_datetime(term1w_df['date'])
term1w_df.index = term1w_df['date'].values
term1w_df.drop('date', axis=1, inplace=True)




### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- THE NEW SYSTEM ---------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### AGGREGATE DATA ###
sofr_effr_merge = merge_dfs([sofr,fed_funds]).dropna()
sofr_effr_merge['sofr-effr'] = sofr_effr_merge['SOFR'] - sofr_effr_merge['EFFR']
sofr_effr_merge['sofr-effr_ma'] = sofr_effr_merge['sofr-effr'].rolling(21).mean()
sofr_effr_merge = sofr_effr_merge['2023-12-01':]

### PLOT ###
plt.figure(figsize=(8, 6))
plt.plot(sofr_effr_merge.index, sofr_effr_merge['sofr-effr'],
         color='#48DEE9', label='SOFR-EFFR', linewidth=2)
plt.plot(sofr_effr_merge.index, sofr_effr_merge['sofr-effr_ma'],
         color='#0B2138', label='SOFR-EFFR 1 Month Index', linewidth=2)
plt.title('The New System', fontsize=16, fontweight='bold')
plt.ylabel('Basis Points')
plt.xlabel('')
plt.legend(loc='upper left')
plt.grid(False)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- VISIBLE REPO RATE COMPLEX ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### OFR DATA PULLS ###
rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
rrp.index = pd.to_datetime(rrp.index.values)
srf = pd.DataFrame(index=sofr.index)
srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25

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
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['RRP'],      lw=2, color=colors['RRP'], label="RRP")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SRF'],      lw=2, color=colors['SRF'], label="SRF", alpha=0.95)
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SOFR'],     lw=2, color=colors['SOFR'], label="SOFR")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['DVP'],      lw=2, color=colors['DVP'], label="DVP")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['GCF'],      lw=2, color=colors['GCF'], label="GCF")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['TRIPARTY'], lw=2, color=colors['TRIPARTY'], label="TRIPARTY")
plt.ylabel("bps")
plt.title("Visible Repo Rate Complex", fontsize=20, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- DOLLAR LENDING COMPLEX ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### OFR DATA PULLS ###
rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
rrp.index = pd.to_datetime(rrp.index.values)
srf = pd.DataFrame(index=sofr.index)
srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25

repo_rate_complex_df = merge_dfs([rrp,srf,sofr,dvp_df,gcf_df,tri_df,fed_funds,iorb])['2025-04-01':]
repo_rate_complex_df.columns = ['RRP','SRF','SOFR','DVP','GCF','TRIPARTY','EFFR','IORB']
repo_rate_complex_df = repo_rate_complex_df.dropna()

### PLOT ###
colors = {
    'SOFR': '#0B2138',
    'DVP': '#48DEE9',
    'TRIPARTY': '#7EC0EE',
    'GCF': '#F9D15B',
    'SRF': '#F9C846',
    'RRP': '#F39C12',
    'EFFR': '#023e8a',
    'IORB': '#808080',
}
plt.figure(figsize=(12,7))
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['RRP'],      lw=2, color=colors['RRP'], label="RRP")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SRF'],      lw=2, color=colors['SRF'], label="SRF", alpha=0.95)
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['SOFR'],     lw=2, color=colors['SOFR'], label="SOFR")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['DVP'],      lw=2, color=colors['DVP'], label="DVP")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['GCF'],      lw=2, color=colors['GCF'], label="GCF")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['TRIPARTY'], lw=2, color=colors['TRIPARTY'], label="TRIPARTY")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['EFFR'], lw=2, color=colors['EFFR'], label="EFFR")
plt.plot(repo_rate_complex_df.index, repo_rate_complex_df['IORB'], lw=2, color=colors['TRIPARTY'], label="IORB")
plt.ylabel("bps")
plt.title("Visible Repo Rate", fontsize=20, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- SOFR FLOOR AND CEILING ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
rrp.index = pd.to_datetime(rrp.index.values)
srf = pd.DataFrame(index=sofr.index)
srf["SRF"] = rrp["RRPONTSYAWARD"] + 0.25  # SRF IS RRP + 25 BPS

sofr_floor_ceiling_merge = merge_dfs([sofr,rrp,srf])['2025-04-01':].dropna()*100
sofr_floor_ceiling_merge.columns = ['SOFR','SRF','RRP']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(sofr_floor_ceiling_merge.index, sofr_floor_ceiling_merge['SOFR'],
         label='SOFR', color='#07AFE3', linewidth=2)
plt.plot(sofr_floor_ceiling_merge.index, sofr_floor_ceiling_merge['SRF'],
         label='SRF', color='#6ECFF6', linewidth=2)
plt.plot(sofr_floor_ceiling_merge.index, sofr_floor_ceiling_merge['RRP'],
         label='RRP', color='#FFB400', linewidth=2)
plt.ylabel('Basis Points')
plt.title('SOFR- Floor and Ceiling', fontweight='bold')
plt.ylim(415, 455)
plt.legend(loc='best')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------- UNSECURED LENDING FLOOR AND CEILING ----------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### AGGREGATE DATA ###
unsecured_lending_merge = merge_dfs([fed_funds,iorb,srf,rrp])['2025-04-01':].dropna()*100
unsecured_lending_merge.columns = ['EFFR','IORB','SRF','RRP']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['EFFR'],
         label='EFFR', color='#6ECFF6', linewidth=2)
plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['IORB'],
         label='IORB', color='#07AFE3', linewidth=2)
plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['SRF'],
         label='Discount Window', color='#FFB400', linewidth=2)
plt.plot(unsecured_lending_merge.index, unsecured_lending_merge['RRP'],
         label='RRP', color='#F57235', linewidth=2)
plt.axhline(y=20, color='navy', linestyle='--', linewidth=1)
plt.ylabel('Basis Points')
plt.title('Unsecured Lending - Floor and Ceiling', fontweight='bold')
plt.legend(loc='best')
plt.tight_layout()
plt.ylim(415, 455)
plt.show()


