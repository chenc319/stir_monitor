### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- FED BALANCE SHEET DATA PULL --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###
import pandas as pd

### PACKAGES ###
from Functions import *
from pathlib import Path
import os
DATA_DIR = os.getenv('DATA_DIR', 'data')

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ ALL ARE WEDNESDAY LEVELS NOT WEEKLY AVERAGES ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### ASSETS ###
start = '1990-01-01'
end = pd.to_datetime('today')

reserve_bank_credit_wed = get_fred_series('WOFSRBRBC', start, end) / 1000

securities_held_wed = get_fred_series('WSHOSHO', start, end) / 1000
treasuries_wed = get_fred_series('WSHOTSL', start, end) / 1000
mbs_wed = get_fred_series('WSHOMCB', start, end) / 1000
agency_wed = get_fred_series('WSHOFADSL', start, end) / 1000

repo_wed = get_fred_series('WORAL', start, end) / 1000
fima_repo_facility_wed = get_fred_series('H41RESPPALGTRFNWW', start, end) / 1000
standing_repo_facility_wed = get_fred_series('H41RESPPALGTRONWW', start, end) / 1000

loans_wed = get_fred_series('WLCFLL', start, end) / 1000
primary_credit_discount_window_wed = get_fred_series('WLCFLPCL', start, end) / 1000
other_credit_extensions_wed = get_fred_series('WLCFOCEL', start, end) / 1000
central_bank_liquidity_swaps_wed = get_fred_series('SWPT', start, end) / 1000

other_assets_wed = pd.DataFrame(merge_dfs([reserve_bank_credit_wed,
                                           pd.DataFrame(merge_dfs([
                                               securities_held_wed,
                                               repo_wed,loans_wed,
                                               central_bank_liquidity_swaps_wed
                                           ]).sum(axis=1))*-1]).sum(axis=1))

### LIABILITIES ###
total_factors_supplying_reserve_funds_wed = get_fred_series('WTFSRFL', start, end) / 1000

currency_in_circulation_wed = get_fred_series('WCICL', start, end) / 1000

rrp_wed = get_fred_series('WLRRAL', start, end) / 1000
foreign_rrp_wed = get_fred_series('WLRRAFOIAL', start, end) / 1000
domestic_rrp_wed = get_fred_series('WLRRAOL', start, end) / 1000

deposits_w_frb_bank_ex_reserves_wed = get_fred_series('WOFDRBORBL', start, end) / 1000
tga_wed = get_fred_series('WDTGAL', start, end) / 1000
foreign_official_wed = get_fred_series('WDFOL', start, end) / 1000
other_deposits_wed = get_fred_series('WLODL', start, end) / 1000

reserves_balanaces_wed = get_fred_series('WRBWFRBL', start, end) / 1000

other_liabilities_wed = get_fred_series('WMTSECL1', start, end) / 1000

### MEMORANDUM ###
fed_custody_holdings_total_wed = get_fred_series('WSEFINTL1', start, end) / 1000
fed_custody_holdings_of_tsys_wed = get_fred_series('WLAD', start, end) / 1000
fed_custody_holdings_of_mbs_wed = get_fred_series('WFASECL1', start, end) / 1000
fed_custody_holdings_others_wed = pd.DataFrame(merge_dfs([fed_custody_holdings_total_wed,
                                                          pd.DataFrame(merge_dfs([
                                                              fed_custody_holdings_of_tsys_wed,
                                                              repo_wed,fed_custody_holdings_of_mbs_wed,
                                                          ]).sum(axis=1))*-1]).sum(axis=1))

### ADDITIONAL DATA ###
reserve_balances_w_frb_wed = get_fred_series('WRBWFRBL', start, end) / 1000
others_absorbing_reserves_wed = get_fred_series('WTFORBAFL', start, end) / 1000
total_factors_supplying_reserves = get_fred_series('WTFSRFL', start, end) / 1000

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ ALL ARE WEDNESDAY LEVELS NOT WEEKLY AVERAGES ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

assets_array = [
    reserve_bank_credit_wed,
    securities_held_wed,
    treasuries_wed,
    mbs_wed,
    agency_wed,
    repo_wed,
    fima_repo_facility_wed,
    standing_repo_facility_wed,
    loans_wed,
    primary_credit_discount_window_wed,
    other_credit_extensions_wed,
    central_bank_liquidity_swaps_wed,
    other_assets_wed,
]
liabilities_array = [
    total_factors_supplying_reserve_funds_wed,
    currency_in_circulation_wed,
    rrp_wed,
    foreign_rrp_wed,
    domestic_rrp_wed,
    deposits_w_frb_bank_ex_reserves_wed,
    tga_wed,
    foreign_official_wed,
    other_deposits_wed,
    reserves_balanaces_wed,
    other_liabilities_wed,
]
memorandum_array = [
    fed_custody_holdings_total_wed,
    fed_custody_holdings_of_tsys_wed,
    fed_custody_holdings_of_mbs_wed,
    fed_custody_holdings_others_wed,
]
additional_array = [
    reserve_balances_w_frb_wed,
    others_absorbing_reserves_wed,
    total_factors_supplying_reserves
]

for df in assets_array + liabilities_array + memorandum_array + additional_array:
    df.columns = ['Level']
    df['1w'] = df.iloc[:,0].diff(1)
    df['4w'] = df.iloc[:,0].diff(4)
    df['6m'] = df.iloc[:,0].diff(26)
    df['12m'] = df.iloc[:,0].diff(52)
    df = df.dropna()

fed_balance_sheet_dict = {
    'Assets': ['Level','1w','4w','6m','12m'],
    'Reserve Bank Credit': reserve_bank_credit_wed,
    'Securities Held': securities_held_wed,
    'Treasury': treasuries_wed,
    'MBS': mbs_wed,
    'Agency': agency_wed,
    'Repo': repo_wed,
    'FIMA Repo Facility': fima_repo_facility_wed,
    'Standing Repo Facility': standing_repo_facility_wed,
    'Loans': loans_wed,
    'Primary Credit (Discount Window)': primary_credit_discount_window_wed,
    'Securities': other_credit_extensions_wed,
    'Other Credit Extensions': central_bank_liquidity_swaps_wed,
    'Other Assets': other_assets_wed,

    'Liabilities': ['Level', '1w', '4w', '6m', '12m'],
    'Currency in Circulation': currency_in_circulation_wed,
    'Reverse Repurchase Agreements': rrp_wed,
    'Foreign RRP': foreign_rrp_wed,
    'Domestic RRP': domestic_rrp_wed,
    'Deposits with FRB Banks (ex. Reserves)': deposits_w_frb_bank_ex_reserves_wed,
    'TGA': tga_wed,
    'Foreign Official': foreign_official_wed,
    'Other Deposits (GSE Cash)': other_deposits_wed,
    'Reserves Balances': reserves_balanaces_wed,
    'Other Liabilities (incl. Tsy Remittances)': other_liabilities_wed,

    'Memorandum': ['Level', '1w', '4w', '6m', '12m'],
    'Fed Custody Holdings': fed_custody_holdings_total_wed,
    'Treasury': fed_custody_holdings_of_tsys_wed,
    'MBS': fed_custody_holdings_of_mbs_wed,
    'Other': fed_custody_holdings_others_wed,
}

with open(Path(DATA_DIR) / 'fed_balance_sheet_dict.pkl', 'wb') as file:
    pickle.dump(fed_balance_sheet_dict, file)




