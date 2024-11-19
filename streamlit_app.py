import pandas as pd
import streamlit as st
import altair as alt

# Set page configuration as the first command
st.set_page_config(page_title="Gun Violence Analysis", layout="wide")

# Load the data (adjust paths as needed)
population_data = pd.read_csv("data/Population.csv")
gun_violence_data = pd.read_csv("data/GunViolenceAllYears.csv")
high_shooting_data = pd.read_csv("data/High.csv")
elementary_shooting_data = pd.read_csv("data/Elementary.csv")

# Convert incident dates to datetime
gun_violence_data['Incident Date'] = pd.to_datetime(gun_violence_data['Incident Date']).dt.tz_localize(None)

# 4th chart - Monthly Mass Shootings with Max State vs US Average
# Date range slider (mimicking the same logic from the movie dataset)
years = st.slider(
    "Select Date Range for Mass Shootings (Max State vs US Average)",
    min_value=pd.Timestamp('2021-01-01').date(),
    max_value=pd.Timestamp('2024-01-01').date(),
    value=(pd.Timestamp('2023-01-01').date(), pd.Timestamp('2023-12-31').date()),  # Default range
    format="YYYY-MM-DD"
)

# Filter data based on the selected date range
filtered_data = gun_violence_data[
    (gun_violence_data['Incident Date'].dt.date >= years[0]) &
    (gun_violence_data['Incident Date'].dt.date <= years[1])
]

# Group data by month and state for the filtered data
monthly_data = filtered_data.groupby(['Month', 'State']).size().reset_index(name='Mass Shootings Max')

# Find the state with the most mass shootings each month
max_states = monthly_data.loc[monthly_data.groupby('Month')['Mass Shootings Max'].idxmax()]

# Calculate the average mass shootings per month for the filtered range
avg_gun_violence = monthly_data.groupby('Month')['Mass Shootings Max'].mean().reset_index(name='Mass Shootings Average')

# Create the line chart for the max state vs US average (4th chart)
max_line = alt.Chart(max_states).mark_line(color='red').encode(
    x='Month:T',
    y='Mass Shootings Max:Q',
    tooltip=['Month:T', 'State:N', 'Mass Shootings Max:Q']
)

avg_line = alt.Chart(avg_gun_violence).mark_line(color='darkred').encode(
    x='Month:T',
    y='Mass Shootings Average:Q',
    tooltip=['Month:T', 'Mass Shootings Average:Q']
)

# Combine the two lines into one chart
chart4 = (max_line + avg_line).properties(
    title='Monthly Mass Shootings (Max State vs US Average)',
    width=500,
    height=300
)

# Streamlit Layout
st.title("Gun Violence Analysis Dashboard")

# Add the 4th chart with the date range slider logic
col1, col2 = st.columns(2)

with col1:
    # Display other charts if needed
    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)

with col2:
    # Display 4th chart with the date slider
    st.altair_chart(chart4, use_container_width=True)  # 4th chart with date slider
