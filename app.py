import streamlit as st
import requests

# API credentials
url = "https://covid-19-data.p.rapidapi.com/country"
headers = {
    "X-RapidAPI-Key": "7ef75016e6mshd080ad5607cce21p1878a4jsn7352066fcd77",
    "X-RapidAPI-Host": "covid-19-data.p.rapidapi.com"
}

# Streamlit UI
st.title("COVID-19 Country Data Tracker")
country = st.text_input("Enter Country Name:", "Ghana")

if st.button("Get Data"):
    querystring = {"name": country}
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            country_data = data[0]
            st.write(f"**Country:** {country_data['country']}")
            st.write(f"**Confirmed Cases:** {country_data['confirmed']}")
            st.write(f"**Deaths:** {country_data['deaths']}")
            st.write(f"**Recovered:** {country_data['recovered']}")
        else:
            st.error("No data found for this country.")
    else:
        st.error("Failed to fetch data. Try again later.")

