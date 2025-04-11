import streamlit as st
import pandas as pd
import requests
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import eurostat

# Page config with EU-themed colors
st.set_page_config(
    page_title="Eurostat Data Explorer", 
    page_icon="🇪🇺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with EU blue theme
st.markdown("""
<style>
    :root {
        --primary-color: #003399;  /* EU blue */
        --secondary-color: #0055A4;
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
        background-color: #FFCC00 !important;  /* EU yellow */
        color: #000 !important;
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

# Title with EU theme
st.markdown("<h1 style='color: #003399;'>🇪🇺 Eurostat Data Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #B0B0B0;'>Access European statistical data from Eurostat</p>", unsafe_allow_html=True)

# ==============================================
# EUROSTAT DATASETS (Replacing World Bank indicators)
# ==============================================

DATASETS = {
    "Economy": {
        "GDP at market prices": "nama_10_gdp",
        "Unemployment rate": "une_rt_m",
        "Inflation rate (HICP)": "prc_hicp_aind"
    },
    "Population": {
        "Population by age group": "demo_pjangroup",
        "Life expectancy": "demo_mlexpec",
        "Births and deaths": "demo_gind"
    },
    "Environment": {
        "Greenhouse gas emissions": "env_air_gge",
        "Waste generation": "env_wasgen",
        "Renewable energy share": "nrg_ind_ren"
    },
    "Industry": {
        "Industrial production": "sts_inpr_m",
        "Retail trade volume": "sts_trtu_m",
        "Construction production": "sts_copr_m"
    },
    "Social": {
        "Median income": "ilc_di04",
        "At-risk-of-poverty rate": "ilc_li02",
        "Early leavers from education": "edat_lfse_14"
    }
}

# Eurostat country codes (EU27 + EFTA)
COUNTRIES = {
    "Western Europe": {
        "Austria": "AT", "Belgium": "BE", "France": "FR", 
        "Germany": "DE", "Luxembourg": "LU", "Netherlands": "NL"
    },
    "Northern Europe": {
        "Denmark": "DK", "Finland": "FI", "Ireland": "IE",
        "Sweden": "SE", "Estonia": "EE", "Latvia": "LV", "Lithuania": "LT"
    },
    "Southern Europe": {
        "Greece": "EL", "Italy": "IT", "Portugal": "PT",
        "Spain": "ES", "Croatia": "HR", "Cyprus": "CY", "Malta": "MT", "Slovenia": "SI"
    },
    "Eastern Europe": {
        "Bulgaria": "BG", "Czechia": "CZ", "Hungary": "HU",
        "Poland": "PL", "Romania": "RO", "Slovakia": "SK"
    },
    "EFTA Countries": {
        "Iceland": "IS", "Liechtenstein": "LI", "Norway": "NO", "Switzerland": "CH"
    }
}

# ==============================================
# UI COMPONENTS (Adjusted for Eurostat)
# ==============================================

# Sidebar Filters with EU theme
with st.sidebar:
    st.markdown("<h2 style='color: #003399;'>🔍 Filters</h2>", unsafe_allow_html=True)
    
    # Domain selection
    selected_domain = st.selectbox(
        "1. Select Domain", 
        list(DATASETS.keys()),
        index=0
    )
    
    # Dataset selection based on domain
    available_datasets = DATASETS[selected_domain]
    selected_dataset = st.selectbox(
        "2. Select Dataset", 
        list(available_datasets.keys()),
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
        1990, dt.datetime.now().year,
        (2010, dt.datetime.now().year-1),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='color: #B0B0B0;'>
    <p><strong>About Eurostat</strong>:<br>
    The statistical office of the European Union providing data on:</p>
    <ul>
        <li>💰 Economy and finance</li>
        <li>👥 Population and society</li>
        <li>🏭 Industry and services</li>
        <li>🌱 Environment and energy</li>
        <li>📊 Science and technology</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================================
# DATA FETCHING FUNCTION (Eurostat version - FIXED)
# ==============================================

@st.cache_data(ttl=24*3600)
def fetch_eurostat_data(dataset_code, country_code, start_year, end_year):
    """Fetches data from Eurostat API with proper handling of geo\time column"""
    try:
        # Get the dataset
        df = eurostat.get_data_df(dataset_code, flags=False)
        
        if df is None or df.empty:
            st.warning("No data available for the selected parameters")
            return None
            
        # Properly handle the geo\time column (with backslash)
        geo_time_col = [col for col in df.columns if 'geo' in col.lower() and 'time' in col.lower()]
        
        if not geo_time_col:
            st.warning("Could not find geo\\time column in the dataset")
            return None
            
        geo_time_col = geo_time_col[0]  # Get the actual column name
        
        # Filter for the selected country
        country_filter = df[geo_time_col] == country_code
        df = df[country_filter]
        
        if df.empty:
            st.warning(f"No data available for {country_code}")
            return None
            
        # Reshape the data from wide to long format
        id_vars = [geo_time_col]
        value_vars = [col for col in df.columns if col not in id_vars]
        
        df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='period', value_name='value')
        
        # Extract year from period (format may be 2020, 2020Q1, 2020M01, etc.)
        df['year'] = df['period'].str.extract(r'(\d{4})').astype(int)
        
        # Filter by year range
        df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        
        if df.empty:
            st.warning("No data available for the selected year range")
            return None
            
        # Clean up the dataframe
        df = df.rename(columns={
            geo_time_col: 'country',
            'value': 'Value',
            'year': 'Year'
        })
        
        # Add metadata
        df['Country'] = selected_country
        df['Dataset'] = selected_dataset
        
        # Get units from Eurostat metadata
        metadata = eurostat.get_pars(dataset_code)
        unit = metadata.get('unit', {}).get('label', '')
        df['Unit'] = unit
        
        return df[['Year', 'period', 'Country', 'Dataset', 'Value', 'Unit']].sort_values('Year')
    
    except Exception as e:
        st.error(f"Error fetching Eurostat data: {str(e)}")
        return None

# ==============================================
# MAIN DISPLAY (Adjusted for Eurostat)
# ==============================================

# Fetch button with EU theme
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🚀 Fetch Data", use_container_width=True, type="primary"):
        with st.spinner(f"Fetching {selected_dataset} data for {selected_country}..."):
            # Get country code
            country_code = COUNTRIES[region][selected_country]
            dataset_code = DATASETS[selected_domain][selected_dataset]
            
            # Fetch data
            df = fetch_eurostat_data(
                dataset_code,
                country_code,
                year_range[0],
                year_range[1]
            )
            
            if df is not None:
                st.session_state.eurostat_data = df
                st.session_state.current_query = {
                    "dataset": selected_dataset,
                    "country": selected_country
                }
                st.success("Data loaded successfully!")

# Display results if data exists
if 'eurostat_data' in st.session_state:
    df = st.session_state.eurostat_data
    query = st.session_state.current_query
    
    # Metrics cards with EU styling
    st.markdown("---")
    st.markdown("<h3 style='color: #003399;'>Key Metrics</h3>", unsafe_allow_html=True)
    
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
    
    # Main dataframe
    st.markdown("---")
    st.markdown(f"<h3 style='color: #003399;'>{query['dataset']} in {query['country']}</h3>", unsafe_allow_html=True)
    st.dataframe(
        clean_df.style.applymap(lambda x: 'color: #B0B0B0' if isinstance(x, str) else 'color: white'),
        hide_index=True,
        use_container_width=True,
        height=min(400, 35 * (len(clean_df) + 1))
    )
    
    # Visualization tabs with dark theme charts
    st.markdown("---")
    tab1, tab2 = st.tabs(["📈 Time Series Analysis", "📊 Statistical Insights"])
    
    with tab1:
        if not clean_df.empty:
            # Set dark background for matplotlib
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Create plot with EU colors
            sns.lineplot(
                data=clean_df, 
                x="Year", 
                y="Value", 
                marker="o",
                color="#003399",
                linewidth=2.5,
                markersize=8
            )
            
            # Customize plot appearance
            ax.set_facecolor('#1E1E1E')
            ax.grid(color='#2E2E2E', linestyle='--', linewidth=0.5)
            ax.set_title(
                f"{query['dataset']} Trend ({query['country']})",
                color='white',
                pad=20,
                fontsize=14
            )
            ax.set_xlabel("Year", color='#B0B0B0')
            ax.set_ylabel(
                f"{query['dataset']} ({clean_df.iloc[0]['Unit']})", 
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
                st.markdown("<h4 style='color: #003399;'>Descriptive Statistics</h4>", unsafe_allow_html=True)
                stats_df = clean_df["Value"].describe().to_frame().T
                st.dataframe(
                    stats_df.style.format("{:,.2f}"),
                    use_container_width=True
                )
            
            with col2:
                st.markdown("<h4 style='color: #003399;'>Annual Changes</h4>", unsafe_allow_html=True)
                clean_df["YoY Change"] = clean_df["Value"].pct_change() * 100
                yoy_df = clean_df[["Year", "YoY Change"]].dropna()
                st.dataframe(
                    yoy_df.style.format({"YoY Change": "{:+.2f}%"}),
                    use_container_width=True,
                    height=min(400, 35 * (len(yoy_df) + 1))
                )
        else:
            st.warning("No valid data points available for statistical analysis")
    
    # Export options with EU colors
    st.markdown("---")
    st.markdown("<h3 style='color: #003399;'>Export Data</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        csv = clean_df.to_csv(index=False)
        st.download_button(
            "💾 Download CSV",
            csv,
            file_name=f"Eurostat_{query['dataset'].replace(' ', '_')}_{query['country']}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        # In a real implementation, this would export the chart
        st.download_button(
            "📊 Download Chart as PNG",
            b"",  # Placeholder for actual implementation
            file_name="Eurostat_chart.png",
            disabled=True,
            use_container_width=True,
            help="Coming soon - will export the visualization as PNG"
        )

# ==============================================
# FOOTER (Eurostat version)
# ==============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #B0B0B0; padding: 20px;">
    <p>Data sourced from <a href="https://ec.europa.eu/eurostat" target="_blank" style="color: #003399;">Eurostat</a> | 
    Statistical Office of the European Union</p>
    <p style="font-size: 0.8em;">Note: Requires installation of the eurostat Python package</p>
</div>
""", unsafe_allow_html=True)