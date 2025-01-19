import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from scraper import FrontierScraper
from utils import (
    get_airport_pairs,
    get_tomorrow_date,
    AIRPORTS
)

# Page configuration
st.set_page_config(
    page_title="Frontier GoWild Flight Checker",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'flight_data' not in st.session_state:
    st.session_state.flight_data = None

def update_flight_data():
    """Update flight data and cache it in session state."""
    scraper = FrontierScraper()
    routes = get_airport_pairs()
    date = get_tomorrow_date()
    
    with st.spinner('Fetching latest flight prices...'):
        df = scraper.search_multiple_routes(routes, date)
        if not df.empty:
            st.session_state.flight_data = df
            st.session_state.last_update = datetime.now()
        else:
            st.error("Unable to fetch flight data. Please try again later.")

# App header
st.title("✈️ Frontier GoWild Flight Checker")
st.subheader("Check prices for tomorrow's flights between Chicago and New York area airports")

# Refresh button
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Refresh Data"):
        update_flight_data()

# Show last update time
with col2:
    if st.session_state.last_update:
        st.text(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# Initial data fetch
if st.session_state.flight_data is None:
    update_flight_data()

# Display flight data
if st.session_state.flight_data is not None:
    df = st.session_state.flight_data
    
    # Add full airport names
    df['origin_name'] = df['origin'].map(lambda x: AIRPORTS[x]['name'])
    df['destination_name'] = df['destination'].map(lambda x: AIRPORTS[x]['name'])
    
    # Filters
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_filter = st.multiselect(
            "Origin Airports",
            options=df['origin'].unique(),
            default=df['origin'].unique(),
            format_func=lambda x: f"{x} - {AIRPORTS[x]['name']}"
        )
    
    with col2:
        dest_filter = st.multiselect(
            "Destination Airports",
            options=df['destination'].unique(),
            default=df['destination'].unique(),
            format_func=lambda x: f"{x} - {AIRPORTS[x]['name']}"
        )
    
    # Apply filters
    filtered_df = df[
        df['origin'].isin(origin_filter) &
        df['destination'].isin(dest_filter)
    ]
    
    # Display results
    st.subheader("Available Flights")
    
    # Sort options
    sort_col = st.selectbox(
        "Sort by",
        options=['price', 'departure_time', 'arrival_time'],
        index=0
    )
    filtered_df = filtered_df.sort_values(sort_col)
    
    # Display as table
    st.dataframe(
        filtered_df[[
            'origin', 'origin_name', 'destination', 'destination_name',
            'departure_time', 'arrival_time', 'price', 'available_seats',
            'flight_number'
        ]],
        hide_index=True
    )
    
    # Price visualization
    st.subheader("Price Comparison")
    fig = px.bar(
        filtered_df,
        x='origin',
        y='price',
        color='destination',
        title='Flight Prices by Route',
        labels={'price': 'Price ($)', 'origin': 'Origin Airport', 'destination': 'Destination Airport'}
    )
    st.plotly_chart(fig)
    
    # Statistics
    st.subheader("Quick Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Lowest Price", f"${filtered_df['price'].min():.2f}")
    with col2:
        st.metric("Average Price", f"${filtered_df['price'].mean():.2f}")
    with col3:
        st.metric("Total Flights Found", len(filtered_df))

else:
    st.warning("No flight data available. Please try refreshing.")

# Footer
st.markdown("---")
st.markdown(
    """
    **Note:** Prices and availability are subject to change. This tool scrapes data from 
    Frontier Airlines' website and should be used for informational purposes only.
    """
)
