### ---------------------------------------------------------------------------------------- ###
### -------------------------------- PACKAGES AND FUNCTIONS -------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

### IMPORT OTHER SCRIPTS ###
import streamlit as st
import pandas as pd
import functools as ft
import app_risk_checks
import app_auctions
# import app_cash
import app_cross_rate
# import app_futures
# import app_primary_dealers
# import app_system
import app_repo

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

# Initialize session state if not already done
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state.get("password", None) == st.secrets["password"]:
            st.session_state.authenticated = True
            if "password" in st.session_state:
                del st.session_state["password"]  # Don't store password
        else:
            st.session_state.authenticated = False

    if not st.session_state.get('authenticated', False):
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    return True


# Main app logic
if not check_password():
    st.stop()


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
menu = st.sidebar.radio(
    "Go to section:",
    ['Risk Checks',
     'Bank System Mapping',
     'Repo',
     'Cross Rate',
     'Cash',
     'Auctions',
     'Futures',
     'Primary Dealers']
)
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime('2019-12-31'))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime('today'))
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['Risk Checks',
                                                          'Bank System Mapping',
                                                          'Repo',
                                                          'Cross Rate',
                                                          'Cash',
                                                          'Auctions',
                                                          'Futures',
                                                          'Primary Dealers'])


### ---------------------------------------------------------------------------------------- ###
### -------------------------------------- BASIC INFO -------------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

with menu == 'Risk Checks':
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
### ---------------------------- HISTORICAL VOLATILITY ANALYSIS ---------------------------- ###
### ---------------------------------------------------------------------------------------- ###

# with tab2:
    # st.markdown('<div class="tab-title">', unsafe_allow_html=True)
    # st.title("Bank System Mapping")
    # st.markdown('</div>', unsafe_allow_html=True)
    # return_and_volatility(ticker,
    #                       start_date,
    #                       end_date)

### ---------------------------------------------------------------------------------------- ###
### ------------------------------- RESPECTIVE PEERS ANALYSIS ------------------------------ ###
### ---------------------------------------------------------------------------------------- ###

with tab3:
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
### ------------------------------- HISTORICAL VOLUME AND ADV ------------------------------ ###
### ---------------------------------------------------------------------------------------- ###

with tab4:
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
### --------------------------------- PRICE-IMPACT MODELING -------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

# with tab5:
    # st.markdown('<div class="tab-title">', unsafe_allow_html=True)
    # st.title("Cash")
    # st.markdown('</div>', unsafe_allow_html=True)
    # price_impact(ticker,
    #              start_date,
    #              end_date)

### ---------------------------------------------------------------------------------------- ###
### --------------------------------- STOCK OWNERSHIP INFO --------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

with tab6:
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
### ----------------------------------- INSIDER ACTIVITY ----------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

# with tab7:
#     st.markdown('<div class="tab-title">', unsafe_allow_html=True)
#     st.title("Futures")
#     st.markdown('</div>', unsafe_allow_html=True)
#     stock_ownership(ticker)

### ---------------------------------------------------------------------------------------- ###
### --------------------------------- PROFITABILITY METRICS -------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

# with tab8:
#     st.markdown('<div class="tab-title">', unsafe_allow_html=True)
#     st.title("Primary Dealers")
#     st.markdown('</div>', unsafe_allow_html=True)
#     stock_ownership(ticker)





