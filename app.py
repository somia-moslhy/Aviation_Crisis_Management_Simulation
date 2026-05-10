import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Page Configuration
st.set_page_config(page_title="Aviation Crisis BI", layout="wide", initial_sidebar_state="expanded")

# 2. CSS for Light/Dark Mode (No Emojis, High Visibility)
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

# 4. Sidebar Controls (Removed Destination Airport Filter)
st.sidebar.header("Dashboard Controls")
theme_choice = st.sidebar.radio("Theme Mode", ["Dark", "Light"])
apply_theme(theme_choice)

st.sidebar.divider()
month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
             7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}

sel_months = st.sidebar.multiselect("Months", options=list(month_map.keys()), default=[], format_func=lambda x: month_map[x])
sel_airlines = st.sidebar.multiselect("Airlines", options=sorted(df['AIRLINE_NAME'].unique()), default=[])
sel_origins = st.sidebar.multiselect("Origin Airports", options=sorted(df['ORIGIN_AIRPORT_NAME'].unique()), default=[])

# Filtering Logic (Updated)
f_df = df.copy()

if sel_months: 
    f_df = f_df[f_df['MONTH'].isin(sel_months)].copy()
if sel_airlines: 
    f_df = f_df[f_df['AIRLINE_NAME'].isin(sel_airlines)].copy()
if sel_origins: 
    f_df = f_df[f_df['ORIGIN_AIRPORT_NAME'].isin(sel_origins)].copy()
    
# --- Financial Engineering Logic (Aligned with Notebook) ---
dist_col = f_df['DISTANCE'] if 'DISTANCE' in f_df.columns else 800 
w_delay = f_df['WEATHER_DELAY'].fillna(0) if 'WEATHER_DELAY' in f_df.columns else 0
is_normal = (f_df['CANCELLED'] == 0) & (f_df['DIVERTED'] == 0) & (w_delay == 0)

# UPSCALING LOGIC: 100% of cancellations are here, but only 5% of normal flights.
# To get an accurate % loss, we must weight the revenue of normal flights by 20x.
f_df['Estimated_Revenue'] = np.select(
    [f_df['CANCELLED'] == 1, is_normal],
    [0, dist_col * 25 * 20], 
    default=dist_col * 25
)

premium_airlines = ['American Airlines Inc.', 'Delta Air Lines Inc.', 'United Air Lines Inc.', 'US Airways Inc.', 'Alaska Airlines Inc.']
budget_airlines = ['Spirit Air Lines', 'Frontier Airlines Inc.']

conditions = [
    (f_df['CANCELLED'] == 1) & (f_df['AIRLINE_NAME'].isin(premium_airlines)),
    (f_df['CANCELLED'] == 1) & (f_df['AIRLINE_NAME'].isin(budget_airlines)),
    (f_df['CANCELLED'] == 1) # Standard/Regional
]
choices = [75000, 25000, 50000]
f_df['Cancellation_Penalty'] = np.select(conditions, choices, default=0)

# 5. Dashboard View
st.title("Aviation Crisis Management Simulation")
st.caption("Strategic Intelligence Dashboard - Operational and Financial Analysis")

