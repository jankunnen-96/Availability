import pandas as pd
from collections import defaultdict
from datetime import datetime
import json

# Load the spreadsheet
file_path = "Beschikbaarheid.xlsx"
df = pd.read_excel(file_path, sheet_name='Overview')

# Clean date column headers
df.columns = [col.strftime('%Y-%m-%d') if isinstance(col, datetime) else col for col in df.columns]

# Build JSON structure
result = {}

for _, row in df.iterrows():
    name = row['Voornaam'].strip().lower()
    availability = defaultdict(dict)

    for date_str in row.index[1:]:
        value = row[date_str]
        if pd.notna(value):
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            month_key = f"{dt.year}-{dt.month:02d}"
            day_key = str(dt.day)
            availability[month_key][day_key] = str(value)

    result[name] = dict(availability)

# Save to JSON
with open("availability_2.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Saved as availability.json")