import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_datareader import wb

# Page config with dark theme
st.set_page_config(
    page_title="World Bank Data Explorer", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with better contrast (same as before)
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
st.markdown("<h1 style='color: #4CAF50;'>🌍 World Bank Data Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #B0B0B0;'>Access global development indicators from the World Bank</p>", unsafe_allow_html=True)

# ==============================================
# WORLD BANK INDICATORS (Replacing FAOSTAT domains)
# ==============================================

INDICATORS = {
    "Economy": {
        "GDP (current US$)": "NY.GDP.MKTP.CD",
        "GDP growth (annual %)": "NY.GDP.MKTP.KD.ZG",
        "Inflation, consumer prices (annual %)": "FP.CPI.TOTL.ZG"
    },
    "Population": {
        "Population, total": "SP.POP.TOTL",
        "Population growth (annual %)": "SP.POP.GROW",
        "Life expectancy at birth": "SP.DYN.LE00.IN"
    },
    "Environment": {
        "CO2 emissions (metric tons per capita)": "EN.ATM.CO2E.PC",
        "Forest area (% of land area)": "AG.LND.FRST.ZS",
        "Renewable energy consumption (% of total)": "EG.FEC.RNEW.ZS"
    },
    "Health": {
        "Mortality rate, under-5 (per 1,000 live births)": "SH.DYN.MORT",
        "Physicians (per 1,000 people)": "SH.MED.PHYS.ZS",
        "Hospital beds (per 1,000 people)": "SH.MED.BEDS.ZS"
    },
    "Education": {
        "Literacy rate, adult total (% of people ages 15 and above)": "SE.ADT.LITR.ZS",
        "School enrollment, primary (% gross)": "SE.PRM.ENRR",
        "Government expenditure on education, total (% of GDP)": "SE.XPD.TOTL.GD.ZS"
    }
}

COUNTRIES = {
    "Americas": {"United States": "USA", "Brazil": "BRA", "Canada": "CAN"},
    "Asia": {"China": "CHN", "India": "IND", "Japan": "JPN"},
    "Europe": {"France": "FRA", "Germany": "DEU", "United Kingdom": "GBR"},
    "Africa": {"Nigeria": "NGA", "South Africa": "ZAF", "Egypt": "EGY"}
}

# ==============================================
# UI COMPONENTS (Adjusted for World Bank Data)
# ==============================================

# Sidebar Filters with better contrast
with st.sidebar:
    st.markdown("<h2 style='color: #4CAF50;'>🔍 Filters</h2>", unsafe_allow_html=True)
    
    # Category selection
    selected_category = st.selectbox(
        "1. Select Category", 
        list(INDICATORS.keys()),
        index=0
    )
    
    # Indicator selection based on category
    available_indicators = INDICATORS[selected_category]
    selected_indicator = st.selectbox(
        "2. Select Indicator", 
        list(available_indicators.keys()),
        index=0
    )
    
    # Region selection
    region = st.selectbox(
        "3. Select Region", 
        list(COUNTRIES.keys()),
        index=0
    )
    
    # Country selection
    selected_country = st.selectbox(
        "4. Select Country", 
        list(COUNTRIES[region].keys()),
        index=0
    )
    
    # Year range
    st.markdown("<p style='color: #B0B0B0;'>5. Year Range</p>", unsafe_allow_html=True)
    year_range = st.slider(
        "",
        1960, dt.datetime.now().year,
        (2000, dt.datetime.now().year-1),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='color: #B0B0B0;'>
    <p><strong>About World Bank Data</strong>:<br>
    The World Bank's comprehensive database covering:</p>
    <ul>
        <li>💰 Economic indicators</li>
        <li>👥 Population statistics</li>
        <li>🌳 Environmental data</li>
        <li>🏥 Health metrics</li>
        <li>🎓 Education statistics</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================================
# DATA FETCHING FUNCTION (Updated for World Bank)
# ==============================================

@st.cache_data(ttl=24*3600)
def fetch_wb_data(indicator_name, indicator_code, country_code, start_year, end_year):
    """Fetches data from World Bank API"""
    try:
        # Get data using pandas_datareader
        df = wb.download(
            indicator=indicator_code,
            country=[country_code],
            start=start_year,
            end=end_year
        )
        
        if df.empty:
            st.warning("No data available for the selected parameters")
            return None
            
        # Clean up the dataframe
        df = df.reset_index()
        df = df.rename(columns={
            'year': 'Year',
            indicator_code: 'Value',
            'country': 'Country'
        })
        
        # Add additional metadata
        df['Indicator'] = indicator_name
        df['Country Code'] = country_code
        
        # Get units from World Bank metadata (simplified for demo)
        unit_mapping = {
            "current US$": "US$",
            "annual %": "%",
            "metric tons per capita": "tons/capita",
            "% of land area": "%",
            "% of total": "%",
            "per 1,000 live births": "per 1000",
            "per 1,000 people": "per 1000",
            "% of people ages 15 and above": "%",
            "% gross": "%",
            "% of GDP": "%"
        }
        
        unit = next((v for k, v in unit_mapping.items() if k in indicator_name), "")
        df['Unit'] = unit
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching World Bank data: {str(e)}")
        return None

# ==============================================
# MAIN DISPLAY (Adjusted for World Bank Data)
# ==============================================

# Fetch button with better contrast
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🚀 Fetch Data", use_container_width=True, type="primary"):
        with st.spinner(f"Fetching {selected_indicator} data for {selected_country}..."):
            # Get country code
            country_code = COUNTRIES[region][selected_country]
            indicator_code = INDICATORS[selected_category][selected_indicator]
            
            # Fetch data
            df = fetch_wb_data(
                selected_indicator,
                indicator_code,
                country_code,
                year_range[0],
                year_range[1]
            )
            
            if df is not None:
                st.session_state.wb_data = df
                st.session_state.current_query = {
                    "indicator": selected_indicator,
                    "country": selected_country
                }
                st.success("Data loaded successfully!")

# Display results if data exists
if 'wb_data' in st.session_state:
    df = st.session_state.wb_data
    query = st.session_state.current_query
    
    # Metrics cards with improved styling
    st.markdown("---")
    st.markdown("<h3 style='color: #4CAF50;'>Key Metrics</h3>", unsafe_allow_html=True)
    
    # Filter out NA values for calculations
    clean_df = df.dropna(subset=['Value'])
    
    if not clean_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "First Year Value", 
                f"{clean_df.iloc[0]['Value']:,.2f} {clean_df.iloc[0]['Unit']}",
                help=f"Value in {clean_df.iloc[0]['Year']}"
            )
        with col2:
            st.metric(
                "Last Year Value", 
                f"{clean_df.iloc[-1]['Value']:,.2f} {clean_df.iloc[-1]['Unit']}",
                help=f"Value in {clean_df.iloc[-1]['Year']}"
            )
        with col3:
            change = ((clean_df.iloc[-1]['Value'] - clean_df.iloc[0]['Value']) / clean_df.iloc[0]['Value']) * 100
            st.metric(
                "Change Over Period", 
                f"{change:.1f}%",
                delta_color="inverse" if change < 0 else "normal",
                help=f"Percentage change from {clean_df.iloc[0]['Year']} to {clean_df.iloc[-1]['Year']}"
            )
    else:
        st.warning("No valid data points available for metrics calculation")
    
    # Main dataframe with better contrast
    st.markdown("---")
    st.markdown(f"<h3 style='color: #4CAF50;'>{query['indicator']} in {query['country']}</h3>", unsafe_allow_html=True)
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
        if not clean_df.empty:
            # Set dark background for matplotlib
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Create plot with better contrast
            sns.lineplot(
                data=clean_df, 
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
                f"{query['indicator']} Trend ({query['country']})",
                color='white',
                pad=20,
                fontsize=14
            )
            ax.set_xlabel("Year", color='#B0B0B0')
            ax.set_ylabel(
                f"{query['indicator']} ({clean_df.iloc[0]['Unit']})", 
                color='#B0B0B0'
            )
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No valid data points available for visualization")
    
    with tab2:
        if not clean_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h4 style='color: #4CAF50;'>Descriptive Statistics</h4>", unsafe_allow_html=True)
                stats_df = clean_df["Value"].describe().to_frame().T
                st.dataframe(
                    stats_df.style.format("{:,.2f}"),
                    use_container_width=True
                )
            
            with col2:
                st.markdown("<h4 style='color: #4CAF50;'>Annual Changes</h4>", unsafe_allow_html=True)
                clean_df["YoY Change"] = clean_df["Value"].pct_change() * 100
                yoy_df = clean_df[["Year", "YoY Change"]].dropna()
                st.dataframe(
                    yoy_df.style.format({"YoY Change": "{:+.2f}%"}),
                    use_container_width=True,
                    height=min(400, 35 * (len(yoy_df) + 1))
                )
        else:
            st.warning("No valid data points available for statistical analysis")
    
    # Export options with better contrast
    st.markdown("---")
    st.markdown("<h3 style='color: #4CAF50;'>Export Data</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "💾 Download CSV",
            csv,
            file_name=f"WorldBank_{query['indicator'].replace(' ', '_')}_{query['country']}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        # In a real implementation, this would export the chart
        st.download_button(
            "📊 Download Chart as PNG",
            b"",  # Placeholder for actual implementation
            file_name="WorldBank_chart.png",
            disabled=True,
            use_container_width=True,
            help="Coming soon - will export the visualization as PNG"
        )

# ==============================================
# FOOTER (Updated for World Bank)
# ==============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #B0B0B0; padding: 20px;">
    <p>Data sourced from <a href="https://data.worldbank.org" target="_blank" style="color: #4CAF50;">World Bank Open Data</a></p>
    <p style="font-size: 0.8em;">Note: This app uses the World Bank API via pandas_datareader</p>
</div>
""", unsafe_allow_html=True)