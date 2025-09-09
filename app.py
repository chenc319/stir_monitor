### ---------------------------------------------------------------------------------------- ###
### -------------------------------- PACKAGES AND FUNCTIONS -------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

### IMPORT OTHER SCRIPTS ###
import streamlit as st
import pandas as pd
import functools as ft
import app_risk_checks
import app_fed_balance_sheet
import app_shadow_banks
import app_repo
import app_cross_rate
import app_cash
import app_auctions
import app_futures
import app_primary_dealers
import app_fed_operations
import app_bulletin
import app_datapull
import time

### FUNCTIONS ###
def merge_dfs(array_of_dfs):
    new_df = ft.reduce(lambda left,
                              right: pd.merge(left,
                                                    right,
                                                    left_index=True,
                                                    right_index=True,
                                                    how='outer'), array_of_dfs)
    return(new_df)

### ---------------------------------------------------------------------------------------- ###
### --------------------------------- CONFIGURE STREAMLIT ---------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

### CONFIGURE PAGE SETTINGS ###
st.set_page_config(
    page_title="Mistral STIR Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# # Initialize session state if not already done
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = False
#
# def check_password():
#     """Returns True if the user had the correct password."""
#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if st.session_state.get("password", None) == st.secrets["password"]:
#             st.session_state.authenticated = True
#             if "password" in st.session_state:
#                 del st.session_state["password"]  # Don't store password
#         else:
#             st.session_state.authenticated = False
#
#     if not st.session_state.get('authenticated', False):
#         st.text_input(
#             "Password", type="password", on_change=password_entered, key="password"
#         )
#         return False
#     return True
#
#
# # Main app logic
# if not check_password():
#     st.stop()


st.markdown("""
    <style>
    .header-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        padding: 8px;
        background-color: white;
        z-index: 999;
        border-bottom: 1px solid #f0f2f6;
        font-size: 14px;
    }
    .main {
        margin-top: 60px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 10px;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

### SIDEBAR ###
st.sidebar.title("Mistral STIR Monitor")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime('2019-12-31'))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime('today'))

progress_placeholder = st.sidebar.empty()
if st.sidebar.button("Refresh Data"):
    progress_bar = progress_placeholder.progress(0)
    for percent_complete in range(1, 101):
        time.sleep(0.01)
        progress_bar.progress(percent_complete)
    app_datapull.refresh_all_data()
    st.sidebar.success("Data refreshed!")
    progress_placeholder.empty()
else:
    progress_placeholder.empty()

menu = st.sidebar.radio(
    "Go to section:",
    ['Risk Checks',
     'Fed Balance Sheet'
     'Fed Operations',
     'Shadow Banks',
     'Repo',
     'Cross Rate',
     'Cash',
     'Auctions',
     'Futures',
     'Primary Dealers',
     'US Treasury Bulletin']
)


### ---------------------------------------------------------------------------------------- ###
### -------------------------------------- RISK CHECKS ------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

if menu == 'Risk Checks':
    st.title("Risk Checks")
    app_risk_checks.plot_dash_for_cash_spread(start_date, end_date)
    app_risk_checks.plot_new_sofr_system(start_date, end_date)
    app_risk_checks.plot_repo_rate_complex(start_date, end_date)
    app_risk_checks.plot_sofr_distribution(start_date, end_date)
    app_risk_checks.plot_fed_balance_sheet(start_date, end_date)
    app_risk_checks.plot_monitoring_reserves(start_date, end_date)
    app_risk_checks.plot_fed_action_vs_reserve_response(start_date, end_date)
    app_risk_checks.plot_fed_action_vs_reserve_response_v2(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### -------------------------------------- RISK CHECKS ------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Fed Operations':
    st.title("Fed Balance Sheet")
    app_fed_operations.plot_soma_holdings(start_date, end_date)
    st.title("SRF Operations")
    app_fed_operations.plot_fed_repo_operations(start_date, end_date)
    st.title("ONRRP Operations")
    app_fed_operations.plot_fed_rrp_operations(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### -------------------------------------- RISK CHECKS ------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Fed Balance Sheet':
    st.title("Fed Balance Sheet Liabilities")
    app_fed_balance_sheet.plot_fed_balance_sheet_liabilities(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### ------------------------------ SHADOW BANK SYSTEM MAPPING ------------------------------ ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Shadow Banks':
    st.title("Shadow Bank Components")
    st.title('Summary')
    app_shadow_banks.plot_shadow_bank_summary(start_date, end_date)
    st.title('Money Market Funds')
    app_shadow_banks.plot_shadow_bank_mmf_repo(start_date,end_date)
    app_shadow_banks.plot_shadow_bank_mmf_on_repo(start_date,end_date)
    st.title('Private Investment Funds')
    app_shadow_banks.plot_shadow_bank_private_investments(start_date,end_date)
    st.title('Shadow Bank Assets Mapping')
    app_shadow_banks.plot_shadow_bank_assets(start_date, end_date)
    st.title('Shadow Bank Liabilities Mapping')
    app_shadow_banks.plot_shadow_bank_liabilities(start_date,end_date)


### ---------------------------------------------------------------------------------------- ###
### ------------------------------------------ REPO ---------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Repo':
    st.title("Repo")
    app_repo.plot_proxy_percent_without_clearing(start_date, end_date)
    app_repo.plot_volume_per_venue(start_date, end_date)
    app_repo.plot_mmf_by_asset(start_date, end_date)
    app_repo.plot_6m_volume_change(start_date, end_date)
    app_repo.plot_volume_invested_in_mmf(start_date, end_date)
    app_repo.plot_rrp_vs_foreign_rrp(start_date, end_date)
    app_repo.plot_mmf_repo_vs_non_repo(start_date, end_date)
    app_repo.plot_triparty_adjusted_for_rrp(start_date, end_date)
    app_repo.plot_mmf_allocation_by_counterparty(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### --------------------------------------- CROSS RATE ------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Cross Rate':
    st.title("Cross Rate")
    app_cross_rate.plot_iorb_spreads(start_date, end_date)
    app_cross_rate.plot_gcf_tri_spread(start_date, end_date)
    app_cross_rate.plot_triparty_term_spread(start_date, end_date)
    app_cross_rate.plot_sofr_effr_chart(start_date, end_date)
    app_cross_rate.plot_repo_rate_complex_cross(start_date, end_date)
    app_cross_rate.plot_dollar_lending_complex(start_date, end_date)
    app_cross_rate.plot_sofr_floor_ceiling(start_date, end_date)
    app_cross_rate.plot_unsecured_lending_floor_ceiling(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### ----------------------------------------- CASH ----------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Cash':
    st.title("Cash")
    app_cash.plot_tga(start_date, end_date)
    app_cash.plot_rrp(start_date, end_date)
    app_cash.plot_reserves(start_date, end_date)
    app_cash.plot_mmf_repo_vs_non_repo(start_date, end_date)
    app_cash.plot_asset_allocation_mmf(start_date, end_date)
    app_cash.plot_reserves_non_fed_repo_rrp(start_date, end_date)
    app_cash.plot_reserves_liabilities_system(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### --------------------------------------- AUCTIONS --------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Auctions':
    st.title("Auctions")
    app_auctions.plot_issuance_by_security(start_date, end_date)
    app_auctions.plot_bills_issuance(start_date, end_date)
    app_auctions.plot_notes_issuance(start_date, end_date)
    app_auctions.plot_bonds_issuance(start_date, end_date)
    app_auctions.plot_bills_dealer_ratio(start_date, end_date)
    app_auctions.plot_bonds_dealer_ratio(start_date, end_date)
    app_auctions.plot_notes_dealer_ratio(start_date, end_date)
    app_auctions.plot_bills_bid_to_cover(start_date, end_date)
    app_auctions.plot_bonds_bid_to_cover(start_date, end_date)
    app_auctions.plot_notes_bid_to_cover(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### ---------------------------------------- FUTURES --------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Futures':
    st.title("Futures")
    app_futures.plot_futures_leverage_money_short(start_date, end_date)
    app_futures.plot_end_of_quarter_spreads(start_date, end_date)
    app_futures.plot_end_of_month_spreads(start_date, end_date)
    app_futures.plot_stability_lower_roc(start_date, end_date)
    app_futures.plot_how_did_levels_change(start_date, end_date)

### ---------------------------------------------------------------------------------------- ###
### ------------------------------------ PRIMARY DEALERS ----------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

elif menu == 'Primary Dealers':
    st.title("Primary Dealers")
    app_primary_dealers.plot_sponsored_volumes_solution(start_date, end_date)
    app_primary_dealers.plot_sponsored_volumes(start_date, end_date)
    app_primary_dealers.plot_pct_dvp_sponsored(start_date, end_date)
    app_primary_dealers.plot_net_positions_bills_vs_bonds(start_date, end_date)
    app_primary_dealers.plot_net_positions_by_bond_tenor(start_date, end_date)
    app_primary_dealers.plot_net_change_by_bond_tenor(start_date, end_date)


elif menu == 'US Treasury Bulletin':
    st.title("US Treasury Bulletin")
    st.title("Ownership")
    app_bulletin.plot_treasury_ownership(start_date,end_date)
    st.title('Buybacks')
    app_bulletin.plot_buyback_volume_by_maturity(start_date,end_date)