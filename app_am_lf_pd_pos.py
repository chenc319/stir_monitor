### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- REAL MONEY VS FAST MONEY ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### FUNCTIONS ###
from Functions import *
from pathlib import Path
import os
DATA_DIR = os.getenv('DATA_DIR', 'data')

### LOAD DATA ###
with open(Path(DATA_DIR) / 'cftc_bond_futures_dict.pkl', 'rb') as file:
    cftc_bond_futures_dict = pickle.load(file)

### COLOR ARRAY ###
cftc_colors_dict = {
    'TU':    '#1f77b4',  # deep blue
    'FV':   '#2ca02c',  # green
    'TY':   '#ff7f0e',  # orange
    'UXY': '#d62728',  # red
    'US':   '#9467bd',  # purple
    'WN':      '#7f7f7f',  # gray
}
cftc_colors_shades = {
    'TU': [
        '#1f77b4',  # base deep blue
        '#4c97c8',  # lighter blue
        '#155289',  # darker blue
    ],
    'FV': [
        '#2ca02c',  # base green
        '#5bbf5b',  # lighter green
        '#1d701d',  # darker green
    ],
    'TY': [
        '#ff7f0e',  # base orange
        '#ffab5a',  # lighter orange
        '#c75b00',  # darker orange
    ],
    'UXY': [
        '#d62728',  # base red
        '#e45b5c',  # lighter red
        '#9b1c1d',  # darker red
    ],
    'US': [
        '#9467bd',  # base purple
        '#b18dd1',  # lighter purple
        '#6c4b8c',  # darker purple
    ],
    'WN': [
        '#7f7f7f',  # base gray
        '#b0b0b0',  # lighter gray
        '#4f4f4f',  # darker gray
    ],
}

### PRE CALCULATIONS ###
real_fast_money_pos_dict = {}
for each_bond_key in cftc_bond_futures_dict.keys():
    df = cftc_bond_futures_dict[each_bond_key]
    df['AM Net Positions'] = (df['Asset_Mgr_Positions_Long_All'] -
                              df['Asset_Mgr_Positions_Short_All'])
    df['LF Net Positions'] = (df['Lev_Money_Positions_Long_All'] -
                             df['Lev_Money_Positions_Short_All'])
    df['AM 1w Pos Chg'] = df['AM Net Positions'].diff(1)
    df['AM 4w Pos Chg'] = df['AM Net Positions'].diff(4)
    df['AM 6m Pos Chg'] = df['AM Net Positions'].diff(26)
    df['AM 12m Pos Chg'] = df['AM Net Positions'].diff(52)
    df['AM OI %'] = (df['AM Net Positions'] / df['Open_Interest_All']) * 100
    df['AM 1w OI Chg'] = df['AM OI %'].diff(1)
    df['AM 4w OI Chg'] = df['AM OI %'].diff(4)
    df['AM 6m OI Chg'] = df['AM OI %'].diff(26)
    df['AM 12m OI Chg'] = df['AM OI %'].diff(52)

    df['LF 1w Pos Chg'] = df['LF Net Positions'].diff(1)
    df['LF 4w Pos Chg'] = df['LF Net Positions'].diff(4)
    df['LF 6m Pos Chg'] = df['LF Net Positions'].diff(26)
    df['LF 12m Pos Chg'] = df['LF Net Positions'].diff(52)
    df['LF OI %'] = (df['LF Net Positions'] / df['Open_Interest_All']) * 100
    df['LF 1w OI Chg'] = df['LF OI %'].diff(1)
    df['LF 4w OI Chg'] = df['LF OI %'].diff(4)
    df['LF 6m OI Chg'] = df['LF OI %'].diff(26)
    df['LF 12m OI Chg'] = df['LF OI %'].diff(52)

    real_fast_money_pos_dict[each_bond_key] = pd.DataFrame(df[[
        'AM Net Positions',
        'AM 1w Pos Chg',
        'AM 4w Pos Chg',
        'AM 6m Pos Chg',
        'AM 12m Pos Chg',
        'AM OI %',
        'AM 1w OI Chg',
        'AM 4w OI Chg',
        'AM 6m OI Chg',
        'AM 12m OI Chg',
        'LF Net Positions',
        'LF 1w Pos Chg',
        'LF 4w Pos Chg',
        'LF 6m Pos Chg',
        'LF 12m Pos Chg',
        'LF OI %',
        'LF 1w OI Chg',
        'LF 4w OI Chg',
        'LF 6m OI Chg',
        'LF 12m OI Chg',
    ]])

