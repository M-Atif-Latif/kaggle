import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

# Page config with dark theme
st.set_page_config(
    page_title="FAOSTAT Explorer", 
    page_icon="🌾", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with better contrast
st.markdown("""
<style>
    :root {
        --primary-color: #4CAF50;
        --secondary-color: #2E7D32;
        --background-color: #121212;
        --surface-color: #1E1E1E;
        --text-color: #FFFFFF;
        --text-secondary: #B0B0B0;
    }
    
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .stSelectbox div, .stTextInput div, .stNumberInput div, .stSlider div {
        background-color: var(--surface-color) !important;
        color: var(--text-color) !important;
    }
    
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {
        color: var(--text-color) !important;
    }
    
    .stButton>button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary-color) !important;
    }
    
    .stDownloadButton>button {
        background-color: #1976D2 !important;
        color: white !important;
    }
    
    .stDataFrame {
        background-color: var(--surface-color) !important;
        color: var(--text-color) !important;
    }
    
    .stMetric {
        background-color: var(--surface-color) !important;
        border-radius: 8px;
        padding: 15px;
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
    }
    
    .stMetric div {
        color: var(--text-color) !important;
        font-size: 24px !important;
    }
    
    .sidebar .sidebar-content {
        background-color: var(--surface-color) !important;
    }
    
    /* Chart background */
    .stPlotlyChart, .stPyplot {
        background-color: var(--surface-color) !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--surface-color) !important;
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--surface-color) !important;
        color: var(--text-secondary) !important;
        padding: 10px 20px !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Title with improved contrast
st.markdown("<h1 style='color: #4CAF50;'>🌾 FAOSTAT Agricultural Data Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #B0B0B0;'>Access global agricultural statistics from the UN Food and Agriculture Organization</p>", unsafe_allow_html=True)

# ==============================================
# FAOSTAT DATA CATALOGUE (Simplified)
# ==============================================

DOMAINS = {
    "Production": {"code": "QCL", "metrics": ["Production", "Yield", "Area Harvested"]},
    "Trade": {"code": "TCL", "metrics": ["Import Quantity", "Export Quantity", "Value"]},
    "Food Security": {"code": "FS", "metrics": ["Food Supply", "Dietary Energy Supply"]},
    "Prices": {"code": "PP", "metrics": ["Producer Price", "Consumer Price"]},
    "Emissions": {"code": "GT", "metrics": ["Emissions", "Carbon Stock"]}
}

COMMODITIES = {
    "Crops": {
        "Wheat": 15, "Rice": 27, "Maize": 56, "Soybeans": 236, 
        "Potatoes": 116, "Tomatoes": 388, "Coffee": 656, "Tea": 667
    },
    "Livestock": {
        "Beef": 867, "Poultry": 1058, "Milk": 882, "Eggs": 1062
    }
}

COUNTRIES = {
    "Americas": {"USA": 231, "Brazil": 21, "Canada": 39},
    "Asia": {"China": 351, "India": 100, "Pakistan": 165},
    "Europe": {"France": 68, "Germany": 79, "Russia": 185},
    "Africa": {"Nigeria": 159, "South Africa": 205}
}

# ==============================================
# UI COMPONENTS (Improved Contrast)
# ==============================================

# Sidebar Filters with better contrast
with st.sidebar:
    st.markdown("<h2 style='color: #4CAF50;'>🔍 Filters</h2>", unsafe_allow_html=True)
    
    # Domain selection
    selected_domain = st.selectbox(
        "1. Select Domain", 
        list(DOMAINS.keys()),
        index=0
    )
    
    # Metric selection based on domain
    available_metrics = DOMAINS[selected_domain]["metrics"]
    selected_metric = st.selectbox(
        "2. Select Metric", 
        available_metrics,
        index=0
    )
    
    # Commodity type selection
    st.markdown("<p style='color: #B0B0B0;'>3. Commodity Type</p>", unsafe_allow_html=True)
    commodity_type = st.radio(
        "",
        list(COMMODITIES.keys()),
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Commodity selection
    selected_commodity = st.selectbox(
        "4. Select Commodity", 
        list(COMMODITIES[commodity_type].keys()),
        index=0
    )
    
    # Region selection
    region = st.selectbox(
        "5. Select Region", 
        list(COUNTRIES.keys()),
        index=0
    )
    
    # Country selection
    selected_country = st.selectbox(
        "6. Select Country", 
        list(COUNTRIES[region].keys()),
        index=0
    )
    
    # Year range
    st.markdown("<p style='color: #B0B0B0;'>7. Year Range</p>", unsafe_allow_html=True)
    year_range = st.slider(
        "",
        1961, dt.datetime.now().year,
        (2000, dt.datetime.now().year-1),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='color: #B0B0B0;'>
    <p><strong>About FAOSTAT</strong>:<br>
    The Food and Agriculture Organization's statistical database covering:</p>
    <ul>
        <li>📈 Agricultural production</li>
        <li>🌍 Trade flows</li>
        <li>🍲 Food security</li>
        <li>🌱 Climate impacts</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================================
# DATA FETCHING FUNCTION (Same as before)
# ==============================================

@st.cache_data(ttl=24*3600)
def fetch_faostat_data(domain, metric, item_code, country_code, start_year, end_year):
    """Simulates FAOSTAT API call with realistic parameters"""
    try:
        # Generate realistic sample data
        years = list(range(start_year, end_year + 1))
        base_value = {
            "Production": 1000000,
            "Yield": 30,
            "Area Harvested": 50000,
            "Import Quantity": 500000,
            "Export Quantity": 300000,
            "Value": 250000000,
            "Food Supply": 2500,
            "Dietary Energy Supply": 3000,
            "Producer Price": 150,
            "Consumer Price": 200,
            "Emissions": 50000,
            "Carbon Stock": 1000000
        }.get(metric, 1000)
        
        # Create realistic trends
        data = {
            "Year": years,
            "Value": [int(base_value * (1 + 0.02*(year - start_year)) * (0.95 + 0.1*(item_code%10)/10)) 
                     for year in years],
            "Unit": {
                "Production": "tonnes",
                "Yield": "hg/ha",
                "Area Harvested": "ha",
                "Import Quantity": "tonnes",
                "Export Quantity": "tonnes",
                "Value": "1000 US$",
                "Food Supply": "kcal/capita/day",
                "Dietary Energy Supply": "kcal/capita/day",
                "Producer Price": "US$/tonne",
                "Consumer Price": "US$/tonne",
                "Emissions": "kt CO2eq",
                "Carbon Stock": "kt C"
            }.get(metric, "units"),
            "Flag": ["Official" if year%2==0 else "Estimated" for year in years],
            "Country": selected_country,
            "Item": selected_commodity,
            "Domain": selected_domain,
            "Metric": metric
        }
        
        df = pd.DataFrame(data)
        return df
    
    except Exception as e:
        st.error(f"Error generating data: {str(e)}")
        return None

# ==============================================
# MAIN DISPLAY (Improved Visual Hierarchy)
# ==============================================

# Fetch button with better contrast
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🚀 Fetch Data", use_container_width=True, type="primary"):
        with st.spinner(f"Fetching {selected_metric} data for {selected_commodity} in {selected_country}..."):
            # Get codes
            domain_code = DOMAINS[selected_domain]["code"]
            item_code = COMMODITIES[commodity_type][selected_commodity]
            country_code = COUNTRIES[region][selected_country]
            
            # Fetch data
            df = fetch_faostat_data(
                domain_code,
                selected_metric,
                item_code,
                country_code,
                year_range[0],
                year_range[1]
            )
            
            if df is not None:
                st.session_state.faostat_data = df
                st.session_state.current_query = {
                    "metric": selected_metric,
                    "commodity": selected_commodity,
                    "country": selected_country
                }
                st.success("Data loaded successfully!")

# Display results if data exists
if 'faostat_data' in st.session_state:
    df = st.session_state.faostat_data
    query = st.session_state.current_query
    
    # Metrics cards with improved styling
    st.markdown("---")
    st.markdown("<h3 style='color: #4CAF50;'>Key Metrics</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "First Year Value", 
            f"{df.iloc[0]['Value']:,} {df.iloc[0]['Unit']}",
            help=f"Value in {year_range[0]}"
        )
    with col2:
        st.metric(
            "Last Year Value", 
            f"{df.iloc[-1]['Value']:,} {df.iloc[-1]['Unit']}",
            help=f"Value in {year_range[1]}"
        )
    with col3:
        change = ((df.iloc[-1]['Value'] - df.iloc[0]['Value']) / df.iloc[0]['Value']) * 100
        st.metric(
            "Change Over Period", 
            f"{change:.1f}%",
            delta_color="inverse" if change < 0 else "normal",
            help=f"Percentage change from {year_range[0]} to {year_range[1]}"
        )
    
    # Main dataframe with better contrast
    st.markdown("---")
    st.markdown(f"<h3 style='color: #4CAF50;'>{query['metric']} of {query['commodity']} in {query['country']}</h3>", unsafe_allow_html=True)
    st.dataframe(
        df.style.applymap(lambda x: 'color: #B0B0B0' if isinstance(x, str) else 'color: white'),
        hide_index=True,
        use_container_width=True,
        height=min(400, 35 * (len(df) + 1))
    )
    
    # Visualization tabs with dark theme charts
    st.markdown("---")
    tab1, tab2 = st.tabs(["📈 Time Series Analysis", "📊 Statistical Insights"])
    
    with tab1:
        # Set dark background for matplotlib
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Create plot with better contrast
        sns.lineplot(
            data=df, 
            x="Year", 
            y="Value", 
            marker="o",
            color="#4CAF50",
            linewidth=2.5,
            markersize=8
        )
        
        # Customize plot appearance
        ax.set_facecolor('#1E1E1E')
        ax.grid(color='#2E2E2E', linestyle='--', linewidth=0.5)
        ax.set_title(
            f"{query['metric']} Trend ({query['country']})",
            color='white',
            pad=20,
            fontsize=14
        )
        ax.set_xlabel("Year", color='#B0B0B0')
        ax.set_ylabel(
            f"{query['metric']} ({df.iloc[0]['Unit']})", 
            color='#B0B0B0'
        )
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4 style='color: #4CAF50;'>Descriptive Statistics</h4>", unsafe_allow_html=True)
            stats_df = df["Value"].describe().to_frame().T
            st.dataframe(
                stats_df.style.format("{:,.2f}"),
                use_container_width=True
            )
        
        with col2:
            st.markdown("<h4 style='color: #4CAF50;'>Annual Changes</h4>", unsafe_allow_html=True)
            df["YoY Change"] = df["Value"].pct_change() * 100
            yoy_df = df[["Year", "YoY Change"]].dropna()
            st.dataframe(
                yoy_df.style.format({"YoY Change": "{:+.2f}%"}),
                use_container_width=True,
                height=min(400, 35 * (len(yoy_df) + 1))
            )
    
    # Export options with better contrast
    st.markdown("---")
    st.markdown("<h3 style='color: #4CAF50;'>Export Data</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "💾 Download CSV",
            csv,
            file_name=f"FAOSTAT_{query['commodity']}_{query['country']}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        # In a real implementation, this would export the chart
        st.download_button(
            "📊 Download Chart as PNG",
            b"",  # Placeholder for actual implementation
            file_name="FAOSTAT_chart.png",
            disabled=True,
            use_container_width=True,
            help="Coming soon - will export the visualization as PNG"
        )

# ==============================================
# FOOTER (Improved Contrast)
# ==============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #B0B0B0; padding: 20px;">
    <p>Data sourced from <a href="https://www.fao.org/faostat" target="_blank" style="color: #4CAF50;">FAOSTAT</a> | 
    UN Food and Agriculture Organization</p>
    <p style="font-size: 0.8em;">Note: This demo uses simulated data. Real implementation requires FAOSTAT API access.</p>
            
</div>
""", unsafe_allow_html=True)