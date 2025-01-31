import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import time

# Configuration
API_URL = "http://127.0.0.1:8000"
UPDATE_INTERVAL = 30  # seconds

def get_metrics(device_id: str):
    """Fetch metrics from API"""
    response = requests.get(f"{API_URL}/metrics/{device_id}")
    if response.status_code == 200:
        return response.json()
    return []

def create_dataframe(metrics):
    """Convert metrics to pandas DataFrame"""
    data = []
    for metric in metrics:
        row = {
            'timestamp': metric['metadata']['timestamp']['iso'],
            'cpu_percent': metric['data']['System']['cpu']['usage_percent'],
            'memory_percent': metric['data']['System']['memory']['usage_percent'],
            'btc_price': metric['data']['BTC']['price_eur'],
            'xrp_price': metric['data']['XRP']['price_eur']
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def main():
    st.title("Metrics Dashboard")
    
    # Sidebar
    st.sidebar.title("Settings")
    device_id = st.sidebar.text_input("Device ID", "Metrics Monitor")
    
    # Main content
    if st.button("Refresh Data") or 'last_update' not in st.session_state:
        metrics = get_metrics(device_id)
        if metrics:
            df = create_dataframe(metrics)
            st.session_state.df = df
            st.session_state.last_update = datetime.now()
            
    # Auto-refresh
    if 'last_update' in st.session_state:
        time_since_update = datetime.now() - st.session_state.last_update
        if time_since_update.seconds >= UPDATE_INTERVAL:
            metrics = get_metrics(device_id)
            if metrics:
                df = create_dataframe(metrics)
                st.session_state.df = df
                st.session_state.last_update = datetime.now()
    
    # Display plots
    if 'df' in st.session_state:
        df = st.session_state.df
        
        # System metrics
        st.subheader("System Metrics")
        fig1 = px.line(df, x='timestamp', y=['cpu_percent', 'memory_percent'],
                      title="CPU and Memory Usage")
        st.plotly_chart(fig1)
        
        # Crypto prices
        st.subheader("Cryptocurrency Prices")
        fig2 = px.line(df, x='timestamp', y=['btc_price', 'xrp_price'],
                      title="BTC and XRP Prices (EUR)")
        st.plotly_chart(fig2)
        
        # Raw data
        if st.checkbox("Show Raw Data"):
            st.dataframe(df)
        
        st.text(f"Last updated: {st.session_state.last_update}")

if __name__ == "__main__":
    main() 