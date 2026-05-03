import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Page Configuration
st.set_page_config(page_title="Aviation Crisis BI", layout="wide", initial_sidebar_state="expanded")

# 2. CSS for Light/Dark Mode (Bulletproof visibility)
def apply_theme(theme_choice):
    if theme_choice == "Dark":
        st.markdown("""
            <style>
            .stApp { background-color: #0f1116; color: #f5f5f5; }
            [data-testid="stMetricValue"] { color: #f5f5f5 !important; font-size: 28px !important; font-weight: bold !important; }
            [data-testid="stMetricLabel"] p { color: #a1a1aa !important; font-size: 16px !important; }
            div[data-testid="metric-container"] { background-color: #151922; border: 1px solid #293042; padding: 15px; border-radius: 10px; }
            .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; color: #f5f5f5; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #ffffff; color: #111827; }
            [data-testid="stMetricValue"] { color: #111827 !important; font-size: 28px !important; font-weight: bold !important; }
            [data-testid="stMetricLabel"] p { color: #374151 !important; font-size: 16px !important; }
            div[data-testid="metric-container"] { background-color: #f8fafc; border: 1px solid #e5e7eb; padding: 15px; border-radius: 10px; }
            .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; color: #111827; }
            </style>
            """, unsafe_allow_html=True)

def format_currency(value):
    if value >= 1e9: return f"${value/1e9:.2f}B"
    else: return f"${value/1e6:.1f}M"

# 3. Data Loader
@st.cache_data
def load_data():
    return pd.read_parquet('Airlines_Dashboard_Slim.parquet')

df = load_data()

# 4. Sidebar Controls (Power BI Logic: Empty = Select All)
st.sidebar.header("Dashboard Controls")
theme_choice = st.sidebar.radio("Theme Mode", ["Dark", "Light"])
apply_theme(theme_choice)

st.sidebar.divider()
month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
             7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}

sel_months = st.sidebar.multiselect("Months", options=list(month_map.keys()), default=[], format_func=lambda x: month_map[x], help="Leave empty to select all")
sel_airlines = st.sidebar.multiselect("Airlines", options=sorted(df['AIRLINE_NAME'].unique()), default=[], help="Leave empty to select all")
sel_origins = st.sidebar.multiselect("Origin Airports", options=sorted(df['ORIGIN_AIRPORT_NAME'].unique()), default=[], help="Leave empty to select all")
sel_dests = st.sidebar.multiselect("Destination Airports", options=sorted(df['DEST_AIRPORT_NAME'].unique()), default=[], help="Leave empty to select all")

# Smart Filtering (If list is empty, don't filter)
f_df = df.copy()
if sel_months: f_df = f_df[f_df['MONTH'].isin(sel_months)]
if sel_airlines: f_df = f_df[f_df['AIRLINE_NAME'].isin(sel_airlines)]
if sel_origins: f_df = f_df[f_df['ORIGIN_AIRPORT_NAME'].isin(sel_origins)]
if sel_dests: f_df = f_df[f_df['DEST_AIRPORT_NAME'].isin(sel_dests)]

# 5. Dashboard View
st.title("Aviation Crisis Management Simulation")
st.caption("Strategic Intelligence Dashboard - Operational and Financial Analysis")

