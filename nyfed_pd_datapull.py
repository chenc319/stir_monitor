### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- REFRESH DATA FUNCTION ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
from Functions import *
from pathlib import Path
import os
DATA_DIR = os.getenv('DATA_DIR', 'data')

### ALL ###
pd_total_masters = get_newyork_fed_data('PDPOSGST-TOT') / 1000
pd_frns = get_newyork_fed_data('PDPOSGS-BFRN') / 1000
pd_bills = get_newyork_fed_data('PDPOSGS-B') / 1000
pd_coupons = pd.DataFrame(merge_dfs([pd_total_masters,(-1*pd_frns),(-1*pd_bills)]).sum(axis=1))

### COUPONS ###
pd_coups_l2 = get_newyork_fed_data('PDPOSGSC-L2') / 1000
pd_coups_23 = get_newyork_fed_data('PDPOSGSC-G2L3') / 1000
pd_coups_36 = get_newyork_fed_data('PDPOSGSC-G3L6') / 1000
pd_coups_67 = get_newyork_fed_data('PDPOSGSC-G6L7') / 1000
pd_coups_711 = get_newyork_fed_data('PDPOSGSC-G7L11') / 1000
pd_coups_1121 = get_newyork_fed_data('PDPOSGSC-G11L21') / 1000
pd_coups_g21 = get_newyork_fed_data('PDPOSGSC-G21') / 1000

### TIPS ###
pd_tips_l2 = get_newyork_fed_data('PDPOSTIPS-L2') / 1000
pd_tips_26 = get_newyork_fed_data('PDPOSTIPS-G2') / 1000
pd_tips_611 = get_newyork_fed_data('PDPOSTIPS-G6L11') / 1000
pd_tips_g11 = get_newyork_fed_data('PDPOSTIPS-G11') / 1000
pd_tips_total = pd.DataFrame(merge_dfs([
    pd_tips_l2,pd_tips_26,pd_tips_611,pd_tips_g11
]).sum(axis=1))

pd_array = [
    pd_total_masters,
    pd_coupons,
    pd_frns,
    pd_bills,
    pd_coups_l2,
    pd_coups_23,
    pd_coups_36,
    pd_coups_67,
    pd_coups_711,
    pd_coups_1121,
    pd_coups_g21,
    pd_tips_total,
    pd_tips_l2,
    pd_tips_26,
    pd_tips_611,
    pd_tips_g11,
]

df = pd_array[0].copy()

for df in pd_array:
    df.columns = ['Level']
    year = df.index.year
    last_per_year = df.groupby(year)['Level'].last()
    prev_year_last = year.map(lambda y: last_per_year.get(y - 1))

    df['YTD chg'] = df['Level'] - prev_year_last
    df['1w chg'] = df.iloc[:,0].diff(1)
    df['4w chg'] = df.iloc[:,0].diff(4)
    df['6m chg'] = df.iloc[:,0].diff(26)
    df['12m chg'] = df.iloc[:,0].diff(52)
    df['5y min'] = df.iloc[:, 0].rolling(window=260, min_periods=1).min()
    df['5y max'] = df.iloc[:, 0].rolling(window=260, min_periods=1).max()
    df['5y avg'] = df.iloc[:, 0].rolling(window=260).mean()
    df = df.dropna()

pd_pos_dict = {
    'Total': ['Level','YTD chg','1w chg','4w chg','6m chg','12m chg','5y min','5y max','5y avg'],
    'All USTs': pd_total_masters,

    'Coupons': ['Level','YTD chg','1w chg','4w chg','6m chg','12m chg','5y min','5y max','5y avg'],
    'All Coupons': pd_coupons,
    'Coupons <2y': pd_coups_l2,
    'Coupons 2-3y': pd_coups_23,
    'Coupons 3-6y': pd_coups_36,
    'Coupons 6-7y': pd_coups_67,
    'Coupons 7-11y': pd_coups_711,
    'Coupons 11-21y': pd_coups_1121,
    'Coupons >21y': pd_coups_g21,

    'TIPS': ['Level','YTD chg','1w chg','4w chg','6m chg','12m chg','5y min','5y max','5y avg'],
    'All TIPS': pd_tips_total,
    'TIPS <2y': pd_tips_l2,
    'TIPS 2-6y': pd_tips_26,
    'TIPS 6-11y': pd_tips_611,
    'TIPS >11y': pd_tips_g11,

    'Bills': ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg'],
    'All Bills': pd_bills,

    'FRNs': ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg'],
    'All FRNs': pd_frns,
}

with open(Path(DATA_DIR) / 'pd_pos_dict.pkl', 'wb') as file:
    pickle.dump(pd_pos_dict, file)