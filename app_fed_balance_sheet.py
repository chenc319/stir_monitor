### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- FED BALANCE SHEET -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### FUNCTIONS AND PACKAGES ###
from Functions import *
from pathlib import Path
import os
DATA_DIR = os.getenv('DATA_DIR', 'data')

asset_colors = {
    'securities_outright': '#5FB3FF',   # Vivid sky blue (QE, stable)
    'lending_portfolio':   '#2DCDB2',   # Bright teal/mint (portfolio)
    'treasuries':          '#FFC145',   # Sun gold (Treasury)
    'mbs':                 '#FF6969',   # Approachable coral (MBS)
    'permanent_lending':   '#54C6EB',   # Aqua blue (permanent lending)
    'temporary_lending':   '#FFD166',   # Citrus yellow-orange (temp lending)
    'srf':                 '#6FE7DD',   # Lively turquoise (repo facility)
    'discount_window':     '#8D8DFF',   # Periwinkle (DW lending)
    'fx_swap_line':        '#A685E2',   # Pleasant purple (FX swaps)
    'ppp':                 '#FF8FAB',   # Bright pink (PPP)
    'ms':                  '#FFA952',   # Peach (Main Street)
}

liab_colors = {
    'currency':         '#F9DB6D',   # Warm gold (currency)
    'rrp':              '#3CB1CD',   # Vivid blue (RRP)
    'foreign_repo':     '#85F4FA',   # Electric cyan (foreign repo)
    'reserves':         '#21A179',   # Strong green (reserves)
    'tga':              '#B084CC',   # Violet (TGA)
    'gse_dmfu':         '#FFB685',   # Soft orange (GSE/DMFU)
    'total_reserves':   '#21A179',   # Match reserves
    'total_rrp':        '#3CB1CD',   # Match RRP
}

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- ASSETS ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_balance_sheet_assets(start, end, **kwargs):
    ### ASSETS ###
    with open(Path(DATA_DIR) / 'fed_assets_securities_outright.pkl', 'rb') as file:
        fed_assets_securities_outright = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_treasury_securities.pkl', 'rb') as file:
        fed_assets_treasury_securities = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_notes_and_bonds.pkl', 'rb') as file:
        fed_assets_notes_and_bonds = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_mbs.pkl', 'rb') as file:
        fed_assets_mbs = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_total.pkl', 'rb') as file:
        fed_assets_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_total.pkl', 'rb') as file:
        fed_assets_total = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_srf.pkl', 'rb') as file:
        fed_assets_srf = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_dw_primary.pkl', 'rb') as file:
        fed_assets_dw_primary = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_dw_secondary.pkl', 'rb') as file:
        fed_assets_dw_secondary = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_dw_seasonal.pkl', 'rb') as file:
        fed_assets_dw_seasonal = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_fx_swap_line.pkl', 'rb') as file:
        fed_assets_fx_swap_line = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_main_street.pkl', 'rb') as file:
        fed_assets_main_street = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_assets_ppp_facility.pkl', 'rb') as file:
        fed_assets_ppp_facility = pickle.load(file)

    fed_assets_merge = merge_dfs([fed_assets_securities_outright,
                                  fed_assets_treasury_securities,
                                  fed_assets_notes_and_bonds,
                                  fed_assets_mbs,
                                  fed_assets_srf,
                                  fed_assets_dw_primary,
                                  fed_assets_dw_secondary,
                                  fed_assets_dw_seasonal,
                                  fed_assets_fx_swap_line,
                                  fed_assets_main_street,
                                  fed_assets_ppp_facility,
                                  fed_assets_total]).dropna()
    fed_assets_merge.index = pd.to_datetime(fed_assets_merge.index.values)
    fed_assets_merge.columns = ['securities_outright',
                                'treasuries',
                                'notes_bonds',
                                'mbs',
                                'srf',
                                'dw_primary',
                                'dw_secondary',
                                'dw_seasonal',
                                'fx_swap_line',
                                'ms',
                                'ppp',
                                'total']
    fed_assets_merge['discount_window'] = (fed_assets_merge['dw_primary']+
                                           fed_assets_merge['dw_secondary']+
                                           fed_assets_merge['dw_seasonal'])
    fed_assets_merge['permanent_lending'] = (fed_assets_merge['srf']+
                                             fed_assets_merge['discount_window']+
                                             fed_assets_merge['fx_swap_line'])
    fed_assets_merge['temporary_lending'] = (fed_assets_merge['ms']+
                                             fed_assets_merge['ppp'])
    fed_assets_merge['lending_portfolio'] = (fed_assets_merge['permanent_lending'] +
                                             fed_assets_merge['temporary_lending'])
    fed_assets_merge_diff = fed_assets_merge.diff(1).dropna()
    fed_assets_merge_diff_mean = fed_assets_merge_diff.mean(axis=0)
    fed_assets_merge_diff_std = fed_assets_merge_diff.std(axis=0)
    fed_assets_merge_diff_z = (fed_assets_merge_diff - fed_assets_merge_diff_mean) / fed_assets_merge_diff_std

    fed_assets_merge = fed_assets_merge[start:end]
    fed_assets_merge_diff = fed_assets_merge_diff[start:end]
    fed_assets_merge_diff_z = fed_assets_merge_diff_z[start:end]

    ### ASSETS SUMMARY ###
    streamlit_plot(
        fed_assets_merge,
        ['securities_outright', 'lending_portfolio'],
        [asset_colors['securities_outright'], asset_colors['lending_portfolio']],
        ['Securities Outright','Lending Portfolio'],
        "Assets: Summary",
        ""
    )

    ### QE SECURITIES ###
    st.title("1. QE Securities")
    streamlit_plot(
        fed_assets_merge,
        ['treasuries', 'mbs'],
        [asset_colors['treasuries'], asset_colors['mbs']],
        ['Treasuries','MBS'],
        "QE Securities: Weekly Averages",
        ""
    )
    streamlit_plot(
        fed_assets_merge_diff,
        ['treasuries', 'mbs'],
        [asset_colors['treasuries'], asset_colors['mbs']],
        ['Treasuries','MBS'],
        "QE Securities: Weekly Changes",
        "",
        rows = 1,
        cols = 2
    )
    streamlit_plot(
        fed_assets_merge_diff_z,
        ['treasuries', 'mbs'],
        [asset_colors['treasuries'], asset_colors['mbs']],
        ['Treasuries','MBS'],
        "QE Securities: Weekly Z-Scored",
        "",
        rows = 1,
        cols = 2
    )

    ### LENDING PORTFOLIO ###
    st.title("2. Lending Portfolio")
    streamlit_plot(
        fed_assets_merge,
        ['permanent_lending', 'temporary_lending'],
        [asset_colors['permanent_lending'], asset_colors['temporary_lending']],
        [
            'Permanent Lending Portfolio',
            'Temporary Lending Portfolio'],
        "Lending Portfolio: Weekly Averages",
        ""
    )
    streamlit_plot(
        fed_assets_merge_diff_z,
        ['srf', 'discount_window','fx_swap_line'],
        [asset_colors['srf'], asset_colors['discount_window'], asset_colors['fx_swap_line']],
        [
            'SRF',
            'Discount Window',
            'FX Swap Line'],
        "Permanent Lending Portfolio: Weekly Averages",
        "",
        rows = 1,
        cols = 3
    )
    streamlit_plot(
        fed_assets_merge_diff_z,
        ['ppp', 'ms'],
        [asset_colors['ppp'], asset_colors['ms']],
        [
            'PPP Liquidity Facility (Direct Lending)',
            'Main Street Lending Facility (Indirect Lending)'],
        "Temporary Lending Portfolio: Weekly Averages",
        "",
        rows = 1,
        cols = 2
    )

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- LIABILITIES ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_fed_balance_sheet_liabilities(start, end, **kwargs):
    ### LIABILITIES ###
    with open(Path(DATA_DIR) / 'fed_liabilities_currency.pkl', 'rb') as file:
        fed_liabilities_currency = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_foreign_repo.pkl', 'rb') as file:
        fed_liabilities_foreign_repo = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_rrp.pkl', 'rb') as file:
        fed_liabilities_rrp = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_reserves.pkl', 'rb') as file:
        fed_liabilities_reserves = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_tga.pkl', 'rb') as file:
        fed_liabilities_tga = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_gse_dmfu.pkl', 'rb') as file:
        fed_liabilities_gse_dmfu = pickle.load(file)
    with open(Path(DATA_DIR) / 'fed_liabilities_total.pkl', 'rb') as file:
        fed_liabilities_total = pickle.load(file)
    fed_liabilities_merge = merge_dfs([fed_liabilities_currency,
                                       fed_liabilities_rrp,
                                       fed_liabilities_foreign_repo,
                                       fed_liabilities_reserves,
                                       fed_liabilities_tga,
                                       fed_liabilities_gse_dmfu,
                                       fed_liabilities_total]).dropna()
    fed_liabilities_merge.index = pd.to_datetime(fed_liabilities_merge.index.values)
    fed_liabilities_merge.columns = ['currency','rrp','foreign_repo',
                                     'reserves','tga','gse_dmfu','total']
    fed_liabilities_merge['others'] = (fed_liabilities_merge['total']-
                                       fed_liabilities_merge['currency'] -
                                       fed_liabilities_merge['rrp']-
                                       fed_liabilities_merge['foreign_repo']-
                                       fed_liabilities_merge['reserves']-
                                       fed_liabilities_merge['tga']-
                                       fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['rrp_total'] = fed_liabilities_merge['rrp'] + fed_liabilities_merge['foreign_repo']
    fed_liabilities_merge['reserves_total'] = (fed_liabilities_merge['reserves'] +
                                               fed_liabilities_merge['tga'] +
                                               fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['total_reserves'] = (fed_liabilities_merge['reserves'] +
                                               fed_liabilities_merge['tga'] +
                                               fed_liabilities_merge['gse_dmfu'])
    fed_liabilities_merge['total_rrp'] = (fed_liabilities_merge['rrp'] + fed_liabilities_merge['foreign_repo'])
    fed_liabilities_merge_diff = fed_liabilities_merge.diff(1).dropna()

    fed_liabilities_merge_diff_mean = fed_liabilities_merge_diff.mean(axis=0)
    fed_liabilities_merge_diff_std = fed_liabilities_merge_diff.std(axis=0)
    fed_liabilities_merge_diff_z = (fed_liabilities_merge_diff -
                                    fed_liabilities_merge_diff_mean) / fed_liabilities_merge_diff_std

    fed_liabilities_merge = fed_liabilities_merge[start:end]
    fed_liabilities_merge_diff = fed_liabilities_merge_diff[start:end]
    fed_liabilities_merge_diff_z = fed_liabilities_merge_diff_z[start:end]

    ### LIABILITIES SUMMARY ###
    streamlit_plot(
        fed_liabilities_merge,
        ['currency', 'total_reserves', 'total_rrp'],
        [liab_colors['currency'], liab_colors['total_reserves'], liab_colors['total_rrp']],
        [
            'Currency',
            'Total Reserves',
            'Total RRP'],
        "Liabilities: Summary",
        ""
    )

    ### PLOT ###
    streamlit_plot(
        fed_liabilities_merge,
        ['currency', 'rrp', 'foreign_repo', 'reserves', 'tga', 'gse_dmfu'],
        [liab_colors['currency'],
         liab_colors['rrp'],
         liab_colors['foreign_repo'],
         liab_colors['reserves'],
         liab_colors['tga'],
         liab_colors['gse_dmfu']],
        [
            'Currency',
            'RRP Facility',
            'Foreign RP Facility',
            'DI Reserves',
            'TGA',
            'GSE/DMFU'
        ],
        "Liabilities: Components",
        ""
    )

    streamlit_plot(
        fed_liabilities_merge,
        ['currency', 'rrp', 'foreign_repo', 'reserves', 'tga', 'gse_dmfu'],
        [liab_colors['currency'],
         liab_colors['rrp'],
         liab_colors['foreign_repo'],
         liab_colors['reserves'],
         liab_colors['tga'],
         liab_colors['gse_dmfu']],
        [
            'Currency',
            'RRP Facility',
            'Foreign RP Facility',
            'DI Reserves',
            'TGA',
            'GSE/DMFU'
        ],
        "Liabilities: Weekly Averages",
        "",
        rows = 3,
        cols = 2
    )

    streamlit_plot(
        fed_liabilities_merge_diff,
        ['currency', 'rrp', 'foreign_repo', 'reserves', 'tga', 'gse_dmfu'],
        [liab_colors['currency'],
         liab_colors['rrp'],
         liab_colors['foreign_repo'],
         liab_colors['reserves'],
         liab_colors['tga'],
         liab_colors['gse_dmfu']],
        [
            'Currency',
            'RRP Facility',
            'Foreign RP Facility',
            'DI Reserves',
            'TGA',
            'GSE/DMFU'
        ],
        "Liabilities: Weekly Change",
        "",
        rows=3,
        cols=2
    )

    streamlit_plot(
        fed_liabilities_merge_diff_z,
        ['currency', 'rrp', 'foreign_repo', 'reserves', 'tga', 'gse_dmfu'],
        [liab_colors['currency'],
         liab_colors['rrp'],
         liab_colors['foreign_repo'],
         liab_colors['reserves'],
         liab_colors['tga'],
         liab_colors['gse_dmfu']],
        [
            'Currency',
            'RRP Facility',
            'Foreign RP Facility',
            'DI Reserves',
            'TGA',
            'GSE/DMFU'
        ],
        "Liabilities: Weekly Change Z-Scored",
        "",
        rows=3,
        cols=2
    )
