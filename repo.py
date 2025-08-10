### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- REPO --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import datetime
from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import functools as ft
import requests
import matplotlib.ticker as mtick
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
### ------------------------------- PROXY OF PERCENT WITHOUT CENTRAL CLEARING -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### OFR DATA PULLS ###
base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

tri_volume = pd.DataFrame(requests.get(base_url + 'REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
tri_volume['date'] = pd.to_datetime(tri_volume['date'])
tri_volume.index = tri_volume['date'].values
tri_volume.drop('date', axis=1, inplace=True)
tri_volume = tri_volume / 1e12

dvp_volume = pd.DataFrame(requests.get(base_url + 'REPO-DVP_TV_TOT-P').json(), columns=["date", "value"])
dvp_volume['date'] = pd.to_datetime(dvp_volume['date'])
dvp_volume.index = dvp_volume['date'].values
dvp_volume.drop('date', axis=1, inplace=True)
dvp_volume = dvp_volume / 1e12

gcf_volume = pd.DataFrame(requests.get(base_url + 'REPO-GCF_TV_TOT-P').json(), columns=["date", "value"])
gcf_volume['date'] = pd.to_datetime(gcf_volume['date'])
gcf_volume.index = gcf_volume['date'].values
gcf_volume.drop('date', axis=1, inplace=True)
gcf_volume = gcf_volume / 1e12

rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
rrp_volume.index = pd.to_datetime(rrp_volume.index.values)

repo_total_merge = merge_dfs([gcf_volume,dvp_volume,tri_volume]).dropna()
total_repo_volume = pd.DataFrame(repo_total_merge.sum(axis=1))
total_repo_volume.columns = ['Repo']


blue_proxy = merge_dfs([tri_volume,rrp_volume,total_repo_volume])
blue_proxy.columns = ['tri','rrp','total_repo']
blue_proxy = blue_proxy.resample('W').last().dropna()
blue_proxy['blue'] = ((blue_proxy['tri']-blue_proxy['rrp']) * 3) / (blue_proxy['total_repo'] + (blue_proxy['tri']-blue_proxy['rrp']) * 2)

black_proxy = merge_dfs([tri_volume,rrp_volume,dvp_volume,gcf_volume,total_repo_volume])
black_proxy.columns = ['tri','rrp','dvp','gcf','all_repo']
black_proxy = black_proxy.resample('W').last().dropna()
black_proxy['black'] = (black_proxy['tri']-black_proxy['rrp']) / (black_proxy['all_repo'] - black_proxy['rrp'])

nccbr_proxy_merge = merge_dfs([blue_proxy['blue'],black_proxy['black']])

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(nccbr_proxy_merge.index, nccbr_proxy_merge['blue'],
         label="DVP",color="#f8b62d", lw=2)
plt.plot(nccbr_proxy_merge.index, nccbr_proxy_merge['black'],
         label="RRP", color="#f8772d", lw=2)

plt.title("Proxy of % of Non Cleared Repos", fontsize=22, fontweight="bold")
plt.ylabel("%")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- VOLUME PER VENUE --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
triparty_rrp_merge = merge_dfs([tri_volume,rrp_volume]).dropna()
triparty_rrp_volume_df = pd.DataFrame(triparty_rrp_merge.iloc[:,0] - triparty_rrp_merge.iloc[:,1])
volume_venue_merge_df = merge_dfs([dvp_volume,rrp_volume,gcf_volume,triparty_rrp_volume_df]).dropna()
volume_venue_merge_df.columns = ['DVP','RRP','GCF','Triparty-RRP']

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['DVP'],
         label="DVP",color="#f8b62d", lw=2)
plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['RRP'],
         label="RRP", color="#f8772d", lw=2)
plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['GCF'],
         label="GCF", color="#2f90c5", lw=2)
plt.plot(volume_venue_merge_df.index, volume_venue_merge_df['Triparty-RRP'],
         label="Triparty-RRP", color="#67cbe7", lw=2)

plt.title("Volume per Venue", fontsize=22, fontweight="bold")
plt.ylabel("Dollars (Trillions)")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- INVESTMENT OF MMF BY ASSET ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
treasury_sec_volume = pdr.DataReader('BOGZ1FL633061105Q', 'fred', start, end)
treasury_sec_volume.index = pd.to_datetime(treasury_sec_volume.index.values)

