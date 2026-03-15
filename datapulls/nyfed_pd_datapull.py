### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ PRIMARY DEALER DATA ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
from Functions import *
from pathlib import Path
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

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

df = pd_coups_g21.copy()

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

    s = df.iloc[:, 0]
    min_periods = 260
    count = s.expanding().count()

    # 5y min
    exp_min = s.expanding(min_periods=1).min()
    roll_min = s.rolling(window=min_periods, min_periods=min_periods).min()
    df['5y min'] = exp_min.where(count < min_periods, roll_min)

    # 5y max
    exp_max = s.expanding(min_periods=1).max()
    roll_max = s.rolling(window=min_periods, min_periods=min_periods).max()
    df['5y max'] = exp_max.where(count < min_periods, roll_max)

    # 5y avg
    exp_mean = s.expanding(min_periods=1).mean()
    roll_mean = s.rolling(window=min_periods, min_periods=min_periods).mean()
    df['5y avg'] = exp_mean.where(count < min_periods, roll_mean)

    df = df.dropna()
    df.index = df.index.values

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

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ PRIMARY DEALER DATA ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

rrp_uncleared_bilateral_special_on = get_newyork_fed_data('PDSIRRA-UBSUTSET')
rrp_uncleared_bilateral_special_l30 = get_newyork_fed_data('PDSIRRA-UBSUTSETTAL30')
rrp_uncleared_bilateral_special_g30 = get_newyork_fed_data('PDSIRRA-UBSUTSETTAG30')

rrp_uncleared_bilateral_general_on = get_newyork_fed_data('PDSIRRA-UBGUTSET')
rrp_uncleared_bilateral_general_l30 = get_newyork_fed_data('PDSIRRA-UBGUTSETTAL30')
rrp_uncleared_bilateral_general_g30 = get_newyork_fed_data('PDSIRRA-UBGUTSETTAG30')

rrp_uncleared_bilateral = merge_dfs([
    rrp_uncleared_bilateral_special_on,
    rrp_uncleared_bilateral_special_l30,
    rrp_uncleared_bilateral_special_g30,
    rrp_uncleared_bilateral_general_on,
    rrp_uncleared_bilateral_general_l30,
    rrp_uncleared_bilateral_general_g30,
])
rrp_uncleared_bilateral.columns = [
    'Uncleared Bilateral Special O/N',
    'Uncleared Bilateral Special L30',
    'Uncleared Bilateral Special G30',
    'Uncleared Bilateral General O/N',
    'Uncleared Bilateral General L30',
    'Uncleared Bilateral General G30',
]
with open(Path(DATA_DIR) / 'rrp_uncleared_bilateral.pkl', 'wb') as file:
    pickle.dump(rrp_uncleared_bilateral, file)

rrp_cleared_bilateral_special_on = get_newyork_fed_data('PDSIRRA-CBSUTSET')
rrp_cleared_bilateral_special_l30 = get_newyork_fed_data('PDSIRRA-CBSUTSETTAL30')
rrp_cleared_bilateral_special_g30 = get_newyork_fed_data('PDSIRRA-CBSUTSETTAG30')

rrp_cleared_bilateral_general_on = get_newyork_fed_data('PDSIRRA-CBGUTSET')
rrp_cleared_bilateral_general_l30 = get_newyork_fed_data('PDSIRRA-CBGUTSETTAL30')
rrp_cleared_bilateral_general_g30 = get_newyork_fed_data('PDSIRRA-CBGUTSETTAG30')

rrp_cleared_bilateral_sponsored_on = get_newyork_fed_data('PDSIRRA-CBSPUTSET')
rrp_cleared_bilateral_sponsored_l30 = get_newyork_fed_data('PDSIRRA-CBSPUTSETTAL30')
rrp_cleared_bilateral_sponsored_g30 = get_newyork_fed_data('PDSIRRA-CBSPUTSETTAG30')

