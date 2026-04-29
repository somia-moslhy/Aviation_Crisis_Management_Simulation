import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# 1. Page Configuration
st.set_page_config(page_title="Aviation Crisis BI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    button[data-baseweb="tab"] p {
        font-size: 24px !format;
        font-weight: bold !important;
        color: white !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 50px;
    }
    div[data-testid="metric-container"] {
        background-color: #111;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading & Coordinate Mapping
@st.cache_data
def fetch_coordinates_with_library(_unique_airports):
    geolocator = Nominatim(user_agent="aviation_dashboard_v3")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    coords = {}
    for airport in _unique_airports:
        location = geocode(f"{airport} Airport, USA")
        if location:
            coords[airport] = (location.latitude, location.longitude)
        else:
            coords[airport] = (np.nan, np.nan)
    return coords

@st.cache_data
def load_data():
    file_name = 'Cleaned_Airlines_Crisis.csv'
    if os.path.exists(file_name):
        cols = ['MONTH', 'ORIGIN_AIRPORT_NAME', 'DEST_AIRPORT_NAME', 'CANCELLED', 'DIVERTED', 'TAXI_OUT', 'WEATHER_DELAY', 'TAXI_IN']
        df = pd.read_csv(file_name, usecols=lambda c: c in cols)
        
        unique_airports = list(df['ORIGIN_AIRPORT_NAME'].dropna().unique())
        coords_dict = fetch_coordinates_with_library(unique_airports)
        
        df['LATITUDE'] = df['ORIGIN_AIRPORT_NAME'].map(lambda x: coords_dict.get(x, (np.nan, np.nan))[0])
        df['LONGITUDE'] = df['ORIGIN_AIRPORT_NAME'].map(lambda x: coords_dict.get(x, (np.nan, np.nan))[1])
        return df
    else:
        st.error("File not found!"); st.stop()

df = load_data()

# 3. Sidebar
st.sidebar.title("BI Controls")
month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
sel_months = st.sidebar.multiselect("Months", options=sorted(df['MONTH'].unique()), default=sorted(df['MONTH'].unique()), format_func=lambda x: month_names.get(x))

avail_origins = sorted(df['ORIGIN_AIRPORT_NAME'].dropna().unique())
sel_origins = st.sidebar.multiselect("Origin Airports", options=avail_origins, default=avail_origins[:5])

avail_dests = sorted(df['DEST_AIRPORT_NAME'].dropna().unique())
sel_dests = st.sidebar.multiselect("Destination Airports", options=avail_dests, default=avail_dests)

f_df = df[(df['MONTH'].isin(sel_months)) & (df['ORIGIN_AIRPORT_NAME'].isin(sel_origins)) & (df['DEST_AIRPORT_NAME'].isin(sel_dests))]

# 4. Header & KPIs
st.title("Aviation Crisis Intelligence Dashboard")
k1, k2, k3, k4 = st.columns(4)
total_cancels = int(f_df['CANCELLED'].sum())
total_diverts = int(f_df['DIVERTED'].sum())

k1.metric("Total Cancellations", f"{total_cancels:,}")
k2.metric("Total Diversions", f"{total_diverts:,}")
k3.metric("Avg Taxi-Out", f"{f_df['TAXI_OUT'].mean():.1f} min")
k4.metric("Airline Loss ($)", f"${(total_cancels * 50000):,.0f}")

st.divider()

# 5. Tabs Layout
tab1, tab2, tab3 = st.tabs(["Financial Analysis", "Operations", "Crisis Map"])

with tab1:
    st.write("### Revenue vs Loss Analysis")
    c1, c2 = st.columns(2)
    loss = f_df.groupby('ORIGIN_AIRPORT_NAME')['CANCELLED'].sum() * 50000
    with c1:
        st.plotly_chart(px.bar(loss.sort_values(ascending=False).head(10), title="Airline Losses", color_discrete_sequence=['#FF4B4B'], template="plotly_dark"), use_container_width=True)
    with c2:
        gain = f_df.groupby('DEST_AIRPORT_NAME')['DIVERTED'].sum() * 15000
        st.plotly_chart(px.bar(gain.sort_values(ascending=False).head(10), title="Airport Gains", color_discrete_sequence=['#00D4FF'], template="plotly_dark"), use_container_width=True)

with tab2:
    st.write("### Bottleneck & Weather Domino")
    c3, c4 = st.columns(2)
    with c3:
        taxi = f_df.groupby('ORIGIN_AIRPORT_NAME')['TAXI_IN'].mean().sort_values(ascending=False).head(10)
        st.plotly_chart(px.bar(taxi, orientation='h', title="Top 10 Taxi-In Delay", color_discrete_sequence=['#00D4FF'], template="plotly_dark"), use_container_width=True)
    with c4:
        weather = f_df.groupby('MONTH').agg({'WEATHER_DELAY':'mean', 'TAXI_OUT':'mean'}).reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=weather['MONTH'], y=weather['WEATHER_DELAY'], name="Weather Delay"), secondary_y=False)
        fig.add_trace(go.Scatter(x=weather['MONTH'], y=weather['TAXI_OUT'], name="Taxi-Out", line=dict(dash='dot')), secondary_y=True)
        fig.update_layout(title="Weather Domino Effect", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.write("### Geographic Crisis Explorer")
    
    map_data = f_df.dropna(subset=['LATITUDE', 'LONGITUDE']).groupby(['ORIGIN_AIRPORT_NAME', 'LATITUDE', 'LONGITUDE']).agg({'CANCELLED':'sum', 'TAXI_OUT':'mean'}).reset_index()
    if not map_data.empty:
        fig_map = px.scatter_geo(map_data, lat='LATITUDE', lon='LONGITUDE', size='CANCELLED', color='TAXI_OUT', 
                                 hover_name='ORIGIN_AIRPORT_NAME', scope='usa', template="plotly_dark",
                                 color_continuous_scale='YlOrRd')
        fig_map.update_layout(height=700, margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True) 
    
    c5, c6 = st.columns(2)
    with c5:
        # Pie Chart
        impact_df = pd.DataFrame({'Status': ['Cancelled', 'Diverted'], 'Count': [total_cancels, total_diverts]})
        st.plotly_chart(px.pie(impact_df, names='Status', values='Count', title="Disruption Breakdown", template="plotly_dark"), use_container_width=True)
    with c6:
        # Radar
        radar = f_df.groupby('ORIGIN_AIRPORT_NAME').agg({'CANCELLED':'sum', 'TAXI_OUT':'mean', 'MONTH':'count'}).reset_index()
        st.plotly_chart(px.scatter(radar, x='TAXI_OUT', y='CANCELLED', size='MONTH', color='CANCELLED', title="Danger Zone Radar", template="plotly_dark"), use_container_width=True)
