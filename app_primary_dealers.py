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

### COLOR ARRAY ###
pd_colors_dict = {
    'Coupons <2y':    '#1f77b4',  # deep blue
    'Coupons 2-3y':   '#2ca02c',  # green
    'Coupons 3-6y':   '#17becf',  # teal
    'Coupons 6-7y':   '#ff7f0e',  # orange
    'Coupons 7-11y':  '#1f77b4',  # deep blue (longer tenors)
    'Coupons 11-21y': '#d62728',  # red
    'Coupons >21y':   '#9467bd',  # purple

    'All TIPS':       '#8c564b',  # brown
    'TIPS <2y':       '#bcbd22',  # olive
    'TIPS 2-6y':      '#17becf',  # teal
    'TIPS 6-11y':     '#e377c2',  # pink
    'TIPS >11y':      '#7f7f7f',  # gray

    'All Bills':      '#aec7e8',  # light blue
    'All FRNs':       '#98df8a',  # light green
}

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- PRIMARY DEALER WAREHOUSE OVERVIEW ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def primary_dealer_snapshot(start, end, **kwargs):
    st.subheader("Primary Dealer Warehouse Snapshot ($bn)")
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

    def style_fed_table(df: pd.DataFrame):
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
                        ("width", "100%"),  # fill available width
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
                        ("padding", "6px 4px"),
                    ],
                },
                {
                    "selector": "th.row_heading",
                    "props": [
                        ("text-align", "left"),
                        ("border", "1px solid #CCCCCC"),
                        ("white-space", "nowrap"),
                        ("width", "220px"),
                        ("max-width", "220px"),
                        ("padding", "4px 6px"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("border", "1px solid #CCCCCC"),
                        ("text-align", "center"),
                        ("padding", "4px 6px"),
                    ],
                },
            ]
        )

        numeric_cols = ['Level', 'YTD chg', '1w chg', '4w chg', '6m chg', '12m chg', '5y min', '5y max', '5y avg']
        existing_cols = [c for c in numeric_cols if c in df.columns]

        if existing_cols:
            # equal width for all numeric columns so table fills page
            per_col =  (100 - 18) / len(existing_cols)  # ~18% left for index column
            col_width_css = f"width: {per_col:.2f}%; max-width: {per_col:.2f}%;"

            # apply width to header + data cells of numeric columns
            styler = styler.set_properties(
                subset=pd.IndexSlice[:, existing_cols],
                **{"text-align": "center", "width": f"{per_col:.2f}%", "max-width": f"{per_col:.2f}%"},
            )

            styler = styler.set_table_styles(
                styler.table_styles
                + [
                    {
                        "selector": f'th.col_heading.level{level}',
                        "props": [( "width", f"{per_col:.2f}%" ), ("max-width", f"{per_col:.2f}%")],
                    }
                    for level in range(len(existing_cols))
                ]
            )

        # row background:
        def row_style(row):
            if row.name in dark_blue_rows:
                return [
                    "background-color: #002b55; color: white; "
                    "font-weight: bold; text-align:left;"
                ] * len(row)
            return [""] * len(row)

        styler = styler.apply(row_style, axis=1)

        # index styling
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
            return ""

        for col in numeric_cols:
            if col in df.columns:
                styler = styler.applymap(
                    color_and_bold_nonzero, subset=pd.IndexSlice[:, col]
                )

        return styler

    styled = style_fed_table(df)
    html = styled.to_html()
    st.markdown(html, unsafe_allow_html=True)


### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------- PRIMARY DEALER HOLDINGS AS % OF TOTAL HEATMAP -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def primary_dealer_nominal_holdings_heatmap(start, end, **kwargs):
    def fig_to_base64(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return encoded
    st.subheader("Primary Dealer Holdings Heatmaps")
    base_series = pd_pos_dict["All USTs"]
    all_dates = base_series.index.sort_values()
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
    col_dates_1, col_dates_2 = st.columns(2)
    with col_dates_1:
        chosen_start_date = st.selectbox(
            "Select Start Snapshot Date",
            options=all_dates,
            index=start_idx_default,
            format_func=lambda d: d.strftime("%Y-%m-%d"),
        )
    with col_dates_2:
        chosen_end_date = st.selectbox(
            "Select End Snapshot Date",
            options=all_dates,
            index=last_idx,
            format_func=lambda d: d.strftime("%Y-%m-%d"),
        )
    start_str = pd.to_datetime(chosen_start_date).strftime("%Y-%m-%d")
    end_str = pd.to_datetime(chosen_end_date).strftime("%Y-%m-%d")

    ### ---------------------------------- FIRST HEATMAP ---------------------------------- ###

    all_ust = pd_pos_dict['All USTs'].loc[start_str:end_str]['Level']
    pd_perc_total = pd.DataFrame({
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
    df_pct_total = pd_perc_total.copy()
    df_pct_total.columns = df_pct_total.columns.strftime("%m-%d-%y")
    df_norm_total = df_pct_total.copy()
    col_min = df_norm_total.min(axis=0)
    col_max = df_norm_total.max(axis=0)
    denom = (col_max - col_min).replace(0, 1)
    df_norm_total = (df_norm_total - col_min) / denom

    ### ---------------------------------- SECOND HEATMAP ---------------------------------- ###

    all_coupons = pd_pos_dict['All Coupons'].loc[start_str:end_str]['Level']
    pd_perc_cpn = pd.DataFrame({
        'Coupons <2y':    (pd_pos_dict['Coupons <2y'].loc[start_str:end_str]['Level']    / all_coupons) * 100,
        'Coupons 2-3y':   (pd_pos_dict['Coupons 2-3y'].loc[start_str:end_str]['Level']   / all_coupons) * 100,
        'Coupons 3-6y':   (pd_pos_dict['Coupons 3-6y'].loc[start_str:end_str]['Level']   / all_coupons) * 100,
        'Coupons 6-7y':   (pd_pos_dict['Coupons 6-7y'].loc[start_str:end_str]['Level']   / all_coupons) * 100,
        'Coupons 7-11y':  (pd_pos_dict['Coupons 7-11y'].loc[start_str:end_str]['Level']  / all_coupons) * 100,
        'Coupons 11-21y': (pd_pos_dict['Coupons 11-21y'].loc[start_str:end_str]['Level'] / all_coupons) * 100,
        'Coupons >21y':   (pd_pos_dict['Coupons >21y'].loc[start_str:end_str]['Level']   / all_coupons) * 100,
    }).T.round(2)
    df_pct_cpn = pd_perc_cpn.copy()
    df_pct_cpn.columns = df_pct_cpn.columns.strftime("%m-%d-%y")
    df_norm_cpn = df_pct_cpn.copy()
    col_min = df_norm_cpn.min(axis=0)
    col_max = df_norm_cpn.max(axis=0)
    denom = (col_max - col_min).replace(0, 1)
    df_norm_cpn = (df_norm_cpn - col_min) / denom

    ### ---------------------------------- THIRD HEATMAP ---------------------------------- ###
    pd_pos_levels_z_dict = {}
    pd_pos_12m_chg_z_dict = {}
    for key in pd_pos_dict.keys():
        if type(pd_pos_dict[key]) == pd.core.frame.DataFrame:
            levels_df = pd.DataFrame(pd_pos_dict[key]['Level'])
            levels_df_mean = levels_df.rolling(156).mean()
            levels_df_std = levels_df.rolling(156).std()
            levels_df_z = (levels_df - levels_df_mean) / levels_df_std
            pd_pos_levels_z_dict[key] = levels_df_z.dropna()
            chg_12m_df = pd.DataFrame(pd_pos_dict[key]['12m chg'])
            chg_12m_df_mean = chg_12m_df.rolling(156).mean()
            chg_12m_df_std = chg_12m_df.rolling(156).std()
            chg_12m_df_z = (chg_12m_df - chg_12m_df_mean) / chg_12m_df_std
            pd_pos_12m_chg_z_dict[key] = chg_12m_df_z.dropna()

    pd_holdings_levels_z = pd.DataFrame({
        'All Coupons': (pd_pos_levels_z_dict['All Coupons'].loc[start_str:end_str])['Level'],
        'Coupons <2y': (pd_pos_levels_z_dict['Coupons <2y'].loc[start_str:end_str])['Level'],
        'Coupons 2-3y': (pd_pos_levels_z_dict['Coupons 2-3y'].loc[start_str:end_str])['Level'],
        'Coupons 3-6y': (pd_pos_levels_z_dict['Coupons 3-6y'].loc[start_str:end_str])['Level'],
        'Coupons 6-7y': (pd_pos_levels_z_dict['Coupons 6-7y'].loc[start_str:end_str])['Level'],
        'Coupons 7-11y': (pd_pos_levels_z_dict['Coupons 7-11y'].loc[start_str:end_str])['Level'],
        'Coupons 11-21y': (pd_pos_levels_z_dict['Coupons 11-21y'].loc[start_str:end_str])['Level'],
        'Coupons >21y': (pd_pos_levels_z_dict['Coupons >21y'].loc[start_str:end_str])['Level'],

        'All TIPS': (pd_pos_levels_z_dict['All TIPS'].loc[start_str:end_str])['Level'],
        'TIPS <2y': (pd_pos_levels_z_dict['TIPS <2y'].loc[start_str:end_str])['Level'],
        'TIPS 2-6y': (pd_pos_levels_z_dict['TIPS 2-6y'].loc[start_str:end_str])['Level'],
        'TIPS 6-11y': (pd_pos_levels_z_dict['TIPS 6-11y'].loc[start_str:end_str])['Level'],
        'TIPS >11y': (pd_pos_levels_z_dict['TIPS >11y'].loc[start_str:end_str])['Level'],

        'All Bills': (pd_pos_levels_z_dict['All Bills'].loc[start_str:end_str])['Level'],
        'All FRNs': (pd_pos_levels_z_dict['All FRNs'].loc[start_str:end_str])['Level'],
    }).T.round(2)
    df_levels_z = pd_holdings_levels_z.copy()
    df_levels_z.columns = df_levels_z.columns.strftime("%m-%d-%y")
    df_norm_levels_z = df_levels_z.copy()
    col_min = df_norm_levels_z.min(axis=0)
    col_max = df_norm_levels_z.max(axis=0)
    denom = (col_max - col_min).replace(0, 1)
    df_norm_levels_z = (df_norm_levels_z - col_min) / denom

    ### ---------------------------------- FOURTH HEATMAP ---------------------------------- ###
    pd_holdings_chg_z = pd.DataFrame({
        'All Coupons': (pd_pos_12m_chg_z_dict['All Coupons'].loc[start_str:end_str])['12m chg'],
        'Coupons <2y': (pd_pos_12m_chg_z_dict['Coupons <2y'].loc[start_str:end_str])['12m chg'],
        'Coupons 2-3y': (pd_pos_12m_chg_z_dict['Coupons 2-3y'].loc[start_str:end_str])['12m chg'],
        'Coupons 3-6y': (pd_pos_12m_chg_z_dict['Coupons 3-6y'].loc[start_str:end_str])['12m chg'],
        'Coupons 6-7y': (pd_pos_12m_chg_z_dict['Coupons 6-7y'].loc[start_str:end_str])['12m chg'],
        'Coupons 7-11y': (pd_pos_12m_chg_z_dict['Coupons 7-11y'].loc[start_str:end_str])['12m chg'],
        'Coupons 11-21y': (pd_pos_12m_chg_z_dict['Coupons 11-21y'].loc[start_str:end_str])['12m chg'],
        'Coupons >21y': (pd_pos_12m_chg_z_dict['Coupons >21y'].loc[start_str:end_str])['12m chg'],

        'All TIPS': (pd_pos_12m_chg_z_dict['All TIPS'].loc[start_str:end_str])['12m chg'],
        'TIPS <2y': (pd_pos_12m_chg_z_dict['TIPS <2y'].loc[start_str:end_str])['12m chg'],
        'TIPS 2-6y': (pd_pos_12m_chg_z_dict['TIPS 2-6y'].loc[start_str:end_str])['12m chg'],
        'TIPS 6-11y': (pd_pos_12m_chg_z_dict['TIPS 6-11y'].loc[start_str:end_str])['12m chg'],
        'TIPS >11y': (pd_pos_12m_chg_z_dict['TIPS >11y'].loc[start_str:end_str])['12m chg'],

        'All Bills': (pd_pos_12m_chg_z_dict['All Bills'].loc[start_str:end_str])['12m chg'],
        'All FRNs': (pd_pos_12m_chg_z_dict['All FRNs'].loc[start_str:end_str])['12m chg'],
    }).T.round(2)
    df_chg_z = pd_holdings_chg_z.copy()
    df_chg_z.columns = df_chg_z.columns.strftime("%m-%d-%y")
    df_norm_chg_z = df_chg_z.copy()
    col_min = df_norm_chg_z.min(axis=0)
    col_max = df_norm_chg_z.max(axis=0)
    denom = (col_max - col_min).replace(0, 1)
    df_norm_chg_z = (df_norm_chg_z - col_min) / denom

    ### ---------------------------------- ALL HEATMAPS ---------------------------------- ###
    plt.rcParams["figure.dpi"] = 200
    vmin, vmax = 0, 1
    cmap = sns.color_palette("RdYlBu_r", as_cmap=True)

    ### FIRST ###
    fig1, ax1 = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        df_norm_total,
        ax=ax1,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=df_pct_total,
        fmt=".2f",
        annot_kws={"fontsize": 8},
        cbar=True,
        cbar_kws={
            "orientation": "horizontal",
            "pad": 0.23,          # more space above plot
            "fraction": 0.04,
            "aspect": 40,
        },
        linewidths=0.5,
        linecolor="white",
    )
    ax1.set_title("Holdings as % of Total USTs", fontsize=14, pad=30)
    cbar1 = ax1.collections[0].colorbar
    cbar1.set_label("Relative level (per column)", fontsize=11)
    cbar1.ax.xaxis.set_ticks_position("top")
    cbar1.ax.xaxis.set_label_position("top")
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])  # leave extra room at top
    img1_b64 = fig_to_base64(fig1)

    ### SECOND ###
    fig2, ax2 = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        df_norm_cpn,
        ax=ax2,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=df_pct_cpn,
        fmt=".2f",
        annot_kws={"fontsize": 8},
        cbar=True,
        cbar_kws={
            "orientation": "horizontal",
            "pad": 0.23,
            "fraction": 0.04,
            "aspect": 40,
        },
        linewidths=0.5,
        linecolor="white",
    )
    ax2.set_title("Holdings as % of All Coupons", fontsize=14, pad=30)
    cbar2 = ax2.collections[0].colorbar
    cbar2.set_label("Relative level (per column)", fontsize=11)
    cbar2.ax.xaxis.set_ticks_position("top")
    cbar2.ax.xaxis.set_label_position("top")
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
    img2_b64 = fig_to_base64(fig2)

    ### THIRD ###
    fig3, ax3 = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        df_norm_levels_z,
        ax=ax3,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=df_levels_z,
        fmt=".2f",
        annot_kws={"fontsize": 8},
        cbar=True,
        cbar_kws={
            "orientation": "horizontal",
            "pad": 0.23,
            "fraction": 0.04,
            "aspect": 40,
        },
        linewidths=0.5,
        linecolor="white",
    )
    ax3.set_title("Holdings Levels as Z-Scores", fontsize=14, pad=30)
    cbar3 = ax3.collections[0].colorbar
    cbar3.set_label("Relative level (per column)", fontsize=11)
    cbar3.ax.xaxis.set_ticks_position("top")
    cbar3.ax.xaxis.set_label_position("top")
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
    img3_b64 = fig_to_base64(fig3)

    ### FOURTH ###
    fig4, ax4 = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        df_norm_chg_z,
        ax=ax4,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=df_chg_z,
        fmt=".2f",
        annot_kws={"fontsize": 8},
        cbar=True,
        cbar_kws={
            "orientation": "horizontal",
            "pad": 0.23,
            "fraction": 0.04,
            "aspect": 40,
        },
        linewidths=0.5,
        linecolor="white",
    )
    ax4.set_title("Holdings 12m Change as Z-Scores", fontsize=14, pad=30)
    cbar4 = ax3.collections[0].colorbar
    cbar4.set_label("Relative level (per column)", fontsize=11)
    cbar4.ax.xaxis.set_ticks_position("top")
    cbar4.ax.xaxis.set_label_position("top")
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
    img4_b64 = fig_to_base64(fig4)

    ### SHOW ALL IMAGES NOW ###
    html = f"""
    <div style="width: 100%; overflow-x: auto;">
        <div style="display: flex; flex-wrap: nowrap;">
            <img src="data:image/png;base64,{img1_b64}" style="margin-right: 24px;" />
            <img src="data:image/png;base64,{img2_b64}" style="margin-right: 24px;" />
            <img src="data:image/png;base64,{img3_b64}" style="margin-right: 24px;" />
            <img src="data:image/png;base64,{img4_b64}" />
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

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
    st.plotly_chart(fig)

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
    st.plotly_chart(fig)

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
    st.plotly_chart(fig)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------- PRIMARY DEALERS BOND FRONT END CURVE ---------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def primary_dealer_bonds_curve(start,end,**kwargs):
    front_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons <2y': pd_pos_dict['Coupons <2y']['Level'],
        'All Bills': pd_pos_dict['All Bills']['Level'],
    })
    belly_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons 2-3y': pd_pos_dict['Coupons 2-3y']['Level'],
        'Coupons 3-6y': pd_pos_dict['Coupons 3-6y']['Level'],
        'Coupons 6-7y': pd_pos_dict['Coupons 6-7y']['Level'],
    })
    back_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons 7-11y': pd_pos_dict['Coupons 7-11y']['Level'],
        'Coupons 11-21y': pd_pos_dict['Coupons 11-21y']['Level'],
        'Coupons >21y': pd_pos_dict['Coupons >21y']['Level'],
    })

    streamlit_plot(
        front_df*1e9,
        ['Coupons <2y', 'All Bills'],
        [pd_colors_dict['Coupons <2y'], pd_colors_dict['All Bills']],
        [
            'Coupons <2y',
            'All Bills'],
        "US Primary Dealer Holdings (Net Position) | Front-End",
        ""
    )
    streamlit_plot(
        belly_df*1e9,
        ['Coupons 2-3y', 'Coupons 3-6y','Coupons 6-7y'],
        [
            pd_colors_dict['Coupons 2-3y'],
            pd_colors_dict['Coupons 3-6y'],
            pd_colors_dict['Coupons 6-7y']],
        ['Coupons 2-3y', 'Coupons 3-6y','Coupons 6-7y'],
        "US Primary Dealer Holdings (Net Position) | Belly",
        ""
    )
    streamlit_plot(
        back_df * 1e9,
        ['Coupons 7-11y', 'Coupons 11-21y','Coupons >21y'],
        [
            pd_colors_dict['Coupons 7-11y'],
            pd_colors_dict['Coupons 11-21y'],
            pd_colors_dict['Coupons >21y']],
        ['Coupons 7-11y', 'Coupons 11-21y','Coupons >21y'],
        "US Primary Dealer Holdings (Net Position) | Back-End",
        ""
    )