rrp_cleared_bilateral = merge_dfs([
    rrp_cleared_bilateral_special_on,
    rrp_cleared_bilateral_special_l30,
    rrp_cleared_bilateral_special_g30,
    rrp_cleared_bilateral_general_on,
    rrp_cleared_bilateral_general_l30,
    rrp_cleared_bilateral_general_g30,
    rrp_cleared_bilateral_sponsored_on,
    rrp_cleared_bilateral_sponsored_l30,
    rrp_cleared_bilateral_sponsored_g30,
])
rrp_cleared_bilateral.columns = [
    'Cleared Bilateral Special O/N',
    'Cleared Bilateral Special L30',
    'Cleared Bilateral Special G30',
    'Cleared Bilateral General O/N',
    'Cleared Bilateral General L30',
    'Cleared Bilateral General G30',
    'Cleared Bilateral Sponsored O/N',
    'Cleared Bilateral Sponsored L30',
    'Cleared Bilateral Sponsored G30',
]
with open(Path(DATA_DIR) / 'rrp_cleared_bilateral.pkl', 'wb') as file:
    pickle.dump(rrp_cleared_bilateral, file)

rrp_gcf_on = get_newyork_fed_data('PDSIRRA-GCFUTSET')
rrp_gcf_l30 = get_newyork_fed_data('PDSIRRA-GCFUTSETTAL30')
rrp_gcf_g30 = get_newyork_fed_data('PDSIRRA-GCFUTSETTAG30')

tri_ex_gcf_gc_on = get_newyork_fed_data('PDSIRRA-TRIGUTSET')
tri_ex_gcf_gc_l30 = get_newyork_fed_data('PDSIRRA-TRIGUTSETTAL30')
tri_ex_gcf_gc_g30 = get_newyork_fed_data('PDSIRRA-TRIGUTSETTAG30')

tri_ex_gcf_sponsored_gc_on = get_newyork_fed_data('PDSIRRA-TRISPUTSET')
tri_ex_gcf_sponsored_gc_l30 = get_newyork_fed_data('PDSIRRA-TRISPUTSETTAL30')
tri_ex_gcf_sponsored_gc_g30 = get_newyork_fed_data('PDSIRRA-TRISPUTSETTAG30')

rrp_gcf_and_triparty = merge_dfs([
    rrp_gcf_on,
    rrp_gcf_l30,
    rrp_gcf_g30,
    tri_ex_gcf_gc_on,
    tri_ex_gcf_gc_l30,
    tri_ex_gcf_gc_g30,
    tri_ex_gcf_sponsored_gc_on,
    tri_ex_gcf_sponsored_gc_l30,
    tri_ex_gcf_sponsored_gc_g30,
])
rrp_gcf_and_triparty.columns = [
    'GCF O/N',
    'GCF L30',
    'GCF G30',
    'Tri-Party ex. GCF GC O/N',
    'Tri-Party ex. GCF GC L30',
    'Tri-Party ex. GCF GC G30',
    'Tri-Party ex. Sponsored GCF GC O/N',
    'Tri-Party ex. Sponsored GCF GC L30',
    'Tri-Party ex. Sponsored GCF GC G30',
]
with open(Path(DATA_DIR) / 'rrp_cleared_bilateral.pkl', 'wb') as file:
    pickle.dump(rrp_cleared_bilateral, file)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ PRIMARY DEALER DATA ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

repo_uncleared_bilateral_special_on = get_newyork_fed_data('PDSORA-UBSUTSET')
repo_uncleared_bilateral_special_l30 = get_newyork_fed_data('PDSORA-UBSUTSETTAL30')
repo_uncleared_bilateral_special_g30 = get_newyork_fed_data('PDSORA-UBSUTSETTAG30')

repo_uncleared_bilateral_general_on = get_newyork_fed_data('PDSORA-UBGUTSET')
repo_uncleared_bilateral_general_l30 = get_newyork_fed_data('PDSORA-UBGUTSETTAL30')
repo_uncleared_bilateral_general_g30 = get_newyork_fed_data('PDSORA-UBGUTSETTAG30')

repo_uncleared_bilateral = merge_dfs([
    repo_uncleared_bilateral_special_on,
    repo_uncleared_bilateral_special_l30,
    repo_uncleared_bilateral_special_g30,
    repo_uncleared_bilateral_general_on,
    repo_uncleared_bilateral_general_l30,
    repo_uncleared_bilateral_general_g30,
])
repo_uncleared_bilateral.columns = [
    'Uncleared Bilateral Special O/N',
    'Uncleared Bilateral Special L30',
    'Uncleared Bilateral Special G30',
    'Uncleared Bilateral General O/N',
    'Uncleared Bilateral General L30',
    'Uncleared Bilateral General G30',
]
with open(Path(DATA_DIR) / 'repo_uncleared_bilateral.pkl', 'wb') as file:
    pickle.dump(repo_uncleared_bilateral, file)

