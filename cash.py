### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- CASH -------------------------------------------------- ###
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
### --------------------------------------------------- TGA -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
tga_volume.index = pd.to_datetime(tga_volume.index.values)
tga_volume.columns = ['tga_volume']
tga_roc = tga_volume.resample('W').last().diff(1)
tga_roc.columns = ['TGA ROC']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(tga_volume.index, tga_volume['tga_volume'],
         label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('TGA', fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 6))
plt.plot(tga_roc.index, tga_roc['TGA ROC'],
         label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('TGA', fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------------- RRP -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
rrp_volume.index = pd.to_datetime(rrp_volume.index.values)
rrp_volume.columns = ['rrp_volume']
rrp_roc = rrp_volume.resample('W').last().diff(1)
rrp_roc.columns = ['RRP ROC']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(rrp_volume.index, rrp_volume['rrp_volume'],
         label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('TGA', fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 6))
plt.plot(rrp_roc.index, rrp_roc['RRP ROC'],
         label='RRP Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('RRP', fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- TOTAL BANKING RESERVES ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
reserves_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
reserves_volume.index = pd.to_datetime(reserves_volume.index.values)
reserves_volume.columns = ['reserves_volume']
reserves_roc = reserves_volume.resample('W').last().diff(1)
reserves_roc.columns = ['reserves_roc']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(reserves_volume.index, reserves_volume['reserves_volume'],
         label='Reserves', color='#07AFE3', linewidth=2)
plt.title('Reserves', fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 6))
plt.plot(reserves_roc.index, reserves_roc['reserves_roc'],
         label='Reserves Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('Reserves', fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()


### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- 6M CASH RATE OF CHANGE ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

'''
- description is to vague so not sure what it is trying to express or the source it is from
'''

# cash_volume = pdr.DataReader('WRESBAL', 'fred', start, end) / 1e3
# cash_volume.index = pd.to_datetime(cash_volume.index.values)
# cash_volume.columns = ['cash_volume']
# cash_roc = cash_volume.resample('ME').last().diff(6)
# cash_roc.columns = ['cash_roc']
#
# ### PLOT ###
# plt.figure(figsize=(7, 6))
# plt.plot(cash_volume.index, cash_volume['cash_volume'],
#          label='Reserves', color='#07AFE3', linewidth=2)
# plt.title('Reserves', fontweight='bold')
# plt.legend(loc='best')
# plt.tight_layout()
# plt.show()
#
# plt.figure(figsize=(7, 6))
# plt.plot(reserves_roc.index, reserves_roc['reserves_roc'],
#          label='Reserves Weekly ROC', color='#07AFE3', linewidth=2)
# plt.title('Reserves', fontweight='bold')
# plt.legend(loc='best')
# plt.tight_layout()
# plt.show()


### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ MMF REPO VS NON REPO ------------------------------------------ ###
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
### ------------------------------------------ ASSET ALLOCATION MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
mmf_repo_total = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_TOT-M').json(), columns=["date", "value"])
mmf_repo_total['date'] = pd.to_datetime(mmf_repo_total['date'])
mmf_repo_total.index = mmf_repo_total['date'].values
mmf_repo_total.drop('date', axis=1, inplace=True)
mmf_repo_total = mmf_repo_total / 1e12

mmf_fed_repo = pd.DataFrame(requests.get(base_url + 'MMF-MMF_RP_wFR-M').json(), columns=["date", "value"])
mmf_fed_repo['date'] = pd.to_datetime(mmf_fed_repo['date'])
mmf_fed_repo.index = mmf_fed_repo['date'].values
mmf_fed_repo.drop('date', axis=1, inplace=True)
mmf_fed_repo = mmf_fed_repo / 1e12

mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo, mmf_repo_total])
mmf_fed_repo_non_repo_merge.columns = ['mmf_fed_repo','mmf_repo_total']
mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'] = (mmf_fed_repo_non_repo_merge['mmf_repo_total'] -
                                                   mmf_fed_repo_non_repo_merge['mmf_fed_repo'])
mmf_fed_repo_non_repo_merge = mmf_fed_repo_non_repo_merge['2019-01-01':]

mmf_fed_repo_non_repo_merge = merge_dfs([mmf_fed_repo_non_repo_merge,mmf_repo_non_repo_merge])

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(mmf_fed_repo_non_repo_merge.index, mmf_fed_repo_non_repo_merge['mmf_non_fed_repo'],
         label="Non-Fed Repo",color="#9DDCF9", lw=2)
plt.plot(mmf_fed_repo_non_repo_merge.index, mmf_fed_repo_non_repo_merge['non_repo'],
         label="Non-Repo Allocation", color="#233852", lw=2)
plt.plot(mmf_fed_repo_non_repo_merge.index, mmf_fed_repo_non_repo_merge['mmf_repo'],
         label="Repo Allocation", color="#F5B820", lw=2)
plt.title("MMF Repo vs Nono Repo", fontsize=22, fontweight="bold")
plt.ylabel('Dollars')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------- RESERVES NON FED REPO + RESERRVES + RRP -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA AGGREGATION ###
reserve_liabilities_merge = merge_dfs([tga_volume.resample('ME').last(),
                                       rrp_volume.resample('ME').last(),
                                       reserves_volume.resample('ME').last(),
                                       mmf_fed_repo_non_repo_merge.resample('ME').last()]).dropna()
reserve_liabilities_merge['reserves_non_repo_rrp'] = (reserve_liabilities_merge['rrp_volume'] +
                                                      reserve_liabilities_merge['reserves_volume'] +
                                                      reserve_liabilities_merge['mmf_non_fed_repo'])

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['reserves_non_repo_rrp'],
         color="#9DDCF9", lw=2)
plt.title("Non Fed Repo + Reserves + RRP", fontsize=22, fontweight="bold")
plt.ylabel('Dollars')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- RESERVES LIABILITIES OF THE SYSTEM ----------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['mmf_non_fed_repo'],
         label="Non-Fed Repo",color="#9DDCF9", lw=2)
plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['tga_volume'],
         label="TGA", color="#233852", lw=2)
plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['reserves_volume'],
         label="Reserves", color="#F5B820", lw=2)
plt.plot(reserve_liabilities_merge.index, reserve_liabilities_merge['rrp_volume'],
         label="RRP", color="#E69B93", lw=2)
plt.title("Reserves Liabilities of the System", fontsize=22, fontweight="bold")
plt.ylabel('Dollars')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()




