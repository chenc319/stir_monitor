### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- PRIMARY DEALERS --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### FUNCTIONS ###
from Functions import *
from pathlib import Path
import os
DATA_DIR = os.getenv('DATA_DIR', 'data')

### LOAD DATA ###
with open(Path(DATA_DIR) / 'pd_pos_dict.pkl', 'rb') as file:
    pd_pos_dict = pickle.load(file)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- PRIMARY DEALER WAREHOUSE OVERVIEW ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def primary_dealer_snapshot(start, end, **kwargs):
    base_series = pd_pos_dict["All USTs"]
    all_dates = base_series.index.sort_values()

    for key, obj in pd_pos_dict.items():
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            pd_pos_dict[key] = obj.round(1)
            pd_pos_dict[key] = pd_pos_dict[key].where(
                pd_pos_dict[key] != 0, 0
            )

    chosen_date = st.selectbox(
        "Select Holdings Snapshot Date",
        options=all_dates,
        index=len(all_dates) - 1,
        format_func=lambda d: d.strftime("%Y-%m-%d"),
    )
    pd_pos_snapshot = pd.DataFrame({
        'All USTs': pd_pos_dict['All USTs'].loc[chosen_date],

        'Coupons': ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg'],
        'All Coupons': pd_pos_dict['All Coupons'].loc[chosen_date],
        'Coupons <2y': pd_pos_dict['Coupons <2y'].loc[chosen_date],
        'Coupons 2-3y': pd_pos_dict['Coupons 2-3y'].loc[chosen_date],
        'Coupons 3-6y': pd_pos_dict['Coupons 3-6y'].loc[chosen_date],
        'Coupons 6-7y': pd_pos_dict['Coupons 6-7y'].loc[chosen_date],
        'Coupons 7-11y': pd_pos_dict['Coupons 7-11y'].loc[chosen_date],
        'Coupons 11-21y': pd_pos_dict['Coupons 11-21y'].loc[chosen_date],
        'Coupons >21y': pd_pos_dict['Coupons >21y'].loc[chosen_date],

        'TIPS': ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg'],
        'All TIPS': pd_pos_dict['All TIPS'].loc[chosen_date],
        'TIPS <2y': pd_pos_dict['TIPS <2y'].loc[chosen_date],
        'TIPS 2-6y': pd_pos_dict['TIPS 2-6y'].loc[chosen_date],
        'TIPS 6-11y': pd_pos_dict['TIPS 6-11y'].loc[chosen_date],
        'TIPS >11y': pd_pos_dict['TIPS >11y'].loc[chosen_date],

        'Bills': ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg'],
        'All Bills': pd_pos_dict['All Bills'].loc[chosen_date],

        'FRNs': ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg'],
        'All FRNs': pd_pos_dict['All FRNs'].loc[chosen_date],
    }).T

    df = pd_pos_snapshot.copy()
    cols = ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg']
    df = df[cols]

    # all headers (untabbed + bold)
    section_rows = {
        "Total",
        "All USTs",
        "Coupons",
        "TIPS",
        "Bills",
        "FRNs",
    }

    # only these get the dark-blue band
    dark_blue_rows = {
        "Total",
        "Coupons",
        "TIPS",
        "Bills",
        "FRNs"
    }

    def style_fed_table(df):
        styler = df.style

        def numeric_formatter(x):
            if isinstance(x, (int, float)) and not pd.isna(x):
                return f"{x:,.1f}"
            return x

        styler = styler.format(numeric_formatter, na_rep="")

        styler = styler.set_table_styles(
            [
                {
                    "selector": "table",
                    "props": [
                        ("border-collapse", "collapse"),
                        ("font-family", "Calibri, Arial, sans-serif"),
                        ("font-size", "14px"),
                        ("table-layout", "fixed"),
                        ("width", "100%"),
                    ],
                },
                {
                    "selector": "th.col_heading",
                    "props": [
                        ("background-color", "#005A9C"),
                        ("color", "white"),
                        ("text-align", "center"),
                        ("border", "1px solid #CCCCCC"),
                        ("font-weight", "bold"),
                    ],
                },
                {
                    "selector": "th.row_heading",
                    "props": [
                        ("text-align", "left"),
                        ("border", "1px solid #CCCCCC"),
                        ("white-space", "nowrap"),
                        ("width", "200px"),
                        ("max-width", "200px"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("border", "1px solid #CCCCCC"),
                        ("text-align", "center"),
                    ],
                },
            ]
        )

        numeric_cols = ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg']
        existing_cols = [c for c in numeric_cols if c in df.columns]
        if existing_cols:
            styler = styler.set_properties(
                subset=pd.IndexSlice[:, existing_cols],
                **{"text-align": "center"},
            )
            data_share = 90
            per_col = data_share / len(existing_cols)
            styler = styler.set_table_styles(
                styler.table_styles
                + [
                    {
                        "selector": "col",
                        "props": [("width", f"{per_col:.2f}%")],
                    }
                ]
            )

        # row background:
        # dark blue only for dark_blue_rows, otherwise white
        def row_style(row):
            if row.name in dark_blue_rows:
                return [
                    "background-color: #002b55; color: white; "
                    "font-weight: bold; text-align:left;"
                ] * len(row)
            # keep other rows default background; bold handled via index
            return [""] * len(row)

        styler = styler.apply(row_style, axis=1)

        # index (row label) styling:
        # - any section_rows: bold + no indent
        # - others: normal + single indent
        def index_style(idx_series):
            styles = []
            for label in idx_series:
                if label in section_rows:
                    styles.append("padding-left: 4px; font-weight: bold;")
                else:
                    styles.append("padding-left: 20px; font-weight: normal;")
            return styles

        styler = styler.apply_index(index_style, axis=0)

        # color and bold only non-zero numbers
        def color_and_bold_nonzero(val):
            if pd.isna(val) or not isinstance(val, (int, float)):
                return ""
            if val > 0:
                return "color: #008000; font-weight:bold;"
            if val < 0:
                return "color: #CC0000; font-weight:bold;"
            return ""  # zero

        for col in ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg']:
            if col in df.columns:
                styler = styler.applymap(
                    color_and_bold_nonzero, subset=pd.IndexSlice[:, col]
                )

        return styler

    st.subheader("Primary Dealer Warehouse Snapshot ($bn)")
    styled = style_fed_table(df)
    html = styled.to_html()
    st.markdown(html, unsafe_allow_html=True)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------- PRIMARY DEALER HOLDINGS AS % OF TOTAL HEATMAP -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------- PRIMARY DEALER HOLDINGS AS % OF TOTAL HEATMAP -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------- PRIMARY DEALER HOLDINGS AS % OF TOTAL HEATMAP (PER-COLUMN SCALED) ---------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def primary_dealer_holdings_heatmap(start, end, **kwargs):
    base_series = pd_pos_dict["All USTs"]
    all_dates = base_series.index.sort_values()

    # round + zero‑clean, consistent with snapshot fn
    for key, obj in pd_pos_dict.items():
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            pd_pos_dict[key] = obj.round(2)
            pd_pos_dict[key] = pd_pos_dict[key].where(
                pd_pos_dict[key] != 0, 0
            )

    # ------------------------------------------------------------------ #
    # Default window: last date and 21 rows before that
    # ------------------------------------------------------------------ #
    last_idx = len(all_dates) - 1
    start_idx_default = max(0, last_idx - 21)

    col1, col2 = st.columns(2)
    with col1:
        chosen_start_date = st.selectbox(
            "Select Start Snapshot Date",
            options=all_dates,
            index=start_idx_default,
            format_func=lambda d: d.strftime("%Y-%m-%d"),
        )
    with col2:
        chosen_end_date = st.selectbox(
            "Select End Snapshot Date",
            options=all_dates,
            index=last_idx,
            format_func=lambda d: d.strftime("%Y-%m-%d"),
        )

    # slice to chosen window
    start_str = pd.to_datetime(chosen_start_date).strftime("%Y-%m-%d")
    end_str = pd.to_datetime(chosen_end_date).strftime("%Y-%m-%d")

    # ------------------------------------------------------------------ #
    # Build % of total DF (rows = buckets, cols = dates), in percent
    # ------------------------------------------------------------------ #
    all_ust = pd_pos_dict['All USTs'].loc[start_str:end_str]['Level']

    pd_perc_holdings_snapshot = pd.DataFrame({
        'Coupons <2y':    (pd_pos_dict['Coupons <2y'].loc[start_str:end_str]['Level']    / all_ust) * 100,
        'Coupons 2-3y':   (pd_pos_dict['Coupons 2-3y'].loc[start_str:end_str]['Level']   / all_ust) * 100,
        'Coupons 3-6y':   (pd_pos_dict['Coupons 3-6y'].loc[start_str:end_str]['Level']   / all_ust) * 100,
        'Coupons 6-7y':   (pd_pos_dict['Coupons 6-7y'].loc[start_str:end_str]['Level']   / all_ust) * 100,
        'Coupons 7-11y':  (pd_pos_dict['Coupons 7-11y'].loc[start_str:end_str]['Level']  / all_ust) * 100,
        'Coupons 11-21y': (pd_pos_dict['Coupons 11-21y'].loc[start_str:end_str]['Level'] / all_ust) * 100,
        'Coupons >21y':   (pd_pos_dict['Coupons >21y'].loc[start_str:end_str]['Level']   / all_ust) * 100,

        'All TIPS':       (pd_pos_dict['All TIPS'].loc[start_str:end_str]['Level']       / all_ust) * 100,
        'TIPS <2y':       (pd_pos_dict['TIPS <2y'].loc[start_str:end_str]['Level']       / all_ust) * 100,
        'TIPS 2-6y':      (pd_pos_dict['TIPS 2-6y'].loc[start_str:end_str]['Level']      / all_ust) * 100,
        'TIPS 6-11y':     (pd_pos_dict['TIPS 6-11y'].loc[start_str:end_str]['Level']     / all_ust) * 100,
        'TIPS >11y':      (pd_pos_dict['TIPS >11y'].loc[start_str:end_str]['Level']      / all_ust) * 100,

        'All Bills':      (pd_pos_dict['All Bills'].loc[start_str:end_str]['Level']      / all_ust) * 100,
        'All FRNs':       (pd_pos_dict['All FRNs'].loc[start_str:end_str]['Level']       / all_ust) * 100,
    }).T.round(2)

    df_pct = pd_perc_holdings_snapshot.copy()
    df_pct.columns = df_pct.columns.strftime("%m-%d-%y")  # pretty date labels

    # ------------------------------------------------------------------ #
    # Column‑wise normalization for colors (0–1 within each column)
    # ------------------------------------------------------------------ #
    df_norm = df_pct.copy()
    col_min = df_norm.min(axis=0)
    col_max = df_norm.max(axis=0)
    denom = (col_max - col_min).replace(0, 1)  # avoid divide‑by‑zero
    df_norm = (df_norm - col_min) / denom

    # ------------------------------------------------------------------ #
    # Plot heatmap: df_norm for colors, df_pct for annotations
    # ------------------------------------------------------------------ #
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np

    st.subheader("Holdings as % of Total: Heatmap")

    fig, ax = plt.subplots(figsize=(14, 8))

    vmin, vmax = 0, 1  # because df_norm is 0–1 by construction
    cmap = sns.color_palette("RdYlBu_r", as_cmap=True)

    sns.heatmap(
        df_norm,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=df_pct,          # show actual % values
        fmt=".2f",
        annot_kws={"fontsize": 8},
        cbar=False,
        linewidths=0.5,
        linecolor="white",
    )

    ax.set_ylabel("Nominals", fontsize=12)
    ax.set_xlabel("Time", fontsize=12)

    # colorbar on top, showing 0–1 relative to each column's own min/max
    cax = fig.add_axes([0.1, 0.90, 0.8, 0.03])   # [left, bottom, width, height]
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.set_label("Relative level within each date (0 = column min, 1 = column max)", fontsize=11)
    cbar.ax.xaxis.set_ticks_position("top")
    cbar.ax.xaxis.set_label_position("top")

    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.88])

    st.pyplot(fig)


### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- SPONSORED VOLUMES - THE SOLUTION? ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sponsored_volumes_solution(start, end, path_to_csv="data/SponsoredVolume.csv", **kwargs):
    sponsored_volume = pd.read_csv(path_to_csv).dropna()
    sponsored_volume = sponsored_volume.iloc[::-1].reset_index(drop=True)
    sponsored_volume.index = pd.to_datetime(sponsored_volume['BUSINESS_DATE'].values)
    sponsored_volume = sponsored_volume.drop('BUSINESS_DATE', axis=1)
    sponsored_volume['DVP_TOTAL_AMOUNT'] = (
        sponsored_volume['DVP_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
    sponsored_volume['GC_TOTAL_AMOUNT'] = (
        sponsored_volume['GC_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
    sponsored_volume = sponsored_volume.sort_index()
    sponsored_volume = sponsored_volume.loc[str(start):str(end)]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(sponsored_volume.index, sponsored_volume['DVP_TOTAL_AMOUNT'],
    #          label='DVP Sponsored', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(sponsored_volume.index, sponsored_volume['GC_TOTAL_AMOUNT'],
    #          label='GC Sponsored', color='#233852', lw=2)  # dark blue
    # plt.ylabel("Trillions")
    # plt.title("Sponsored Volumes - The Solutions?", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sponsored_volume.index, y=sponsored_volume['DVP_TOTAL_AMOUNT'], name='DVP Sponsored',
                             line=dict(color='#4CD0E9', width=2)))
    fig.add_trace(go.Scatter(x=sponsored_volume.index, y=sponsored_volume['GC_TOTAL_AMOUNT'], name='GC Sponsored',
                             line=dict(color='#233852', width=2)))
    fig.update_layout(
        title="Sponsored Volumes - The Solutions?",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SPONSORED VOLUMES -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_sponsored_volumes(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'ficc_sponsored_repo_volume.pkl', 'rb') as file:
        ficc_sponsored_repo_volume = pickle.load(file)
    with open(Path(DATA_DIR) / 'ficc_sponsored_rrp_volume.pkl', 'rb') as file:
        ficc_sponsored_rrp_volume = pickle.load(file)

    merge = merge_dfs([ficc_sponsored_repo_volume, ficc_sponsored_rrp_volume])
    merge.columns = ['sponsored_repo', 'sponsored_rrp']
    merge = merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(merge.index, merge['sponsored_repo'],
    #          label='Repo Sponsored', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(merge.index, merge['sponsored_rrp'],
    #          label='RRP Sponsored', color='#233852', lw=2)  # dark blue
    # plt.ylabel("Trillions")
    # plt.title("Sponsored Volumes", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['sponsored_repo'], name='Repo Sponsored',
                             line=dict(color='#4CD0E9', width=2)))
    fig.add_trace(go.Scatter(x=merge.index, y=merge['sponsored_rrp'], name='RRP Sponsored',
                             line=dict(color='#233852', width=2)))
    fig.update_layout(
        title="Sponsored Volumes",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- % OF DVP VOLUME THAT IS SPONSORED ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_pct_dvp_sponsored(start, end, path_to_csv="data/SponsoredVolume.csv", **kwargs):
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'rb') as file:
        dvp_volume = pickle.load(file)

    sponsored_volume = pd.read_csv(path_to_csv).dropna()
    sponsored_volume = sponsored_volume.iloc[::-1].reset_index(drop=True)
    sponsored_volume.index = pd.to_datetime(sponsored_volume['BUSINESS_DATE'].values)
    sponsored_volume = sponsored_volume.drop('BUSINESS_DATE', axis=1)
    sponsored_volume['DVP_TOTAL_AMOUNT'] = (
        sponsored_volume['DVP_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
    sponsored_volume = sponsored_volume.sort_index().loc[str(start):str(end)]
    dvp_sponsored_vol = pd.DataFrame(sponsored_volume['DVP_TOTAL_AMOUNT'])

    merge = merge_dfs([dvp_sponsored_vol, dvp_volume]).dropna()
    merge.columns = ['dvp_sponsored', 'total_dvp']
    merge['pct'] = merge['dvp_sponsored'] / merge['total_dvp']
    merge = merge[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(merge.index, merge['pct'],
    #          color='#4CD0E9', lw=2)  # cyan
    # plt.ylabel("%")
    # plt.title("% of DVP that is Sponsored", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merge.index, y=merge['pct'] * 100,
                             name="% of DVP that is Sponsored", line=dict(color='#4CD0E9', width=2)))
    fig.update_layout(
        title="% of DVP that is Sponsored",
        yaxis_title="%",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ PRIMARY DEALERS NET POSITIONS BILLS VS BONDS ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_positions_bills_vs_bonds(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_positions.pkl', 'rb') as file:
        all_pd_bills_bonds_positions = pickle.load(file)
    all_pd_bills_bonds_positions = all_pd_bills_bonds_positions[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(13, 7))
    # plt.plot(all_pd.index, all_pd['bills'],
    #          label='Bills', color='#43c4e6', linewidth=2)
    # plt.plot(all_pd.index, all_pd['net_nominal_bonds'],
    #          label='Net Nominal Bonds', color='#262e39', linewidth=2)
    # plt.title("Primary Dealers Net Positions Bills VS Bonds", fontsize=20, fontweight="bold")
    # plt.ylabel("Billions")
    # plt.xlabel("")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True, which='major', linestyle='-', color='grey', alpha=0.3)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=all_pd_bills_bonds_positions.index,
                             y=all_pd_bills_bonds_positions['bills'], name="Bills",
                             line=dict(color='#43c4e6', width=2)))
    fig.add_trace(go.Scatter(x=all_pd_bills_bonds_positions.index,
                             y=all_pd_bills_bonds_positions['net_nominal_bonds'], name="Net Nominal Bonds",
                             line=dict(color='#262e39', width=2)))
    fig.update_layout(
        title="Primary Dealers Net Positions Bills VS Bonds",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------- PRIMARY DEALERS NET POSITIONS BY BOND TENOR ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_positions_by_bond_tenor(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_positions.pkl', 'rb') as file:
        all_pd_bills_bonds_positions = pickle.load(file)
    all_pd_bills_bonds_positions = all_pd_bills_bonds_positions[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(all_pd.index, all_pd['l2'],
    #          label='Bond <2Y', color='#9DDCF9')
    # plt.plot(all_pd.index, all_pd['g2l3'],
    #          label='Bond 2-3Y', color='#4CD0E9')
    # plt.plot(all_pd.index, all_pd['g3l6'],
    #          label='Bond 3-6Y', color='#233852')
    # plt.plot(all_pd.index, all_pd['g6l7'],
    #          label='Bond 6-7Y', color='#F5B820', linewidth=2)
    # plt.plot(all_pd.index, all_pd['g7l11'],
    #          label='Bond 7-10Y', color='#E69B93')
    # plt.ylabel("Billions")
    # plt.title("Primary Dealers Net Positions By Bond Tenor", fontsize=20, fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    tenors = [
        ('l2', 'Bond <2Y', '#9DDCF9'),
        ('g2l3', 'Bond 2-3Y', '#4CD0E9'),
        ('g3l6', 'Bond 3-6Y', '#233852'),
        ('g6l7', 'Bond 6-7Y', '#F5B820'),
        ('g7l11', 'Bond 7-10Y', '#E69B93'),
    ]
    for k, name, color in tenors:
        fig.add_trace(go.Scatter(x=all_pd_bills_bonds_positions.index,
                                 y=all_pd_bills_bonds_positions[k], name=name, line=dict(color=color, width=2)))
    fig.update_layout(
        title="Primary Dealers Net Positions By Bond Tenor",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------- PRIMARY DEALERS BOND NET POSITION CHANGE -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_net_change_by_bond_tenor(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_net_changes.pkl', 'rb') as file:
        all_pd_bills_bonds_net_changes = pickle.load(file)
    all_pd_bills_bonds_net_changes = all_pd_bills_bonds_net_changes[start:end]

    # ### PLOT ###
    # plt.figure(figsize=(12, 7))
    # plt.plot(all_pd_change.index, all_pd_change['l2'],
    #          label='Bond <2Y', color='#9DDCF9')
    # plt.plot(all_pd_change.index, all_pd_change['g2l3'],
    #          label='Bond 2-3Y', color='#4CD0E9')
    # plt.plot(all_pd_change.index, all_pd_change['g3l6'],
    #          label='Bond 3-6Y', color='#233852')
    # plt.plot(all_pd_change.index, all_pd_change['g6l7'],
    #          label='Bond 6-7Y', color='#F5B820', linewidth=2)
    # plt.plot(all_pd_change.index, all_pd_change['g7l11'],
    #          label='Bond 7-10Y', color='#E69B93')
    # plt.ylabel("Billions")
    # plt.title("Primary Dealers Net Position Change By Bond Tenor", fontsize=20, fontweight='bold')
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

    fig = go.Figure()
    tenors = [
        ('l2', 'Bond <2Y', '#9DDCF9'),
        ('g2l3', 'Bond 2-3Y', '#4CD0E9'),
        ('g3l6', 'Bond 3-6Y', '#233852'),
        ('g6l7', 'Bond 6-7Y', '#F5B820'),
        ('g7l11', 'Bond 7-10Y', '#E69B93'),
    ]
    for k, name, color in tenors:
        fig.add_trace(go.Scatter(x=all_pd_bills_bonds_net_changes.index,
                                 y=all_pd_bills_bonds_net_changes[k], name=name, line=dict(color=color, width=2)))
    fig.update_layout(
        title="Primary Dealers Net Position Change By Bond Tenor",
        yaxis_title="Dollars",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)




