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

repo_market_volumes = pd.read_csv('data/SponsoredVolume.csv').dropna()
repo_market_volumes = repo_market_volumes.iloc[::-1].reset_index(drop=True)
repo_market_volumes.index = pd.to_datetime(repo_market_volumes['BUSINESS_DATE'].values)
repo_market_volumes = repo_market_volumes.drop('BUSINESS_DATE',axis=1)
repo_market_volumes['DVP_TOTAL_AMOUNT'] = (
    repo_market_volumes['DVP_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
repo_market_volumes['GC_TOTAL_AMOUNT'] = (
    repo_market_volumes['GC_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
repo_market_volumes['TOTAL_REPO_AMOUNT'] = (
    repo_market_volumes['TOTAL_REPO_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
repo_market_volumes['TOTAL_REVERSE_REPO_AMOUNT'] = (
    repo_market_volumes['TOTAL_REVERSE_REPO_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
repo_market_volumes['TOTAL_AMOUNT'] = (
    repo_market_volumes['TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))

tri_volume = pd.DataFrame(requests.get(base_url + 'REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
tri_volume['date'] = pd.to_datetime(tri_volume['date'])
tri_volume.index = tri_volume['date'].values
tri_volume.drop('date', axis=1, inplace=True)
tri_volume = tri_volume / 1e12
tri_volume.columns = ['tri']

dvp_volume = pd.DataFrame(requests.get(base_url + 'REPO-DVP_TV_TOT-P').json(), columns=["date", "value"])
dvp_volume['date'] = pd.to_datetime(dvp_volume['date'])
dvp_volume.index = dvp_volume['date'].values
dvp_volume.drop('date', axis=1, inplace=True)
dvp_volume = dvp_volume / 1e12
dvp_volume.columns = ['dvp']

gcf_volume = pd.DataFrame(requests.get(base_url + 'REPO-GCF_TV_TOT-P').json(), columns=["date", "value"])
gcf_volume['date'] = pd.to_datetime(gcf_volume['date'])
gcf_volume.index = gcf_volume['date'].values
gcf_volume.drop('date', axis=1, inplace=True)
gcf_volume = gcf_volume / 1e12
gcf_volume.columns = ['gcf']

rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
rrp_volume.index = pd.to_datetime(rrp_volume.index.values)
rrp_volume.columns = ['rrp']

nccbr = 'https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSET.json'
nccbr_volume = pd.DataFrame(requests.get(nccbr).json()['pd']['timeseries']).drop('keyid', axis=1)
nccbr_volume['value'] = pd.to_numeric(nccbr_volume['value'], errors='coerce')
nccbr_volume.dropna(subset=['value'], inplace=True)
nccbr_volume['asofdate'] = pd.to_datetime(nccbr_volume['asofdate'])
nccbr_volume.index = nccbr_volume['asofdate'].values
nccbr_volume.drop('asofdate', axis=1, inplace=True)
nccbr_volume = (nccbr_volume/1e6) * 2
nccbr_volume.columns = ['nccbr']

repo_total_merge = merge_dfs([gcf_volume,dvp_volume,tri_volume,nccbr_volume]).dropna()
total_repo_volume = pd.DataFrame(repo_total_merge.sum(axis=1))
total_repo_volume.columns = ['Repo']

blue_proxy = merge_dfs([tri_volume,rrp_volume,total_repo_volume,nccbr_volume])
blue_proxy.columns = ['tri','rrp','total_repo','nccbr']
blue_proxy = blue_proxy.resample('W').last().dropna()
blue_proxy['blue'] = ((blue_proxy['tri']-blue_proxy['rrp']) + blue_proxy['nccbr']) / (blue_proxy['total_repo']+ blue_proxy['nccbr'] - blue_proxy['rrp'])

black_proxy = merge_dfs([tri_volume,rrp_volume,dvp_volume,gcf_volume,total_repo_volume])
black_proxy.columns = ['tri','rrp','dvp','gcf','all_repo']
black_proxy = black_proxy.resample('W').last().dropna()
black_proxy['black'] = (black_proxy['tri']-black_proxy['rrp']) / (black_proxy['all_repo'] - black_proxy['rrp'])

nccbr_proxy_merge = merge_dfs([blue_proxy['blue'],black_proxy['black']])

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(nccbr_proxy_merge.index, nccbr_proxy_merge['blue'],
         label="(Tri Party-RRP + 2T NCCBR)/(All Repo + 2T NCCBR-RRP)",color="#f8b62d", lw=2)
plt.plot(nccbr_proxy_merge.index, nccbr_proxy_merge['black'],
         label="Tri Party-RRP / (Tri Party+DVP+GCF-RRP)", color="#f8772d", lw=2)
plt.title("Proxy of % of Non Cleared Repos", fontsize=22, fontweight="bold")
plt.ylabel("%")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.18), ncol=1)
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
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- INVESTMENT OF MMF BY ASSET ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

mmf_repo_allocation = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_TOT-M').json(), columns=["date", "value"])
mmf_repo_allocation['date'] = pd.to_datetime(mmf_repo_allocation['date'])
mmf_repo_allocation.index = mmf_repo_allocation['date'].values
mmf_repo_allocation.drop('date', axis=1, inplace=True)
mmf_repo_allocation = mmf_repo_allocation / 1e12

total_mmf_allocation = pd.DataFrame(requests.get(base_url + 'MMF-MMF_TOT-M').json(), columns=["date", "value"])
total_mmf_allocation['date'] = pd.to_datetime(total_mmf_allocation['date'])
total_mmf_allocation.index = total_mmf_allocation['date'].values
total_mmf_allocation.drop('date', axis=1, inplace=True)
total_mmf_allocation = total_mmf_allocation / 1e12

mmf_us_treasury_sec = pd.DataFrame(requests.get(base_url + 'MMF-MMF_T_TOT-M').json(), columns=["date", "value"])
mmf_us_treasury_sec['date'] = pd.to_datetime(mmf_us_treasury_sec['date'])
mmf_us_treasury_sec.index = mmf_us_treasury_sec['date'].values
mmf_us_treasury_sec.drop('date', axis=1, inplace=True)
mmf_us_treasury_sec = mmf_us_treasury_sec / 1e12

mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, total_mmf_allocation,mmf_us_treasury_sec])
mmf_repo_non_repo_merge.columns = ['mmf_repo','mmf_total','mmf_us_treasury_sec']
mmf_repo_non_repo_merge['non_repo'] = mmf_repo_non_repo_merge['mmf_total'] - mmf_repo_non_repo_merge['mmf_repo']
mmf_repo_non_repo_merge = mmf_repo_non_repo_merge['2019-01-01':]

mmf_repo_non_repo_merge['US_Repo_Allocation'] = mmf_repo_non_repo_merge['mmf_repo'] / mmf_repo_non_repo_merge['mmf_total']
mmf_repo_non_repo_merge['US_TS_Allocation'] = mmf_repo_non_repo_merge['mmf_us_treasury_sec'] / mmf_repo_non_repo_merge['mmf_total']
mmf_repo_non_repo_merge = mmf_repo_non_repo_merge.dropna()

### PLOT ###
plt.figure(figsize=(8,6))
plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['US_TS_Allocation'],
         label='U.S. Treasury Sec.', color='#29B6D9', lw=2)
plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['US_Repo_Allocation'],
         label='U.S. Treasury Repo', color='#272f37', lw=2)
plt.title('Investment of MMF by Asset', fontsize=18, fontweight='bold', pad=18)
plt.ylabel('% Allocation')
plt.yticks(fontsize=11)
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- 6M VOLUME CHANGE --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
volume6m_merge_df = merge_dfs([volume_venue_merge_df,total_repo_volume]).dropna()
volume6m_merge_df['Repo-RRP'] = volume6m_merge_df['Repo'] - volume6m_merge_df['RRP']
roc_6m_volume = volume6m_merge_df.resample('W').last().pct_change(26).rolling(4).mean().dropna()

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(roc_6m_volume.index, roc_6m_volume['DVP'],
         label="DVP",color="#f8b62d", lw=2)
plt.plot(roc_6m_volume.index, roc_6m_volume['Repo-RRP'],
         label="Repo-RRP", color="#f8772d", lw=2)
plt.plot(roc_6m_volume.index, roc_6m_volume['GCF'],
         label="GCF", color="#2f90c5", lw=2)
plt.plot(roc_6m_volume.index, roc_6m_volume['Triparty-RRP'],
         label="Triparty-RRP", color="#67cbe7", lw=2)
plt.title("Volume per Venue", fontsize=22, fontweight="bold")
plt.ylabel("%")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- VOLUME INVESTED IN MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
mmf_repo_allocation = pd.DataFrame(requests.get(base_url + 'MMF-MMF_TOT-M').json(), columns=["date", "value"])
mmf_repo_allocation['date'] = pd.to_datetime(mmf_repo_allocation['date'])
mmf_repo_allocation.index = mmf_repo_allocation['date'].values
mmf_repo_allocation.drop('date', axis=1, inplace=True)
mmf_repo_allocation = mmf_repo_allocation / 1e12
mmf_repo_allocation = mmf_repo_allocation['2021-01-01':]
mmf_repo_allocation.columns = ['MMF_TOTAL']

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(mmf_repo_allocation.index, mmf_repo_allocation['MMF_TOTAL'],
         color="#67cbe7", lw=2)
plt.title("Volume Invested in MMF", fontsize=22, fontweight="bold")
plt.ylabel("Trillions")
plt.tight_layout()
plt.show()

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
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- MMF REPO VS NON REPO ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

mmf_repo_allocation = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_TOT-M').json(), columns=["date", "value"])
mmf_repo_allocation['date'] = pd.to_datetime(mmf_repo_allocation['date'])
mmf_repo_allocation.index = mmf_repo_allocation['date'].values
mmf_repo_allocation.drop('date', axis=1, inplace=True)
mmf_repo_allocation = mmf_repo_allocation / 1e12

total_mmf_allocation = pd.DataFrame(requests.get(base_url + 'MMF-MMF_TOT-M').json(), columns=["date", "value"])
total_mmf_allocation['date'] = pd.to_datetime(total_mmf_allocation['date'])
total_mmf_allocation.index = total_mmf_allocation['date'].values
total_mmf_allocation.drop('date', axis=1, inplace=True)
total_mmf_allocation = total_mmf_allocation / 1e12

mmf_repo_non_repo_merge = merge_dfs([mmf_repo_allocation, total_mmf_allocation])
mmf_repo_non_repo_merge.columns = ['mmf_repo','mmf_total']
mmf_repo_non_repo_merge['non_repo'] = mmf_repo_non_repo_merge['mmf_total'] - mmf_repo_non_repo_merge['mmf_repo']
mmf_repo_non_repo_merge = mmf_repo_non_repo_merge['2019-01-01':]

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['non_repo'],
         label="Non-Repo Allocation",color="#f8b62d", lw=2)
plt.plot(mmf_repo_non_repo_merge.index, mmf_repo_non_repo_merge['mmf_repo'],
         label="Repo Allocation", color="#f8772d", lw=2)

plt.title("MMF Repo vs Nono Repo", fontsize=22, fontweight="bold")
plt.ylabel('Dollars')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- TRIPARTY ADJUSTED FOR RRP ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA AGGREGATION ###
triparty_merge = merge_dfs([tri_volume,rrp_volume,dvp_volume])
triparty_merge.columns = ['tri','rrp','dvp']
triparty_merge['triparty-rrp'] = triparty_merge['tri'] - triparty_merge['rrp']
triparty_merge['residual_flows'] = triparty_merge['dvp'] - triparty_merge['triparty-rrp']
triparty_merge = triparty_merge.dropna()

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(triparty_merge.index, triparty_merge['triparty-rrp'],
         label="Triparty-RRP",color="#f8b62d", lw=2)
plt.plot(triparty_merge.index, triparty_merge['dvp'],
         label="DVP", color="#f8772d", lw=2)
plt.plot(triparty_merge.index, triparty_merge['residual_flows'],
         label="Residual Flow", color="#2f90c5", lw=2)
plt.title("Tri-Party Adjusted for RRP", fontsize=22, fontweight="bold")
plt.ylabel("Trillions")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ MMF ALLOCATION BY COUNTERPARTY -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
mmf_foreign = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_wFFI-M').json(), columns=["date", "value"])
mmf_foreign['date'] = pd.to_datetime(mmf_foreign['date'])
mmf_foreign.index = mmf_foreign['date'].values
mmf_foreign.drop('date', axis=1, inplace=True)
mmf_foreign = mmf_foreign / 1e12
mmf_foreign.columns = ['foreign']

mmf_fed = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_wFR-M').json(), columns=["date", "value"])
mmf_fed['date'] = pd.to_datetime(mmf_fed['date'])
mmf_fed.index = mmf_fed['date'].values
mmf_fed.drop('date', axis=1, inplace=True)
mmf_fed = mmf_fed / 1e12
mmf_fed.columns = ['fed']

mmf_us_fin_inst = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_wDFI-M').json(), columns=["date", "value"])
mmf_us_fin_inst['date'] = pd.to_datetime(mmf_us_fin_inst['date'])
mmf_us_fin_inst.index = mmf_us_fin_inst['date'].values
mmf_us_fin_inst.drop('date', axis=1, inplace=True)
mmf_us_fin_inst = mmf_us_fin_inst / 1e12
mmf_us_fin_inst.columns = ['us_inst']

mmf_ficc = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_wFICC-M').json(), columns=["date", "value"])
mmf_ficc['date'] = pd.to_datetime(mmf_ficc['date'])
mmf_ficc.index = mmf_ficc['date'].values
mmf_ficc.drop('date', axis=1, inplace=True)
mmf_ficc = mmf_ficc / 1e12
mmf_ficc.columns = ['ficc']

mmf_allocations_merge = merge_dfs([mmf_foreign,mmf_fed,mmf_us_fin_inst,mmf_ficc]).dropna()['2020-12-01':]

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['foreign'],
         label="Foreign",color="#f8b62d", lw=2)
plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['fed'],
         label="Fed", color="#f8772d", lw=2)
plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['us_inst'],
         label="US Financial Institutions", color="#2f90c5", lw=2)
plt.plot(mmf_allocations_merge.index, mmf_allocations_merge['ficc'],
         label="FICC", color="#67cbe7", lw=2)
plt.title("Allocation of MMF by Counterparties", fontsize=22, fontweight="bold")
plt.ylabel("Trillions")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()
