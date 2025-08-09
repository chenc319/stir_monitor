### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- PRIMARY DEALERS --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###













import requests
import pandas as pd
import matplotlib.pyplot as plt

# 1. Get all available weekly report dates
asof_url = "https://markets.newyorkfed.org/api/pd/list/asof.json"
asofdates = requests.get(asof_url).json()['pd']['asofdates']
dates = [d['asof'] for d in asofdates]

# 2. Define tenor mapping — update if API/field names change
tenor_mnemonics = {
    '<2Y': 'PDPOSTSYLT2Y',          # U.S. Treasury Coupon Issues: <2Y
    '2-3Y': 'PDPOSTSYNO2TO3',       # U.S. Treasury Coupon Issues: 2-3Y
    '3-6Y': 'PDPOSTSYNTHREE6',      # U.S. Treasury Coupon Issues: 3-6Y
    '6-7Y': 'PDPOSTSYNSIX7',        # U.S. Treasury Coupon Issues: 6-7Y
    '7-10Y': 'PDPOSTSYSEVEN10',     # U.S. Treasury Coupon Issues: 7-10Y
}

records = []
for d in dates:
    try:
        r = requests.get(f"https://markets.newyorkfed.org/api/pd/get/asof/{d}.json")
        series = r.json()['pd']['series']
        row = {'date': pd.to_datetime(d)}
        for label, mnemonic in tenor_mnemonics.items():
            # Find the series for each tenor mnemonic
            val = next((item for item in series if item['mnemonic'] == mnemonic), None)
            if val and 'observations' in val and val['observations']:
                # Values are in millions of dollars
                row[label] = float(val['observations'][0]['value'])
            else:
                row[label] = None
        records.append(row)
    except Exception as e:
        # Skip problematic weeks
        continue

df = pd.DataFrame(records).set_index('date').sort_index()
df = df / 1e3  # Convert to billions for visual clarity

# 3. Plot the time series
plt.figure(figsize=(14, 8))
colors = ['#60cfff', '#33a1cc', '#063952', '#ffc13b', '#fb9483']
for i, col in enumerate(df.columns):
    plt.plot(df.index, df[col], label=f'Bond {col}', lw=2, color=colors[i])

plt.title('Primary Dealers Net Positions By Bond Tenor')
plt.ylabel('Dollars (Billions)')
plt.xlabel('Date')
plt.legend()
plt.tight_layout()
plt.grid(True, alpha=0.4)
plt.show()
