### ---------------------------------------------------------------------------------------- ###
### -------------------------------- PACKAGES AND FUNCTIONS -------------------------------- ###
### ---------------------------------------------------------------------------------------- ###

### IMPORT OTHER SCRIPTS ###
import streamlit as st
import app_risk_checks
# from app_auctions import *
# from app_cash import *
import app_cross_rate
# from app_futures import *
# from app_primary_dealers import *
# from app_system import *
# from app_repo import *

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
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state.authenticated = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state.authenticated = False

    if not st.session_state.authenticated:
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
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime('2025-04-01'))
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

with tab1:
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

# with tab3:
    # st.markdown('<div class="tab-title">', unsafe_allow_html=True)
    # st.title("Repo")
    # st.markdown('</div>', unsafe_allow_html=True)
    # peers(start_date,
    #       end_date)

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

# with tab6:
#     st.markdown('<div class="tab-title">', unsafe_allow_html=True)
#     st.title("Auctions")
#     st.markdown('</div>', unsafe_allow_html=True)
#     stock_ownership(ticker)

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





