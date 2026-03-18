### ------------------------------------------------------------------------------------------------- ###
### ------------------------------------- POSITIONING DATA PULL ------------------------------------- ###
### ------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
from Functions import *
from pathlib import Path
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

### ------------------------------------------------------------------------------------------------ ###
### ---------------------------------------- CFTC DATA PULL ---------------------------------------- ###
### ------------------------------------------------------------------------------------------------ ###

years_array = ['2022','2023','2024','2025','2026']
all_bond_fut_names = [
    'UST 2Y NOTE - CHICAGO BOARD OF TRADE',
    'UST 5Y NOTE - CHICAGO BOARD OF TRADE',
    'UST 10Y NOTE - CHICAGO BOARD OF TRADE',
    'ULTRA UST 10Y - CHICAGO BOARD OF TRADE',
    'UST BOND - CHICAGO BOARD OF TRADE',
    'ULTRA UST BOND - CHICAGO BOARD OF TRADE',
]
tu_historical_futopt_df = pd.DataFrame()
fv_historical_futopt_df = pd.DataFrame()
ty_historical_futopt_df = pd.DataFrame()
uxy_historical_futopt_df = pd.DataFrame()
us_historical_futopt_df = pd.DataFrame()
wn_historical_futopt_df = pd.DataFrame()
for year_str in years_array:
    year_df = cot_year(
        year = year_str,
        cot_report_type= 'traders_in_financial_futures_futopt'
    )
    tu_mini_df = year_df[year_df['Market_and_Exchange_Names'] ==
                         'UST 2Y NOTE - CHICAGO BOARD OF TRADE']
    tu_mini_df.index = pd.to_datetime(tu_mini_df['Report_Date_as_YYYY-MM-DD']).values
    tu_mini_df = tu_mini_df.sort_index()

    fv_mini_df = year_df[year_df['Market_and_Exchange_Names'] ==
                         'UST 5Y NOTE - CHICAGO BOARD OF TRADE']
    fv_mini_df.index = pd.to_datetime(fv_mini_df['Report_Date_as_YYYY-MM-DD']).values
    fv_mini_df = fv_mini_df.sort_index()

    ty_mini_df = year_df[year_df['Market_and_Exchange_Names'] ==
                         'UST 10Y NOTE - CHICAGO BOARD OF TRADE']
    ty_mini_df.index = pd.to_datetime(ty_mini_df['Report_Date_as_YYYY-MM-DD']).values
    ty_mini_df = ty_mini_df.sort_index()

    uxy_mini_df = year_df[year_df['Market_and_Exchange_Names'] ==
                         'ULTRA UST 10Y - CHICAGO BOARD OF TRADE']
    uxy_mini_df.index = pd.to_datetime(uxy_mini_df['Report_Date_as_YYYY-MM-DD']).values
    uxy_mini_df = uxy_mini_df.sort_index()

    us_mini_df = year_df[year_df['Market_and_Exchange_Names'] ==
                         'UST BOND - CHICAGO BOARD OF TRADE']
    us_mini_df.index = pd.to_datetime(us_mini_df['Report_Date_as_YYYY-MM-DD']).values
    us_mini_df = us_mini_df.sort_index()

    wn_mini_df = year_df[year_df['Market_and_Exchange_Names'] ==
                         'ULTRA UST BOND - CHICAGO BOARD OF TRADE']
    wn_mini_df.index = pd.to_datetime(wn_mini_df['Report_Date_as_YYYY-MM-DD']).values
    wn_mini_df = wn_mini_df.sort_index()

    tu_historical_futopt_df = pd.concat([tu_historical_futopt_df,tu_mini_df],axis=0)
    fv_historical_futopt_df = pd.concat([fv_historical_futopt_df,fv_mini_df],axis=0)
    ty_historical_futopt_df = pd.concat([ty_historical_futopt_df,ty_mini_df],axis=0)
    uxy_historical_futopt_df = pd.concat([uxy_historical_futopt_df,uxy_mini_df],axis=0)
    us_historical_futopt_df = pd.concat([us_historical_futopt_df,us_mini_df],axis=0)
    wn_historical_futopt_df = pd.concat([wn_historical_futopt_df,wn_mini_df],axis=0)

cftc_bond_futures_dict = {
    'TU': tu_historical_futopt_df,
    'FV': fv_historical_futopt_df,
    'TY': ty_historical_futopt_df,
    'UXY': uxy_historical_futopt_df,
    'US': us_historical_futopt_df,
    'WN': wn_historical_futopt_df,
}

with open(Path(DATA_DIR) / 'cftc_bond_futures_dict.pkl', 'wb') as file:
    pickle.dump(cftc_bond_futures_dict, file)

### ------------------------------------------------------------------------------------------------ ###
### ----------------------------------- CAYMAN ISLANDS DATA PULL ----------------------------------- ###
### ------------------------------------------------------------------------------------------------ ###

foreign_holdings = ("https://ticdata.treasury.gov/resource-center/"
                    "data-chart-center/tic/Documents/slt_table1.txt")
tic_columns = [
    'Country',
    'Country Code',
    'Date',
    'Total US Securities Holdings',
    'Total US Securities Net US Sales',
    'Total US Securtities Valuation Change',
    'US Treasuries Holdings',
    'US Treasuries Net US Sales',
    'US Treasuries Valuation Change',
    'US Agency Bonds Holdings',
    'US Agency Bonds Net US Sales',
    'US Agency Bonds Valuation Change',
    'US Corp and Other Bonds Holdings',
    'US Corp and Other Bonds Net US Sales',
    'US Corp and Other Bonds Valuation Change',
    'US Corp Equity Holdings',
    'US Corp Equity Net US Sales',
    'US Corp Equity Valuation Change',
]
tic_df = pd.read_csv(foreign_holdings, sep="\t")
tic_df = tic_df.iloc[8:]
tic_df.columns = tic_columns
cayman_df = tic_df[tic_df['Country'] == 'Cayman Islands']
cayman_df = cayman_df.replace("n.a.", pd.NA)
cayman_df = cayman_df.dropna()
cayman_df.index = pd.to_datetime(cayman_df['Date'])
cayman_df = cayman_df.resample('ME').sum()

with open(Path(DATA_DIR) / 'cayman_df.pkl', 'wb') as file:
    pickle.dump(cayman_df, file)
