import streamlit as st
import requests
import pandas as pd

# --- Configuration for Streamlit Page ---
st.set_page_config(
    page_title="COVID-19 Latest Data Tracker",
    page_icon="🦠",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Country Name to ISO Code Mapping ---
# The API uses country codes (e.g., 'us') while the user uses names.
# This dictionary handles the conversion. You can expand this list.
COUNTRY_CODES = {
    "United States": "us",
    "United Kingdom": "gb",
    "Canada": "ca",
    "India": "in",
    "Australia": "au",
    "France": "fr",
    "Germany": "de",
    "Brazil": "br",
    "Japan": "jp",
    "Italy": "it"
}

# --- RapidAPI Secrets Management ---
# The secrets must be stored in st.secrets in a TOML format for deployment.
# We use a try-except block to allow local testing (where secrets might be missing).
try:
    API_HOST = st.secrets["rapidapi"]["host"]
    API_KEY = st.secrets["rapidapi"]["key"]
except KeyError:
    st.error("⚠️ **API Keys Missing!** Please configure `secrets.toml` or Streamlit secrets.")
    API_HOST = "covid-19-data.p.rapidapi.com" # Placeholder host
    API_KEY = "YOUR_API_KEY_HERE" # Placeholder key

# --- API Caching Function ---
@st.cache_data(ttl=3600) # Cache the data for 1 hour (3600 seconds)
def fetch_country_data(country_code):
    """Fetches the latest COVID-19 data for a given country code."""
    
    url = "https://covid-19-data.p.rapidapi.com/country/code"
    
    # The API requires parameters for country code and format
    querystring = {"format": "json", "code": country_code}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    try:
        # Implementing basic retry logic for stability
        for attempt in range(3):
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data and isinstance(data, list) and len(data) > 0:
                    return "SUCCESS", data[0]
                elif data and isinstance(data, dict) and data.get("message") and "Unauthorized" in data["message"]:
                    return "ERROR", "Invalid API Key or Subscription is not active."
                else:
                    return "ERROR", f"No data found for code '{country_code}' or unexpected response format."
            
            # Handle rate limiting or server errors with backoff
            elif response.status_code in (429, 500, 503) and attempt < 2:
                st.warning(f"API call failed with status {response.status_code}. Retrying in {2**attempt} seconds...")
                import time
                time.sleep(2**attempt)
            else:
                return "ERROR", f"API Request failed with status code: {response.status_code}. Response: {response.text}"
        
        return "ERROR", "Failed to connect to the API after multiple retries."

    except requests.exceptions.RequestException as e:
        return "ERROR", f"Network or connection error: {e}"


# --- Streamlit UI and Logic ---

st.title("🦠 COVID-19 Latest Data Tracker")
st.markdown("Use the dropdown below to select a country and view its most recent reported COVID-19 statistics from the RapidAPI source.")

# Create the country selection box
selected_country_name = st.selectbox(
    "Select a Country",
    options=sorted(list(COUNTRY_CODES.keys())),
    index=0
)

# Get the ISO code for the selected country
selected_code = COUNTRY_CODES.get(selected_country_name, "")

# Button to trigger data fetch
if st.button(f"Get Data for {selected_country_name}", type="primary"):
    if selected_code:
        # Display a spinner while fetching data
        with st.spinner(f"Fetching latest data for {selected_country_name}..."):
            status, result = fetch_country_data(selected_code)

        if status == "SUCCESS":
            # Extract main data fields
            data = result
            
            # Use columns for a clean display of key metrics
            col1, col2, col3 = st.columns(3)
            
            # Format numbers with thousands separator for readability
            def format_number(n):
                return f"{n:,.0f}" if isinstance(n, (int, float)) else "N/A"

            # Use st.metric for large, impactful numbers
            col1.metric("Confirmed Cases", format_number(data.get("confirmed")), help="Total confirmed cases.")
            col2.metric("Deaths", format_number(data.get("deaths")), help="Total confirmed deaths.")
            col3.metric("Recovered", format_number(data.get("recovered")), help="Total recovered cases.")
            
            st.divider()

            st.subheader(f"Detailed Data for {selected_country_name}")
            
            # Prepare data for a table
            display_data = {
                "Metric": ["Confirmed", "Deaths", "Recovered", "Critical", "Last Update"],
                "Value": [
                    format_number(data.get("confirmed")), 
                    format_number(data.get("deaths")), 
                    format_number(data.get("recovered")),
                    format_number(data.get("critical")),
                    data.get("lastChange") or data.get("lastUpdate") or "Date N/A"
                ]
            }
            
            df = pd.DataFrame(display_data)
            # Display the DataFrame as a static table
            st.table(df.set_index('Metric'))
            
            st.caption(f"Data retrieved as of: {data.get('lastUpdate') or 'N/A'}")


        elif status == "ERROR":
            st.error(f"Failed to retrieve data: {result}")
        
    else:
        st.error("Invalid country selection or missing code.")

st.markdown("""
---
*Note: Data reliability is dependent on the source API, which compiles reports from various health organizations.*
""")
