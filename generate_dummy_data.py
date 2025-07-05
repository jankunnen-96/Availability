import json
import os
import random
from datetime import datetime, date

USERS_FILE = "users.json"
DATA_DIR = "data"
CONFIG_FILE = "config.json"
MONTHS = [6, 7, 8, 9]
VALUES = ["Ja", "Nee", "9-12", "13-17", "8-16"]

with open(USERS_FILE, "r") as f:
    users = json.load(f)
with open(CONFIG_FILE, "r") as f:
    year = json.load(f)["year"]

def get_days_in_month(year, month):
    from calendar import monthrange
    return monthrange(year, month)[1]

for user in users:
    if user["role"] != "user":
        continue
    username = user["username"]
    for month in MONTHS:
        days = get_days_in_month(year, month)
        month_str = f"{year}-{month:02d}"
        avail_path = f"{DATA_DIR}/availability_{username}_{month_str}.json"
        availability = {str(i): random.choice(VALUES) for i in range(1, days + 1)}
        os.makedirs(os.path.dirname(avail_path), exist_ok=True)
        with open(avail_path, "w") as f:
            json.dump(availability, f, indent=2)
print("Dummy data generated.") 