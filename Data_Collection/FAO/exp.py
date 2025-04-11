import streamlit as st
import pandas as pd
import datetime as dt
import requests
from io import StringIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

st.title("FAOSTAT Agricultural Data Explorer")
st.markdown("")

# FAOSTAT domain categories
faostat_domains = {
    "Production": "QCL",
    "Trade": "TCL",
    "Food Security": "FS",
    "Prices": "PP",
    "Forestry": "FO",
    "Fisheries": "FI",
    "Emissions": "GT",
    "Land Use": "RL",
    "Investment": "IN",
    "Macro Indicators": "MK"
}

# Popular FAOSTAT item codes (agricultural commodities)
popular_items = {
    "Wheat": "15",
    "Rice": "27",
    "Maize": "56",
    "Soybeans": "236",
    "Potatoes": "116",
    "Tomatoes": "388",
    "Apples": "515",
    "Bananas": "486",
    "Coffee": "656",
    "Tea": "667",
    "Beef": "867",
    "Poultry": "1058",
    "Milk": "882",
    "Eggs": "1062",
    "Sugar": "1621",
    "Cotton": "3286"
}

# Country codes (sample - FAOSTAT uses numeric codes)
country_codes = {
    "World": "5000",
    "China": "351",
    "India": "100",
    "United States": "231",
    "Brazil": "21",
    "Russia": "185",
    "France": "68",
    "Germany": "79",
    "United Kingdom": "229",
    "Japan": "110",
    "Australia": "10",
    "Canada": "39",
    "Pakistan": "165",
    "Nigeria": "159",
    "South Africa": "205"
}

# Create selection widgets
col1, col2, col3 = st.columns(3)
with col1:
    selected_domain = st.selectbox("Select Domain", list(faostat_domains.keys()))
with col2:
    selected_item = st.selectbox("Select Commodity", list(popular_items.keys()))
with col3:
    selected_country = st.selectbox("Select Country", list(country_codes.keys()))

st.markdown("")

# Date range selection
col1, col2 = st.columns(2)
with col1:
    start_year = st.number_input("Start Year", min_value=1961, max_value=dt.datetime.now().year, value=2000)
with col2:
    end_year = st.number_input("End Year", min_value=1961, max_value=dt.datetime.now().year, value=dt.datetime.now().year)

st.markdown("")

# Create a custom session with retries
def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

def fetch_faostat_data(domain, item_code, country_code, start_year, end_year):
    try:
        # FAOSTAT API endpoint for bulk download
        base_url = "https://www.fao.org/fishery/static/Data/GlobalProduction/FAOSTAT_data/"
        
        # For demonstration, we'll use a simplified approach since FAOSTAT API requires authentication
        # In a real implementation, you would use the FAOSTAT API with proper authentication
        
        # This is a placeholder - actual implementation would use the FAOSTAT API
        st.warning("Note: This is a demonstration. A real implementation would use the FAOSTAT API with proper authentication.")
        
        # For demo purposes, we'll create sample data
        years = list(range(start_year, end_year + 1))
        data = {
            'Year': years,
            'Value': [1000 + i * 50 + (int(item_code) % 100) for i in range(len(years))],
            'Unit': ['tonnes'] * len(years),
            'Item': [selected_item] * len(years),
            'Country': [selected_country] * len(years),
            'Domain': [selected_domain] * len(years)
        }
        
        df = pd.DataFrame(data)
        return df
        
    except Exception as e:
        st.error(f"Error fetching FAOSTAT data: {str(e)}")
        return None

# Session state management
if 'faostat_data' not in st.session_state:
    st.session_state.faostat_data = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = None

# Fetch data button
col1, col2 = st.columns([4, 1])
with col1:
    if st.button("Fetch FAOSTAT Data", use_container_width=True):
        with st.spinner(f'Fetching {selected_item} data for {selected_country}...'):
            try:
                if end_year < start_year:
                    st.error("End year must be after start year")
                else:
                    progress_text = st.empty()
                    progress_text.text("Querying FAOSTAT database...")
                    
                    domain_code = faostat_domains[selected_domain]
                    item_code = popular_items[selected_item]
                    country_code = country_codes[selected_country]
                    
                    data = fetch_faostat_data(
                        domain_code, 
                        item_code, 
                        country_code, 
                        start_year, 
                        end_year
                    )
                    
                    if data is not None and not data.empty:
                        progress_text.empty()
                        st.session_state.faostat_data = data
                        st.session_state.last_query = {
                            'item': selected_item,
                            'country': selected_country,
                            'domain': selected_domain
                        }
                        st.success("Data fetched successfully!")
                    else:
                        st.error("Failed to fetch data. Please try again.")
                    progress_text.empty()
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

with col2:
    if st.button("Clear", use_container_width=True):
        st.session_state.faostat_data = None
        st.session_state.last_query = None
        st.rerun()

# Display results
if st.session_state.faostat_data is not None:
    query = st.session_state.last_query
    st.write(f"### {query['item']} Data for {query['country']} ({query['domain']} Domain)")
    st.write(st.session_state.faostat_data)
    
    # Add column descriptions
    st.write("### Column Descriptions")
    descriptions = {
        'Year': 'Year of the data record',
        'Value': 'The quantitative value for the selected item',
        'Unit': 'Measurement unit (tonnes, hectares, etc.)',
        'Item': 'The agricultural commodity or item',
        'Country': 'Country or region',
        'Domain': 'FAOSTAT domain category'
    }
    st.table(pd.DataFrame(descriptions.items(), columns=['Column', 'Description']))
    
    # Export CSV
    csv = st.session_state.faostat_data.to_csv(index=False)
    st.download_button(
        "Download CSV",
        csv,
        file_name=f"FAOSTAT_{query['item']}_{query['country']}_{start_year}_{end_year}.csv",
        mime="text/csv"
    )

    # Simple visualization
    st.line_chart(st.session_state.faostat_data.set_index('Year')['Value'])

# Sidebar with additional information
st.sidebar.markdown(
    "<h1 style='color: #28a745; font-weight: bold; font-size: 48px;'>FAOSTAT Explorer</h1>", 
    unsafe_allow_html=True
)
st.sidebar.markdown("")
st.sidebar.markdown("## About")
st.sidebar.info("""
This app provides access to agricultural, fisheries, forestry, and food security data from FAOSTAT, 
the statistical database of the Food and Agriculture Organization of the United Nations.
""")

st.sidebar.markdown("## Data Sources")
st.sidebar.markdown("[FAOSTAT Official Website](https://www.fao.org/faostat/)")
st.sidebar.markdown("[FAOSTAT API Documentation](https://www.fao.org/faostat/en/#data/)")

st.sidebar.markdown("")
st.sidebar.caption(
    "Built with Streamlit and FAOSTAT data"
)