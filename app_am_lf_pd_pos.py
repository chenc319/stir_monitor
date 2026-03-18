### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- PRIMARY DEALERS --------------------------------------------- ###
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

### PRE CALCULATIONS ###
real_fast_money_pos_dict = {}
for each_bond_key in cftc_bond_futures_dict.keys():
    df = cftc_bond_futures_dict[each_bond_key]
    df['AM Net Positions'] = (df['Asset_Mgr_Positions_Long_All'] -
                              df['Asset_Mgr_Positions_Short_All'])
    df['LF Net Positions'] = (df['Lev_Money_Positions_Long_All'] -
                             df['Lev_Money_Positions_Short_All'])
    df['AM 1w Chg'] = df['AM Net Positions'].diff(1)
    df['AM 4w Chg'] = df['AM Net Positions'].diff(4)
    df['AM 6m Chg'] = df['AM Net Positions'].diff(26)
    df['AM 12m Chg'] = df['AM Net Positions'].diff(52)
    df['AM OI %'] = (df['AM Net Positions'] / df['Open_Interest_All']) * 100

    df['LF 1w Chg'] = df['LF Net Positions'].diff(1)
    df['LF 4w Chg'] = df['LF Net Positions'].diff(4)
    df['LF 6m Chg'] = df['LF Net Positions'].diff(26)
    df['LF 12m Chg'] = df['LF Net Positions'].diff(52)
    df['LF OI %'] = (df['LF Net Positions'] / df['Open_Interest_All']) * 100

    real_fast_money_pos_dict[each_bond_key] = pd.DataFrame(df[[
        'AM Net Positions',
        'AM 1w Chg',
        'AM 4w Chg',
        'AM 6m Chg',
        'AM 12m Chg',
        'AM OI %',
        'LF Net Positions',
        'LF 1w Chg',
        'LF 4w Chg',
        'LF 6m Chg',
        'LF 12m Chg',
        'LF OI %'
    ]])

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- PRIMARY DEALER WAREHOUSE OVERVIEW ------------------------------------ ###
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
        'TU': ['','','','','',''],
        'TU Real Money': real_fast_money_pos_dict['TU'].loc[chosen_date][[
            'AM Net Positions','AM 1w Chg','AM 4w Chg','AM 6m Chg','AM 12m Chg','AM OI %']].tolist(),
        'TU Fast Money': real_fast_money_pos_dict['TU'].loc[chosen_date][[
            'LF Net Positions','LF 1w Chg','LF 4w Chg','LF 6m Chg','LF 12m Chg','LF OI %']].tolist(),

        'FV': ['','','','','',''],
        'FV Real Money': real_fast_money_pos_dict['FV'].loc[chosen_date][[
            'AM Net Positions','AM 1w Chg','AM 4w Chg','AM 6m Chg','AM 12m Chg','AM OI %']].tolist(),
        'FV Fast Money': real_fast_money_pos_dict['FV'].loc[chosen_date][[
            'LF Net Positions','LF 1w Chg','LF 4w Chg','LF 6m Chg','LF 12m Chg','LF OI %']].tolist(),

        'TY': ['','','','','',''],
        'TY Real Money': real_fast_money_pos_dict['TY'].loc[chosen_date][[
            'AM Net Positions','AM 1w Chg','AM 4w Chg','AM 6m Chg','AM 12m Chg','AM OI %']].tolist(),
        'TY Fast Money': real_fast_money_pos_dict['TY'].loc[chosen_date][[
            'LF Net Positions','LF 1w Chg','LF 4w Chg','LF 6m Chg','LF 12m Chg','LF OI %']].tolist(),

        'UXY': ['','','','','',''],
        'UXY Real Money': real_fast_money_pos_dict['UXY'].loc[chosen_date][[
            'AM Net Positions','AM 1w Chg','AM 4w Chg','AM 6m Chg','AM 12m Chg','AM OI %']].tolist(),
        'UXY Fast Money': real_fast_money_pos_dict['UXY'].loc[chosen_date][[
            'LF Net Positions','LF 1w Chg','LF 4w Chg','LF 6m Chg','LF 12m Chg','LF OI %']].tolist(),

        'US': ['','','','','',''],
        'US Real Money': real_fast_money_pos_dict['US'].loc[chosen_date][[
            'AM Net Positions','AM 1w Chg','AM 4w Chg','AM 6m Chg','AM 12m Chg','AM OI %']].tolist(),
        'US Fast Money': real_fast_money_pos_dict['US'].loc[chosen_date][[
            'LF Net Positions','LF 1w Chg','LF 4w Chg','LF 6m Chg','LF 12m Chg','LF OI %']].tolist(),

        'WN': ['','','','','',''],
        'WN Real Money': real_fast_money_pos_dict['WN'].loc[chosen_date][[
            'AM Net Positions','AM 1w Chg','AM 4w Chg','AM 6m Chg','AM 12m Chg','AM OI %']].tolist(),
        'WN Fast Money': real_fast_money_pos_dict['WN'].loc[chosen_date][[
            'LF Net Positions','LF 1w Chg','LF 4w Chg','LF 6m Chg','LF 12m Chg','LF OI %']].tolist(),
    }).T

    df = cftc_am_of_snapshot.copy()
    df.columns = ['Net Positions', '1w Chg', '4w Chg', '6m Chg', '12m Chg', 'OI %']

    # all headers (untabbed + bold)
    section_rows = {
        'TU',
        'FV',
        'TY',
        'UXY',
        'US',
        'WN'
    }

    # only these get the dark-blue band
    dark_blue_rows = {
        "TU",
        "FV",
        "TY",
        "UXY",
        "US",
        "WN"
    }

    def style_fed_table(df):
        styler = df.style

        def numeric_formatter(x):
            if isinstance(x, (int, float)) and not pd.isna(x):
                return f"{x:,.0f}"
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

        numeric_cols = ['Net Positions', '1w Chg', '4w Chg', '6m Chg', '12m Chg', 'OI %']
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

        for col in ['Net Positions', '1w Chg', '4w Chg', '6m Chg', '12m Chg', 'OI %']:
            if col in df.columns:
                styler = styler.applymap(
                    color_and_bold_nonzero, subset=pd.IndexSlice[:, col]
                )

        return styler

    styled = style_fed_table(df)
    html = styled.to_html()
    st.markdown(html, unsafe_allow_html=True)