repo_cleared_bilateral_special_on = get_newyork_fed_data('PDSORA-CBSUTSET')
repo_cleared_bilateral_special_l30 = get_newyork_fed_data('PDSORA-CBSUTSETTAL30')
repo_cleared_bilateral_special_g30 = get_newyork_fed_data('PDSORA-CBSUTSETTAG30')

repo_cleared_bilateral_general_on = get_newyork_fed_data('PDSORA-CBGUTSET')
repo_cleared_bilateral_general_l30 = get_newyork_fed_data('PDSORA-CBGUTSETTAL30')
repo_cleared_bilateral_general_g30 = get_newyork_fed_data('PDSORA-CBGUTSETTAG30')

repo_cleared_bilateral_sponsored_on = get_newyork_fed_data('PDSORA-CBSPUTSET')
repo_cleared_bilateral_sponsored_l30 = get_newyork_fed_data('PDSORA-CBSPUTSETTAL30')
repo_cleared_bilateral_sponsored_g30 = get_newyork_fed_data('PDSORA-CBSPUTSETTAG30')

repo_cleared_bilateral = merge_dfs([
    repo_cleared_bilateral_special_on,
    repo_cleared_bilateral_special_l30,
    repo_cleared_bilateral_special_g30,
    repo_cleared_bilateral_general_on,
    repo_cleared_bilateral_general_l30,
    repo_cleared_bilateral_general_g30,
    repo_cleared_bilateral_sponsored_on,
    repo_cleared_bilateral_sponsored_l30,
    repo_cleared_bilateral_sponsored_g30,
])
repo_cleared_bilateral.columns = [
    'Cleared Bilateral Special O/N',
    'Cleared Bilateral Special L30',
    'Cleared Bilateral Special G30',
    'Cleared Bilateral General O/N',
    'Cleared Bilateral General L30',
    'Cleared Bilateral General G30',
    'Cleared Bilateral Sponsored O/N',
    'Cleared Bilateral Sponsored L30',
    'Cleared Bilateral Sponsored G30',
]
with open(Path(DATA_DIR) / 'repo_cleared_bilateral.pkl', 'wb') as file:
    pickle.dump(repo_cleared_bilateral, file)

repo_gcf_on = get_newyork_fed_data('PDSORA-GCFUTSET')
repo_gcf_l30 = get_newyork_fed_data('PDSORA-GCFUTSETTAL30')
repo_gcf_g30 = get_newyork_fed_data('PDSORA-GCFUTSETTAG30')

tri_ex_gcf_gc_on = get_newyork_fed_data('PDSORA-TRIGUTSET')
tri_ex_gcf_gc_l30 = get_newyork_fed_data('PDSORA-TRIGUTSETTAL30')
tri_ex_gcf_gc_g30 = get_newyork_fed_data('PDSORA-TRIGUTSETTAG30')

tri_ex_gcf_sponsored_gc_on = get_newyork_fed_data('PDSORA-TRISPUTSET')
tri_ex_gcf_sponsored_gc_l30 = get_newyork_fed_data('PDSORA-TRISPUTSETTAL30')
tri_ex_gcf_sponsored_gc_g30 = get_newyork_fed_data('PDSORA-TRISPUTSETTAG30')

repo_gcf_and_triparty = merge_dfs([
    repo_gcf_on,
    repo_gcf_l30,
    repo_gcf_g30,
    tri_ex_gcf_gc_on,
    tri_ex_gcf_gc_l30,
    tri_ex_gcf_gc_g30,
    tri_ex_gcf_sponsored_gc_on,
    tri_ex_gcf_sponsored_gc_l30,
    tri_ex_gcf_sponsored_gc_g30,
])
repo_gcf_and_triparty.columns = [
    'GCF O/N',
    'GCF L30',
    'GCF G30',
    'Tri-Party ex. GCF GC O/N',
    'Tri-Party ex. GCF GC L30',
    'Tri-Party ex. GCF GC G30',
    'Tri-Party ex. Sponsored GCF GC O/N',
    'Tri-Party ex. Sponsored GCF GC L30',
    'Tri-Party ex. Sponsored GCF GC G30',
]
with open(Path(DATA_DIR) / 'repo_cleared_bilateral.pkl', 'wb') as file:
    pickle.dump(repo_cleared_bilateral, file)