treasury_sec_volume = pd.DataFrame(requests.get(base_url + 'MMF-ALC_TSY-P').json(), columns=["date", "value"])
treasury_sec_volume['date'] = pd.to_datetime(treasury_sec_volume['date'])
treasury_sec_volume.index = treasury_sec_volume['date'].values
treasury_sec_volume.drop('date', axis=1, inplace=True)
treasury_sec_volume = treasury_sec_volume / 1e12

us_treasury_repo_volume = pdr.DataReader('BOGZ1FL632051000Q', 'fred', start, end)
us_treasury_repo_volume.index = pd.to_datetime(us_treasury_repo_volume.index.values)

total_mmf_volume  = pdr.DataReader('BOGZ1FL632051000Q', 'fred', start, end)
total_mmf_volume.index = pd.to_datetime(total_mmf_volume.index.values)

mmf_merge = merge_dfs([treasury_sec_volume,us_treasury_repo_volume,total_mmf_volume])
mmf_merge.columns = ['U.S. Treasury Sec.', 'U.S. Treasury Repo', 'Total MMF Assets']
mmf_merge['US_TS_Allocation'] = mmf_merge['U.S. Treasury Sec.'] / mmf_merge['Total MMF Assets'] * 100
mmf_merge['US_Repo_Allocation'] = mmf_merge['U.S. Treasury Repo'] / mmf_merge['Total MMF Assets'] * 100

# Plot
plt.figure(figsize=(8,6))
plt.plot(mmf_merge.index, mmf_merge['US_TS_Allocation'],
         label='U.S. Treasury Sec.', color='#29B6D9', lw=2)
plt.plot(mmf_merge.index, mmf_merge['US_Repo_Allocation'],
         label='U.S. Treasury Repo', color='#272f37', lw=2)
plt.title('Investment of MMF by Asset', fontsize=18, fontweight='bold', pad=18)
plt.ylabel('% Allocation')
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.ylim(10, 55)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.annotate('Source: FRED, IE.', xy=(0.01, 0.01), xycoords='figure fraction', fontsize=10, color='gray')
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- 6M VOLUME CHANGE --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
volume6m_merge_df = merge_dfs([volume_venue_merge_df,total_repo_volume]).dropna()
volume6m_merge_df['Repo-RRP'] = volume6m_merge_df['Repo'] - volume6m_merge_df['RRP']
roc_6m_volume = volume_venue_merge_df.resample('ME').last().pct_change(6)

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(roc_6m_volume.index, roc_6m_volume['DVP'],
         label="DVP",color="#f8b62d", lw=2)
plt.plot(roc_6m_volume.index, roc_6m_volume['RRP'],
         label="RRP", color="#f8772d", lw=2)
plt.plot(roc_6m_volume.index, roc_6m_volume['GCF'],
         label="GCF", color="#2f90c5", lw=2)
plt.plot(roc_6m_volume.index, roc_6m_volume['Triparty-RRP'],
         label="Triparty-RRP", color="#67cbe7", lw=2)
plt.title("Volume per Venue", fontsize=22, fontweight="bold")
plt.ylabel("%")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- VOLUME INVESTED IN MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

mmf = fred.get_series('RMFSL')









### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- RRP AND FOREIGN RRP -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PULL DATA ###
foreign_rrp = pd.DataFrame(fred.get_series('WREPOFOR', observation_start=start, observation_end=end) / 1e6)
rrp_foreign_rrp_merge = merge_dfs([rrp_volume,foreign_rrp])
rrp_foreign_rrp_merge = rrp_foreign_rrp_merge.resample('W').last().dropna()
rrp_foreign_rrp_merge.columns = ['RRP','Foreign_RRP']

### PLOT DATA ###
plt.figure(figsize=(12, 7))
plt.plot(rrp_foreign_rrp_merge.index, rrp_foreign_rrp_merge['RRP'],
         label="RRP",color="#07AFE3", lw=2)
plt.plot(rrp_foreign_rrp_merge.index, rrp_foreign_rrp_merge['Foreign_RRP'],
         label="Foreign RRP", color="#F57235", lw=2)
plt.title("RRP vs. Foreign RRP", fontsize=22, fontweight="bold")
plt.ylabel("%")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- MMF REPO VS NON REPO ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
rrp_on_volume = pdr.DataReader('RRPONTSYD', 'fred', start, end) / 1e3
treasury = pdr.DataReader('TREAST', 'fred', start, end) / 1e6

### PLOT ###


### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- TRIPARTY ADJUSTED FOR RRP ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###








### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ MMF ALLOCATION BY COUNTERPARTY -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###