if not f_df.empty:
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    total_cancels = int(f_df['CANCELLED'].sum())
    total_diverts = int(f_df['DIVERTED'].sum())
    airline_loss = total_cancels * 50000
    airport_gain = total_diverts * 15000
    
    k1.metric("Total Flights", f"{len(f_df):,}")
    k2.metric("Cancellations", f"{total_cancels:,}")
    k3.metric("Diversions", f"{total_diverts:,}")
    k4.metric("Avg Taxi-Out", f"{f_df['TAXI_OUT'].mean():.1f}m")
    k5.metric("Airline Loss", format_currency(airline_loss))
    k6.metric("Airport Revenue", format_currency(airport_gain))
    
    st.divider()

    tab_fin, tab_ops, tab_map, tab_data = st.tabs(["Financial Analysis", "Operations Analysis", "Crisis Geography", "Detailed Data"])

    with tab_fin:
        c1, c2 = st.columns(2)
        with c1:
            loss = f_df.groupby('AIRLINE_NAME')['CANCELLED'].sum().nlargest(10) * 50000
            st.plotly_chart(px.bar(loss, title="Top 10 Airline Losses", 
                                   template="plotly_dark" if theme_choice=="Dark" else "plotly_white", 
                                   color_discrete_sequence=['#FF4B4B']), use_container_width=True)
        with c2:
            gain = f_df.groupby('DEST_AIRPORT_NAME')['DIVERTED'].sum().nlargest(10) * 15000
            st.plotly_chart(px.bar(gain, title="Top 10 Airport Revenue Gains", 
                                   template="plotly_dark" if theme_choice=="Dark" else "plotly_white", 
                                   color_discrete_sequence=['#00D4FF']), use_container_width=True)

    with tab_ops:
        c3, c4 = st.columns(2)
        with c3:
            reason_map = {'A':'Carrier', 'B':'Weather', 'C':'NAS', 'D':'Security'}
            if 'CANCELLATION_REASON' in f_df.columns:
                reasons = f_df[f_df['CANCELLED']==1]['CANCELLATION_REASON'].map(reason_map).value_counts().reset_index()
                st.plotly_chart(px.pie(reasons, names='CANCELLATION_REASON', values='count', 
                                       title="Primary Reasons for Cancellation",
                                       template="plotly_dark" if theme_choice=="Dark" else "plotly_white"), use_container_width=True)
        
        with c4:
            weather_impact = f_df.groupby('MONTH').agg(Avg_Weather_Delay=('WEATHER_DELAY', 'mean'), Avg_Taxi_Out=('TAXI_OUT', 'mean')).reset_index()
            weather_impact['Month_Name'] = weather_impact['MONTH'].map(month_map)

            fig_weather = make_subplots(specs=[[{"secondary_y": True}]])
            fig_weather.add_trace(go.Scatter(x=weather_impact['Month_Name'], y=weather_impact['Avg_Weather_Delay'], 
                                             name="Avg Weather Delay", line=dict(color='blue', width=4)), secondary_y=False)
            fig_weather.add_trace(go.Scatter(x=weather_impact['Month_Name'], y=weather_impact['Avg_Taxi_Out'], 
                                             name="Avg TAXI_OUT", line=dict(color='red', width=4, dash='dot')), secondary_y=True)
            
            fig_weather.update_layout(title='<b>Weather vs. Taxi-Out Domino Effect</b>', xaxis_title='Month', 
                                      template="plotly_dark" if theme_choice=="Dark" else "plotly_white", hovermode='x unified')
            fig_weather.update_yaxes(title_text="Weather Delay (Mins)", secondary_y=False)
            fig_weather.update_yaxes(title_text="Taxi-Out Time (Mins)", secondary_y=True)
            st.plotly_chart(fig_weather, use_container_width=True)

    with tab_map:
        map_agg = f_df.groupby(['ORIGIN_AIRPORT_NAME', 'ORIGIN_LATITUDE', 'ORIGIN_LONGITUDE']).agg({'CANCELLED':'sum', 'TAXI_OUT':'mean'}).reset_index()
        fig_map = px.scatter_geo(map_agg, lat='ORIGIN_LATITUDE', lon='ORIGIN_LONGITUDE', 
                                 size='CANCELLED', color='TAXI_OUT', hover_name='ORIGIN_AIRPORT_NAME',
                                 scope='usa', template="plotly_dark" if theme_choice=="Dark" else "plotly_white",
                                 color_continuous_scale='YlOrRd', title="Geographical Crisis Hotspots")
        fig_map.update_layout(height=750, margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with tab_data:
        st.dataframe(f_df, use_container_width=True)
else:
    st.error("No data available for the current selection. Try selecting more Airlines or Airports.")