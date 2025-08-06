import requests
import pandas as pd

# Base Fiscal Data API URL and endpoint
BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/"
ENDPOINT = "securities_auctions"
FULL_URL = BASE_URL + ENDPOINT

# API parameters for fields and paging
params = {
    'fields': 'record_date,security_type,security_term,offering_amount',
    'page[size]': 1000,  # Max entries per page
    'sort': 'record_date' # Ascending by date
}

# Download and combine all pages for comprehensive data
results = []
while True:
    resp = requests.get(FULL_URL, params=params)
    resp.raise_for_status()
    result = resp.json()
    # Flatten and collect attribute dicts for each result
    results.extend([item['attributes'] for item in result['data']])
    # Follow next link for more pages
    if 'next' in result['links']:
        FULL_URL = result['links']['next']
        params = {}  # Params not needed when using 'next' link
    else:
        break

df = pd.DataFrame(results)

# (Optional) Process data: filter by security type, convert amounts, etc.
# Example - only Bills, Notes, Bonds:
df = df[df['security_type'].isin(['Bill', 'Note', 'Bond'])]
df['record_date'] = pd.to_datetime(df['record_date'])

print(df.head())
