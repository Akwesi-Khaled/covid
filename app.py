import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ---- APP TITLE ----
st.set_page_config(page_title="COVID-19 Tracker", layout="wide")
st.title("🌍 COVID-19 Latest Statistics")

# ---- API DETAILS ----
url = "https://covid-19-data.p.rapidapi.com"
headers = {
    "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
    "X-RapidAPI-Host": "covid-19-data.p.rapidapi.com"
}

# ---- FETCH DATA ----
@st.cache_data(ttl=3600)
def get_data():
    response = requests.get(url, headers=headers)
    data = response.json()
    df = pd.json_normalize(data["response"])
    df.fillna(0, inplace=True)
    # Convert numeric columns to int
    for col in ["cases.total", "cases.recovered", "cases.active", "deaths.total"]:
        df[col] = df[col].astype(int)
    return df

df = get_data()

# ---- GLOBAL SUMMARY ----
total_cases = df["cases.total"].sum()
total_deaths = df["deaths.total"].sum()
total_recovered = df["cases.recovered"].sum()
total_active = df["cases.active"].sum()

st.subheader("🌐 Global Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cases", f"{total_cases:,}")
col2.metric("Total Deaths", f"{total_deaths:,}")
col3.metric("Total Recovered", f"{total_recovered:,}")
col4.metric("Active Cases", f"{total_active:,}")

st.divider()

# ---- COUNTRY SELECTION ----
countries = sorted(df["country"].unique())
selected_country = st.selectbox("Select a country:", countries, index=countries.index("Ghana") if "Ghana" in countries else 0)
country_data = df[df["country"] == selected_country].iloc[0]

st.subheader(f"📍 COVID-19 in {selected_country}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cases", f"{country_data['cases.total']:,}")
col2.metric("Total Deaths", f"{country_data['deaths.total']:,}")
col3.metric("Total Recovered", f"{country_data['cases.recovered']:,}")
col4.metric("Active Cases", f"{country_data['cases.active']:,}")

st.divider()

# ---- TOP 10 COUNTRIES BY CASES ----
st.subheader("📊 Top 10 Countries by Total Cases")
top10 = df.sort_values(by="cases.total", ascending=False).head(10)
fig = px.bar(top10, x="country", y="cases.total",
             hover_data=["deaths.total", "cases.recovered", "cases.active"],
             labels={"cases.total": "Total Cases", "country": "Country"},
             color="cases.total", color_continuous_scale="Reds")
st.plotly_chart(fig, use_container_width=True)

# ---- FULL TABLE ----
st.subheader("All Countries Summary")
st.dataframe(df[["country", "cases.total", "cases.recovered", "cases.active", "deaths.total"]].sort_values(by="cases.total", ascending=False))