if not f_df.empty:
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    total_cancels = int(f_df['CANCELLED'].sum())
    total_diverts = int(f_df['DIVERTED'].sum())
    airline_loss = f_df['Cancellation_Penalty'].sum()
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
            loss = f_df.groupby('AIRLINE_NAME')['Cancellation_Penalty'].sum().nlargest(10)
            st.plotly_chart(px.bar(loss, title="Top 10 Airline Losses", 
                       template="plotly_dark" if theme_choice=="Dark" else "plotly_white", 
                       color_discrete_sequence=['#FF4B4B']), 
                use_container_width=True)
        with c2:
            gain = f_df.groupby('DEST_AIRPORT_NAME')['DIVERTED'].sum().nlargest(10) * 15000
            st.plotly_chart(px.bar(gain, title="Top 10 Airport Revenue Gains", 
                                   template="plotly_dark" if theme_choice=="Dark" else "plotly_white", 
                                   color_discrete_sequence=['#00D4FF']), use_container_width=True, key="fin_gain_bar")

        st.divider()
        
        c_trend, c_margin = st.columns(2)
        with c_trend:
            month_trend = f_df.groupby('MONTH')['CANCELLED'].sum().reset_index()
            month_trend['Month_Name'] = month_trend['MONTH'].map(month_map)
            fig_month_fin = px.line(month_trend, x='Month_Name', y='CANCELLED', title="Monthly Financial Impact Trend",
                                    template="plotly_dark" if theme_choice=="Dark" else "plotly_white", markers=True)
            st.plotly_chart(fig_month_fin, use_container_width=True, key="fin_month_line")
            
        with c_margin:
            airline_fin = f_df.groupby('AIRLINE_NAME').agg(
                Total_Revenue=('Estimated_Revenue', 'sum'),
                Total_Penalty=('Cancellation_Penalty', 'sum')
            ).reset_index()
            
            # Aligned exactly with Notebook rounding and calculation
            airline_fin['loss_percentage'] = (airline_fin['Total_Penalty'] / airline_fin['Total_Revenue']).round(4) * 100
            airline_fin = airline_fin.replace([np.inf, -np.inf], np.nan).fillna(0)
            top_airlines_margin = airline_fin.nlargest(10, 'Total_Revenue')
            
            fig_margin = go.Figure()
            fig_margin.add_trace(go.Bar(x=top_airlines_margin['AIRLINE_NAME'], y=top_airlines_margin['Total_Revenue'], 
                                        name='Estimated Revenue', marker_color='#00D4FF' if theme_choice=="Dark" else '#007BFF'))
            fig_margin.add_trace(go.Bar(x=top_airlines_margin['AIRLINE_NAME'], y=top_airlines_margin['Total_Penalty'], 
                                        name='Crisis Loss', marker_color='#FF4B4B'))
            
            # Adding percentage text for the manager
            fig_margin.add_trace(go.Scatter(x=top_airlines_margin['AIRLINE_NAME'], y=top_airlines_margin['Total_Revenue'],
                                            mode='text', text=top_airlines_margin['loss_percentage'].apply(lambda x: f"{x:.2f}% Impact"),
                                            textposition="top center", name="Margin Impact %"))
            
            fig_margin.update_layout(title="<b>The Margin Killer: Estimated Revenue vs Crisis Loss</b>",
                                     barmode='group', template="plotly_dark" if theme_choice=="Dark" else "plotly_white", hovermode='x unified')
            st.plotly_chart(fig_margin, use_container_width=True, key="fin_margin_grouped")

        st.divider()
        # Added the "Real Impact" Chart from the notebook to the dashboard
        st.subheader("Crisis Vulnerability Index")
        impact_df = airline_fin.sort_values(by='loss_percentage', ascending=False).head(15)
        fig_impact = px.bar(impact_df, x='loss_percentage', y='AIRLINE_NAME', orientation='h',
                            title='<b>The Real Impact: Which Airlines Suffered the Most?</b><br><sup>(Penalty as a % of Total Revenue)</sup>',
                            labels={'loss_percentage': '% of Revenue Lost', 'AIRLINE_NAME': 'Airline'},
                            color='loss_percentage', color_continuous_scale='Reds',
                            template="plotly_dark" if theme_choice=="Dark" else "plotly_white")
        fig_impact.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_impact, use_container_width=True, key="fin_impact_bar")

        st.divider()
        # New section: Airport Diversion Windfall
        st.subheader("The Diversion Windfall: Unplanned Airport Revenue")
        c_div_1, c_div_2 = st.columns([1, 2])
        with c_div_1:
            st.info("""
            **The Diversion Logic:** 
            While airlines lose money on cancellations, diversions represent a revenue shift. 
            Each diversion generates an estimated **$15,000** for the receiving airport in landing fees, fuel, and passenger services.
            """)
            st.metric("Total Diversion Windfall", format_currency(airport_gain))
        
        with c_div_2:
            div_trend = f_df.groupby('MONTH')['DIVERTED'].sum().reset_index()
            div_trend['Revenue_Gain'] = div_trend['DIVERTED'] * 15000
            div_trend['Month_Name'] = div_trend['MONTH'].map(month_map)
            fig_div = px.area(div_trend, x='Month_Name', y='Revenue_Gain', 
                             title="Monthly Airport Revenue Influx (Diversions)",
                             template="plotly_dark" if theme_choice=="Dark" else "plotly_white",
                             color_discrete_sequence=['#00D4FF'])
            st.plotly_chart(fig_div, use_container_width=True, key="fin_div_area")

    with tab_ops:
        c3, c4 = st.columns(2)
        with c3:
            reason_map = {'A':'Carrier', 'B':'Weather', 'C':'NAS', 'D':'Security'}
            if 'CANCELLATION_REASON' in f_df.columns:
                reasons = f_df[f_df['CANCELLED']==1]['CANCELLATION_REASON'].map(reason_map).value_counts().reset_index()
                st.plotly_chart(px.pie(reasons, names='CANCELLATION_REASON', values='count', 
                                       title="Primary Reasons for Cancellation",
                                       template="plotly_dark" if theme_choice=="Dark" else "plotly_white"), use_container_width=True, key="ops_reason_pie")
        
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
            st.plotly_chart(fig_weather, use_container_width=True, key="ops_weather_multi")

    with tab_map:
        map_agg = f_df.groupby(['ORIGIN_AIRPORT_NAME', 'ORIGIN_LATITUDE', 'ORIGIN_LONGITUDE']).agg({'CANCELLED':'sum', 'TAXI_OUT':'mean'}).reset_index()
        fig_map = px.scatter_geo(map_agg, lat='ORIGIN_LATITUDE', lon='ORIGIN_LONGITUDE', 
                                 size='CANCELLED', color='TAXI_OUT', hover_name='ORIGIN_AIRPORT_NAME',
                                 scope='usa', template="plotly_dark" if theme_choice=="Dark" else "plotly_white",
                                 color_continuous_scale='YlOrRd', title="Geographical Crisis Hotspots")
        fig_map.update_layout(height=750, margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True, key="map_geo_scatter")

    with tab_data:
        st.dataframe(f_df, use_container_width=True)
else:
    st.error("No data available for the current selection. Try selecting more Airlines or Airports.")