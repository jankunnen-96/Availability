import streamlit as st
st.set_page_config(layout="wide")
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd

# --- Constants ---
USERS_FILE = "users.json"
DATA_DIR = "data"
CONFIG_FILE = "config.json"
MONTHS = [(6, "Juni"), (7, "Juli"), (8, "Augustus"), (9, "September")]
DUTCH_WEEKDAYS = ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo']
AVAILABILITY_FILE = "availability.json"

# --- Helper Functions ---
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_days_in_month(year, month):
    from calendar import monthrange
    return monthrange(year, month)[1]

def get_dutch_weekday(year, month, day):
    # Python's weekday(): Monday=0, Sunday=6
    weekday = date(year, month, day).weekday()
    return DUTCH_WEEKDAYS[weekday]

def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_availability():
    return load_json(AVAILABILITY_FILE, default={})

def save_availability(data):
    save_json(AVAILABILITY_FILE, data)

# --- Authentication ---
def login_screen(users):
    st.markdown("<h1 style='text-align: center;'>🏊‍♂️ Wouterbron Planning 🏖️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Duik in je planning 🫧</p>", unsafe_allow_html=True)
    
    usernames = [u["username"] for u in users]
    username = st.selectbox("🏷️ Selecteer je gebruikersnaam", usernames)
    password = st.text_input("🔒 Paswoord", type="password")

    if st.button("💦 Login"):
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("🚫 Foutieve gebruikersnaam of paswoord")

# --- User Calendar ---
def user_calendar(user, year):
    st.title(f"Welkom, {user['username'].capitalize()}")
    st.subheader(f"Jouw beschikbaarheid voor {year}")
    st.markdown(""" Duid je beschikbaarheid aan door een "x" in het veld te plaatsen als je de hele dag beschikbaar bent of een uurrange (bv 11- 19) als je een deel van de dag beschikbaar bent. Waar je niet kan, de x verwijderen. Ga nauwkeurig te werk .""")

    availability_data = load_availability()
    username = user['username']
    for month, month_name in MONTHS:
        st.markdown(f"## {month_name} {year}")
        days = get_days_in_month(year, month)
        month_str = f"{year}-{month:02d}"
        user_month = availability_data.get(username, {}).get(month_str, {})
        columns = [f"{i} {get_dutch_weekday(year, month, i)}" for i in range(1, days + 1)]
        data = {col: user_month.get(str(i), "") for i, col in enumerate(columns, 1)}
        edited = st.data_editor(
            pd.DataFrame([data]),
            column_config={col: st.column_config.TextColumn() for col in columns},
            hide_index=True,
            key=f"user_editor_{month_str}"
        )
        if st.button(f"Beschikbaarheid opslaan voor {month_name}", key=f"save_{month_str}"):
            to_save = {str(i): edited.iloc[0][col] for i, col in enumerate(columns, 1)}
            if username not in availability_data:
                availability_data[username] = {}
            availability_data[username][month_str] = to_save
            save_availability(availability_data)
            st.success(f"Saved for {month_name}!")

# --- Admin Dashboard ---
def admin_dashboard(users, year):
    st.title("Admin Dashboard")
    st.subheader(f"Edit All Users' Availability for {year}")
    usernames = [u["username"] for u in users if u["role"] == "user"]
    availability_data = load_availability()
    for month, month_name in MONTHS:
        st.markdown(f" {month_name} {year}")
        days = get_days_in_month(year, month)
        month_str = f"{year}-{month:02d}"
        columns = [f"{i} {get_dutch_weekday(year, month, i)}" for i in range(1, days + 1)]
        data = []
        for username in usernames:
            user_month = availability_data.get(username, {}).get(month_str, {})
            row = {col: user_month.get(str(i), "") for i, col in enumerate(columns, 1)}
            row["Gebruiker"] = username
            data.append(row)
        df = pd.DataFrame(data).set_index("Gebruiker")
        edited = st.data_editor(
            df,
            height=650,
            key=f"admin_editor_{month_str}"
        )
        if st.button(f"Beschikbaarheid opslaan voor {month_name}", key=f"save_admin_{month_str}"):
            for username in usernames:
                row = edited.loc[username]
                to_save = {str(i): row[col] for i, col in enumerate(columns, 1)}
                if username not in availability_data:
                    availability_data[username] = {}
                availability_data[username][month_str] = to_save
            save_availability(availability_data)
            st.success(f"Saved availability for {month_name}!")

# --- Main App ---
def main():
    users = load_users()
    config = load_config()
    year = config.get("year", datetime.now().year)
    if "user" not in st.session_state:
        login_screen(users)
        return
    user = st.session_state["user"]
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()
    if user["role"] == "admin":
        admin_dashboard(users, year)
    else:
        user_calendar(user, year)

if __name__ == "__main__":
    main() 