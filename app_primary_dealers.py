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

def primary_dealer_front_end(start, end, **kwargs):
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    def fig_to_base64(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return encoded

    # ------------------------------------------------------------------ #
    # Build front-end positions dataframe
    # ------------------------------------------------------------------ #
    front_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons <2y': pd_pos_dict['Coupons <2y']['Level'],
        'All Bills': pd_pos_dict['All Bills']['Level'],
    })

    # restrict to selected window if you want (optional)
    if start is not None and end is not None:
        front_df = front_df.loc[pd.to_datetime(start):pd.to_datetime(end)]

    # ------------------------------------------------------------------ #
    # FIRST CHART: levels (dollars)
    # ------------------------------------------------------------------ #
    fig1, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(
        front_df.index,
        front_df['Coupons <2y'] * 1e9,
        color=pd_colors_dict['Coupons <2y'],
        label='Coupons <2y',
    )
    ax1.plot(
        front_df.index,
        front_df['All Bills'] * 1e9,
        color=pd_colors_dict['All Bills'],
        label='All Bills',
    )
    ax1.set_title("US Primary Dealer Holdings (Net Position) | Front-End", fontsize=14)
    ax1.set_ylabel("Notional", fontsize=12)
    ax1.set_xlabel("Date", fontsize=12)
    ax1.legend(loc="best", fontsize=9)
    ax1.grid(True, linewidth=0.3, alpha=0.4)
    fig1.autofmt_xdate()
    img1_b64 = fig_to_base64(fig1)

    # ------------------------------------------------------------------ #
    # SECOND CHART: 3yr Z-scores
    # ------------------------------------------------------------------ #
    z_df = front_df.copy()
    z_df['Coupons <2y z'] = (
        (z_df['Coupons <2y'] - z_df['Coupons <2y'].rolling(156).mean())
        / z_df['Coupons <2y'].rolling(156).std()
    )
    z_df['All Bills z'] = (
        (z_df['All Bills'] - z_df['All Bills'].rolling(156).mean())
        / z_df['All Bills'].rolling(156).std()
    )
    z_df = z_df.dropna(subset=['Coupons <2y z', 'All Bills z'])

    fig2, ax2 = plt.subplots(figsize=(14, 6))
    ax2.plot(
        z_df.index,
        z_df['Coupons <2y z'],
        color=pd_colors_dict['Coupons <2y'],
        label='Coupons <2y',
    )
    ax2.plot(
        z_df.index,
        z_df['All Bills z'],
        color=pd_colors_dict['All Bills'],
        label='All Bills',
    )
    ax2.axhline(0, color="black", linewidth=0.5)
    ax2.set_title("US Primary Dealer Holdings (Net Positions 3yr Z-Score) | Front-End", fontsize=14)
    ax2.set_ylabel("Z-score", fontsize=12)
    ax2.set_xlabel("Date", fontsize=12)
    ax2.legend(loc="best", fontsize=9)
    ax2.grid(True, linewidth=0.3, alpha=0.4)
    fig2.autofmt_xdate()
    img2_b64 = fig_to_base64(fig2)

    # ------------------------------------------------------------------ #
    # THIRD CHART: % of All Coupons
    # ------------------------------------------------------------------ #
    pct_df = front_df.copy()
    pct_df['Coupons <2y %'] = (pct_df['Coupons <2y'] / pct_df['All Coupons']) * 100
    pct_df['All Bills %'] = (pct_df['All Bills'] / pct_df['All Coupons']) * 100
    pct_df = pct_df.dropna(subset=['Coupons <2y %', 'All Bills %'])

    fig3, ax3 = plt.subplots(figsize=(14, 6))
    ax3.plot(
        pct_df.index,
        pct_df['Coupons <2y %'],
        color=pd_colors_dict['Coupons <2y'],
        label='Coupons <2y',
    )
    ax3.plot(
        pct_df.index,
        pct_df['All Bills %'],
        color=pd_colors_dict['All Bills'],
        label='All Bills',
    )
    ax3.set_title("US Primary Dealer Holdings (% of Net Positions) | Front-End", fontsize=14)
    ax3.set_ylabel("% of All Coupons", fontsize=12)
    ax3.set_xlabel("Date", fontsize=12)
    ax3.legend(loc="best", fontsize=9)
    ax3.grid(True, linewidth=0.3, alpha=0.4)
    fig3.autofmt_xdate()
    img3_b64 = fig_to_base64(fig3)

    # ------------------------------------------------------------------ #
    # Show all three charts in a horizontally scrollable row
    # ------------------------------------------------------------------ #
    html = f"""
    <div style="width: 100%; overflow-x: auto;">
        <div style="display: flex; flex-wrap: nowrap;">
            <img src="data:image/png;base64,{img1_b64}" style="margin-right: 24px;" />
            <img src="data:image/png;base64,{img2_b64}" style="margin-right: 24px;" />
            <img src="data:image/png;base64,{img3_b64}" />
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

def primary_dealer_front_end(start,end,**kwargs):
    front_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons <2y': pd_pos_dict['Coupons <2y']['Level'],
        'All Bills': pd_pos_dict['All Bills']['Level'],
    })
    streamlit_plot(
        front_df.dropna()*1e9,
        ['Coupons <2y', 'All Bills'],
        [pd_colors_dict['Coupons <2y'], pd_colors_dict['All Bills']],
        [
            'Coupons <2y',
            'All Bills'],
        "US Primary Dealer Holdings (Net Position) | Front-End",
        ""
    )
    front_df['Coupons <2y z'] = ((front_df['Coupons <2y'] -
                                 front_df['Coupons <2y'].rolling(156).mean()) /
                                 front_df['Coupons <2y'].rolling(156).std())
    front_df['All Bills z'] = ((front_df['All Bills'] -
                                 front_df['All Bills'].rolling(156).mean()) /
                                 front_df['All Bills'].rolling(156).std())
    streamlit_plot(
        front_df.dropna(),
        ['Coupons <2y z', 'All Bills z'],
        [pd_colors_dict['Coupons <2y'], pd_colors_dict['All Bills']],
        [
            'Coupons <2y',
            'All Bills'],
        "US Primary Dealer Holdings (Net Positions 3yr Z-Score) | Front-End",
        ""
    )
    front_df['Coupons <2y %'] = (front_df['Coupons <2y'] / front_df['All Coupons']) * 100
    front_df['All Bills %'] = (front_df['All Bills'] / front_df['All Coupons']) * 100
    streamlit_plot(
        front_df.dropna(),
        ['Coupons <2y %', 'All Bills %'],
        [pd_colors_dict['Coupons <2y'], pd_colors_dict['All Bills']],
        [
            'Coupons <2y',
            'All Bills'],
        "US Primary Dealer Holdings (% of Net Positions) | Front-End",
        ""
    )



def primary_dealer_belly(start,end,**kwargs):
    belly_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons 2-3y': pd_pos_dict['Coupons 2-3y']['Level'],
        'Coupons 3-6y': pd_pos_dict['Coupons 3-6y']['Level'],
        'Coupons 6-7y': pd_pos_dict['Coupons 6-7y']['Level'],
    })
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

def primary_dealer_back_end(start,end,**kwargs):
    back_df = pd.DataFrame({
        'All Coupons': pd_pos_dict['All Coupons']['Level'],
        'Coupons 7-11y': pd_pos_dict['Coupons 7-11y']['Level'],
        'Coupons 11-21y': pd_pos_dict['Coupons 11-21y']['Level'],
        'Coupons >21y': pd_pos_dict['Coupons >21y']['Level'],
    })
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