am_net_positions = pd.DataFrame({
    key: df["AM Net Positions"]
    for key, df in cftc_bond_futures_dict.items()
})
am_pos_oi = pd.DataFrame({
    key: df["AM OI %"]
    for key, df in cftc_bond_futures_dict.items()
})
lf_net_positions = pd.DataFrame({
    key: df["LF Net Positions"]
    for key, df in cftc_bond_futures_dict.items()
})
lf_pos_oi = pd.DataFrame({
    key: df["LF OI %"]
    for key, df in cftc_bond_futures_dict.items()
})

real_fast_money_dict = {}
for bond_fut_str in ['TU','FV','TY','UXY','US','WN']:
    real_fast_fut_data = real_fast_money_pos_dict[bond_fut_str][[
        'AM Net Positions','AM OI %','LF Net Positions', 'LF OI %',
    ]]

    real_fast_fut_data['AM 4w Pos MA'] = real_fast_fut_data['AM Net Positions'].rolling(4).mean()
    real_fast_fut_data['LF 4w Pos MA'] = real_fast_fut_data['LF Net Positions'].rolling(4).mean()
    real_fast_fut_data['AM 6m Pos MA'] = real_fast_fut_data['AM Net Positions'].rolling(26).mean()
    real_fast_fut_data['LF 6m Pos MA'] = real_fast_fut_data['LF Net Positions'].rolling(26).mean()

    real_fast_fut_data['AM 4w OI MA'] = real_fast_fut_data['AM OI %'].rolling(4).mean()
    real_fast_fut_data['LF 4w OI MA'] = real_fast_fut_data['LF OI %'].rolling(4).mean()
    real_fast_fut_data['AM 6m OI MA'] = real_fast_fut_data['AM OI %'].rolling(26).mean()
    real_fast_fut_data['LF 6m OI MA'] = real_fast_fut_data['LF OI %'].rolling(26).mean()

    real_fast_fut_data['AM Net Positions Z'] = (
            (real_fast_fut_data['AM Net Positions'] -
             real_fast_fut_data['AM Net Positions'].rolling(52).mean()) /
            real_fast_fut_data['AM Net Positions'].rolling(52).std()
    )
    real_fast_fut_data['LF Net Positions Z'] = (
            (real_fast_fut_data['LF Net Positions'] -
             real_fast_fut_data['LF Net Positions'].rolling(52).mean()) /
            real_fast_fut_data['LF Net Positions'].rolling(52).std()
    )
    real_fast_fut_data['AM OI % Z'] = (
            (real_fast_fut_data['AM OI %'] -
             real_fast_fut_data['AM OI %'].rolling(52).mean()) /
            real_fast_fut_data['AM OI %'].rolling(52).std()
    )
    real_fast_fut_data['LF OI % Z'] = (
            (real_fast_fut_data['LF OI %'] -
             real_fast_fut_data['LF OI %'].rolling(52).mean()) /
            real_fast_fut_data['LF OI %'].rolling(52).std()
    )
    real_fast_money_dict[bond_fut_str] = real_fast_fut_data

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- REAL MONEY VS FAST MONEY ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def am_lf_snapshot(start, end, **kwargs):
    st.subheader("CFTC Positioning Snapshot")
    base_series = real_fast_money_pos_dict["TU"]
    all_dates = base_series.index.sort_values()

    for key, obj in real_fast_money_pos_dict.items():
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            real_fast_money_pos_dict[key] = obj.round(1)
            real_fast_money_pos_dict[key] = real_fast_money_pos_dict[key].where(
                real_fast_money_pos_dict[key] != 0, 0
            )

    chosen_date = st.selectbox(
        "Select CFTC Snapshot Date",
        options=all_dates,
        index=len(all_dates) - 1,
        format_func=lambda d: d.strftime("%Y-%m-%d"),
    )

    cftc_am_of_snapshot = pd.DataFrame({
        'TU': ['','','','','','','','','',''],
        'TU Real Money': real_fast_money_pos_dict['TU'].loc[chosen_date][[
            'AM Net Positions','AM 1w Pos Chg','AM 4w Pos Chg','AM 6m Pos Chg','AM 12m Pos Chg',
            'AM OI %','AM 1w OI Chg','AM 4w OI Chg','AM 6m OI Chg','AM 12m OI Chg']].tolist(),
        'TU Fast Money': real_fast_money_pos_dict['TU'].loc[chosen_date][[
            'LF Net Positions','LF 1w Pos Chg','LF 4w Pos Chg','LF 6m Pos Chg','LF 12m Pos Chg',
            'LF OI %','LF 1w OI Chg','LF 4w OI Chg','LF 6m OI Chg','LF 12m OI Chg']].tolist(),

        'FV': ['','','','','','','','','',''],
        'FV Real Money': real_fast_money_pos_dict['FV'].loc[chosen_date][[
            'AM Net Positions','AM 1w Pos Chg','AM 4w Pos Chg','AM 6m Pos Chg','AM 12m Pos Chg',
            'AM OI %','AM 1w OI Chg','AM 4w OI Chg','AM 6m OI Chg','AM 12m OI Chg']].tolist(),
        'FV Fast Money': real_fast_money_pos_dict['FV'].loc[chosen_date][[
            'LF Net Positions','LF 1w Pos Chg','LF 4w Pos Chg','LF 6m Pos Chg','LF 12m Pos Chg',
            'LF OI %','LF 1w OI Chg','LF 4w OI Chg','LF 6m OI Chg','LF 12m OI Chg']].tolist(),

        'TY': ['','','','','','','','','',''],
        'TY Real Money': real_fast_money_pos_dict['TY'].loc[chosen_date][[
            'AM Net Positions','AM 1w Pos Chg','AM 4w Pos Chg','AM 6m Pos Chg','AM 12m Pos Chg',
            'AM OI %','AM 1w OI Chg','AM 4w OI Chg','AM 6m OI Chg','AM 12m OI Chg']].tolist(),
        'TY Fast Money': real_fast_money_pos_dict['TY'].loc[chosen_date][[
            'LF Net Positions','LF 1w Pos Chg','LF 4w Pos Chg','LF 6m Pos Chg','LF 12m Pos Chg',
            'LF OI %','LF 1w OI Chg','LF 4w OI Chg','LF 6m OI Chg','LF 12m OI Chg']].tolist(),

        'UXY': ['','','','','','','','','',''],
        'UXY Real Money': real_fast_money_pos_dict['UXY'].loc[chosen_date][[
            'AM Net Positions','AM 1w Pos Chg','AM 4w Pos Chg','AM 6m Pos Chg','AM 12m Pos Chg',
            'AM OI %','AM 1w OI Chg','AM 4w OI Chg','AM 6m OI Chg','AM 12m OI Chg']].tolist(),
        'UXY Fast Money': real_fast_money_pos_dict['UXY'].loc[chosen_date][[
            'LF Net Positions','LF 1w Pos Chg','LF 4w Pos Chg','LF 6m Pos Chg','LF 12m Pos Chg',
            'LF OI %','LF 1w OI Chg','LF 4w OI Chg','LF 6m OI Chg','LF 12m OI Chg']].tolist(),

        'US': ['','','','','','','','','',''],
        'US Real Money': real_fast_money_pos_dict['US'].loc[chosen_date][[
            'AM Net Positions','AM 1w Pos Chg','AM 4w Pos Chg','AM 6m Pos Chg','AM 12m Pos Chg',
            'AM OI %','AM 1w OI Chg','AM 4w OI Chg','AM 6m OI Chg','AM 12m OI Chg']].tolist(),
        'US Fast Money': real_fast_money_pos_dict['US'].loc[chosen_date][[
            'LF Net Positions','LF 1w Pos Chg','LF 4w Pos Chg','LF 6m Pos Chg','LF 12m Pos Chg',
            'LF OI %','LF 1w OI Chg','LF 4w OI Chg','LF 6m OI Chg','LF 12m OI Chg']].tolist(),

        'WN': ['','','','','','','','','',''],
        'WN Real Money': real_fast_money_pos_dict['WN'].loc[chosen_date][[
            'AM Net Positions','AM 1w Pos Chg','AM 4w Pos Chg','AM 6m Pos Chg','AM 12m Pos Chg',
            'AM OI %','AM 1w OI Chg','AM 4w OI Chg','AM 6m OI Chg','AM 12m OI Chg']].tolist(),
        'WN Fast Money': real_fast_money_pos_dict['WN'].loc[chosen_date][[
            'LF Net Positions','LF 1w Pos Chg','LF 4w Pos Chg','LF 6m Pos Chg','LF 12m Pos Chg',
            'LF OI %','LF 1w OI Chg','LF 4w OI Chg','LF 6m OI Chg','LF 12m OI Chg']].tolist(),
    }).T
    df = cftc_am_of_snapshot.copy()
    df.columns = [
        'Net Pos', '1w Pos', '4w Pos', '6m Pos', '12m Pos',
        'Pos % OI','1w OI','4w OI','6m OI','12m OI'
    ]
    section_rows = {'TU','FV','TY','UXY','US','WN'}
    dark_blue_rows = {"TU","FV","TY","UXY","US","WN"}

    def style_fed_table(df):
        styler = df.style
        # --- formatting: numeric vs OI % columns ---
        pos_cols = ['Net Pos', '1w Pos', '4w Pos', '6m Pos', '12m Pos']
        oi_cols = ['Pos % OI','1w OI','4w OI','6m OI','12m OI']

        def pos_formatter(x):
            if isinstance(x, (int, float)) and not pd.isna(x):
                return f"{x:,.0f}"
            return x

        def oi_formatter(x):
            if isinstance(x, (int, float)) and not pd.isna(x):
                return f"{x:0.2f}%"   # 2 decimals + percent sign
            return x

        styler = styler.format(pos_formatter, subset=pos_cols, na_rep="")
        styler = styler.format(oi_formatter, subset=oi_cols, na_rep="")
        styler = styler.set_table_styles(
            [
                {
                    "selector": "table",
                    "props": [
                        ("border-collapse", "collapse"),
                        ("font-family", "Calibri, Arial, sans-serif"),
                        ("font-size", "14px"),
                        ("table-layout", "fixed"),   # fixed layout to respect widths
                        ("width", "100%"),           # fill full page width
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
                        ("width", "150px"),
                        ("max-width", "300px"),
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

        # center all data columns and give equal widths
        numeric_cols = pos_cols + oi_cols
        existing_cols = [c for c in numeric_cols if c in df.columns]
        if existing_cols:
            styler = styler.set_properties(
                subset=pd.IndexSlice[:, existing_cols],
                **{"text-align": "center"},
            )
            # full width (100%) minus some slack can be allocated evenly
            per_col = 100 / len(existing_cols)
            extra_styles = []
            for i, col in enumerate(existing_cols):
                extra_styles.append(
                    {
                        "selector": f"th.col_heading.level0.col{i}",
                        "props": [("width", f"{per_col:.2f}%")],
                    }
                )
            styler = styler.set_table_styles(styler.table_styles + extra_styles)

        # row banding for header rows
        def row_style(row):
            if row.name in dark_blue_rows:
                return [
                    "background-color: #002b55; color: white; "
                    "font-weight: bold; text-align:left;"
                ] * len(row)
            return [""] * len(row)
        styler = styler.apply(row_style, axis=1)

        def index_style(idx_series):
            styles = []
            for label in idx_series:
                if label in section_rows:
                    styles.append("padding-left: 4px; font-weight: bold;")
                else:
                    styles.append("padding-left: 20px; font-weight: normal;")
            return styles
        styler = styler.apply_index(index_style, axis=0)

        # color + bold non-zero numbers
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

    ### STREAMLIT PLOTS ###
    subplots_array = [
        # 1) Net positions (levels)
        lambda: streamlit_plot(
            am_net_positions,
            ['TU','FV','TY','UXY','US','WN'],
            [
            cftc_colors_dict["TU"],
            cftc_colors_dict["FV"],
            cftc_colors_dict["TY"],
            cftc_colors_dict["UXY"],
            cftc_colors_dict["US"],
            cftc_colors_dict["WN"],
        ],
            ['TU','FV','TY','UXY','US','WN'],
            "Real Money Net Positions",
            "",
        ),
        # 2) Net positions Z-scores
        lambda: streamlit_plot(
            am_pos_oi,
            ['TU','FV','TY','UXY','US','WN'],
            [
            cftc_colors_dict["TU"],
            cftc_colors_dict["FV"],
            cftc_colors_dict["TY"],
            cftc_colors_dict["UXY"],
            cftc_colors_dict["US"],
            cftc_colors_dict["WN"],
        ],
            ['TU','FV','TY','UXY','US','WN'],
            "Real Money Net Positions OI %",
            "",
        ),
        # 3) % of back
        lambda: streamlit_plot(
            lf_net_positions,
            ['TU','FV','TY','UXY','US','WN'],
            [
            cftc_colors_dict["TU"],
            cftc_colors_dict["FV"],
            cftc_colors_dict["TY"],
            cftc_colors_dict["UXY"],
            cftc_colors_dict["US"],
            cftc_colors_dict["WN"],
        ],
            ['TU','FV','TY','UXY','US','WN'],
            "Fast Money Net Positions",
            "",
        ),
        # 4) % of back Z-scores
        lambda: streamlit_plot(
            lf_pos_oi,
            ['TU','FV','TY','UXY','US','WN'],
            [
            cftc_colors_dict["TU"],
            cftc_colors_dict["FV"],
            cftc_colors_dict["TY"],
            cftc_colors_dict["UXY"],
            cftc_colors_dict["US"],
            cftc_colors_dict["WN"],
        ],
            ['TU','FV','TY','UXY','US','WN'],
            "Fast Money Net Positions OI% ",
            "",
        ),
    ]
    streamlit_plot_subplot_layout(subplots_array, 2, 2)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- REAL MONEY VS FAST MONEY ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def real_money_fast_money_master_fxn(bond_fut_str):
    subplots_array = [
        lambda: streamlit_plot(
            real_fast_fut_data,
            ["AM Net Positions", "AM 4w Pos MA", "AM 6m Pos MA"],
            [
                cftc_colors_shades[bond_fut_str][0],
                cftc_colors_shades[bond_fut_str][1],
                cftc_colors_shades[bond_fut_str][2],
            ],
            ["Net Positions", "4w MA", "6m MA"],
            "Real Money Net Positions",
            "",
        ),
        lambda: streamlit_plot(
            real_fast_fut_data,
            ["AM OI %", "AM 4w OI MA", "AM 6m OI MA"],
            [
                cftc_colors_shades[bond_fut_str][0],
                cftc_colors_shades[bond_fut_str][1],
                cftc_colors_shades[bond_fut_str][2],
            ],
            ["Net Positions % OI", "4w MA", "6m MA"],
            "Real Money Net Positions % of OI",
            "",
        ),
        lambda: streamlit_plot(
            real_fast_fut_data,
            ["LF Net Positions", "LF 4w Pos MA", "LF 6m Pos MA"],
            [
                cftc_colors_shades[bond_fut_str][0],
                cftc_colors_shades[bond_fut_str][1],
                cftc_colors_shades[bond_fut_str][2],
            ],
            ["Net Positions", "4w MA", "6m MA"],
            "Fast Money Net Positions",
            "",
        ),
        lambda: streamlit_plot(
            real_fast_fut_data,
            ["LF OI %", "LF 4w OI MA", "LF 6m OI MA"],
            [
                cftc_colors_shades[bond_fut_str][0],
                cftc_colors_shades[bond_fut_str][1],
                cftc_colors_shades[bond_fut_str][2],
            ],
            ["Net Positions % OI", "4w MA", "6m MA"],
            "Fast Money Net Positions % of OI",
            "",
        ),
    ]
    streamlit_plot_subplot_layout(subplots_array, 2, 2)

    streamlit_plot(
        real_fast_fut_data,
        ["AM OI % Z", "LF OI % Z"],
        [
            cftc_colors_shades[bond_fut_str][0],
            cftc_colors_shades[bond_fut_str][2],
        ],
        ["Real Money", "Fast Money"],
        "Real Money vs. Fast Money Net Positions % OI Z-Scored",
        "",
    )

def real_fast_tu(start, end, **kwargs):
    real_money_fast_money_master_fxn('TU')
def real_fast_fv(start, end, **kwargs):
    real_money_fast_money_master_fxn('FV')
def real_fast_ty(start, end, **kwargs):
    real_money_fast_money_master_fxn('TY')
def real_fast_uxy(start, end, **kwargs):
    real_money_fast_money_master_fxn('UXY')
def real_fast_us(start, end, **kwargs):
    real_money_fast_money_master_fxn('US')
def real_fast_wn(start, end, **kwargs):
    real_money_fast_money_master_fxn('WN')

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- REAL MONEY VS FAST MONEY ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def real_money_fast_money_summary(start, end, **kwargs):
    base_series = real_fast_money_pos_dict["TU"]
    all_dates = base_series.index.sort_values()

    # Round existing series/DFs to 2 decimals and keep zeros as 0
    for key, obj in real_fast_money_pos_dict.items():
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            real_fast_money_pos_dict[key] = obj.round(2)
            real_fast_money_pos_dict[key] = real_fast_money_pos_dict[key].where(
                real_fast_money_pos_dict[key] != 0, 0
            )

    chosen_date = st.selectbox(
        "Select Snapshot Date",
        options=all_dates,
        index=len(all_dates) - 1,
        format_func=lambda d: d.strftime("%Y-%m-%d"),
    )

    # Only AM / LF Z-score columns, 2 decimals
    cftc_am_of_snapshot = pd.DataFrame({
        'TU':  real_fast_money_dict['TU'].loc[chosen_date][[
            'AM Net Positions Z',"AM OI % Z", "LF OI % Z",'LF Net Positions Z']],
        'FV':  real_fast_money_dict['FV'].loc[chosen_date][[
            'AM Net Positions Z',"AM OI % Z", "LF OI % Z",'LF Net Positions Z']],
        'TY':  real_fast_money_dict['TY'].loc[chosen_date][[
            'AM Net Positions Z',"AM OI % Z", "LF OI % Z",'LF Net Positions Z']],
        'UXY': real_fast_money_dict['UXY'].loc[chosen_date][[
            'AM Net Positions Z',"AM OI % Z", "LF OI % Z",'LF Net Positions Z']],
        'US':  real_fast_money_dict['US'].loc[chosen_date][[
            'AM Net Positions Z',"AM OI % Z", "LF OI % Z",'LF Net Positions Z']],
        'WN':  real_fast_money_dict['WN'].loc[chosen_date][[
            'AM Net Positions Z',"AM OI % Z", "LF OI % Z",'LF Net Positions Z']],
    }).T.round(2)

    df = cftc_am_of_snapshot.copy()
    df.columns = ["AM Pos", "AM Pos %",'LF Pos','LF Pos %']  # simple, no extra labels

    def style_simple(df):
        styler = df.style

        # format both columns to 2 decimals
        styler = styler.format("{:.2f}")

        # color positives green, negatives red, zeros default
        def color_and_bold_nonzero(val):
            if pd.isna(val) or not isinstance(val, (int, float)):
                return ""
            if val > 0:
                return "color: #008000; font-weight:bold;"
            if val < 0:
                return "color: #CC0000; font-weight:bold;"
            return ""

        for col in df.columns:
            styler = styler.applymap(color_and_bold_nonzero, subset=pd.IndexSlice[:, col])

        return styler

    styled = style_simple(df)
    html = styled.to_html()
    st.markdown(html, unsafe_allow_html=True)

