import streamlit as st
import pandas as pd
import altair as alt

# Load the data
population_data = pd.read_csv("data/Population.csv")
gun_violence_data = pd.read_csv("data/GunViolenceAllYears.csv")
high_shooting_data = pd.read_csv("data/High.csv")
elementary_shooting_data = pd.read_csv("data/Elementary.csv")

# Chart 1: Mass Shootings per Million Residents by State
state_population_data = population_data.rename(columns={'NAME': 'State', 'POPESTIMATE': 'Population'})
filtered_data = gun_violence_data[gun_violence_data['Victims Killed'] + gun_violence_data['Victims Injured'] >= 4]
state_incidents = (
    filtered_data.groupby('State', as_index=False).size().rename(columns={'size': 'Number of Incidents'})
)
merged_data = pd.merge(state_incidents, state_population_data, on="State")
merged_data['Incidents per Million'] = (merged_data['Number of Incidents'] / merged_data['Population']) * 1_000_000
total_incidents = merged_data['Number of Incidents'].sum()
total_population = state_population_data['Population'].sum()
us_average = (total_incidents / total_population) * 1_000_000
average_row = pd.DataFrame({
    'State': ['United States Average'],
    'Number of Incidents': [total_incidents],
    'Population': [total_population],
    'Incidents per Million': [us_average]
})
merged_data = pd.concat([merged_data, average_row], ignore_index=True)

chart1 = alt.Chart(merged_data).mark_bar().encode(
    x=alt.X('Incidents per Million:Q', title='Incidents per Million Residents'),
    y=alt.Y('State:O', sort='-x', title='State'),
    color=alt.Color('Incidents per Million:Q', scale=alt.Scale(range=['#ffcccc', '#800000'])),
    tooltip=['State', 'Number of Incidents', 'Population', 'Incidents per Million']
).properties(
    title='Mass Shootings per Million Residents by State (2021-2024)',
    width=300,
    height=400
)

# Chart 2: Total Mass Shooting and School Shootings per Month
gun_violence_data['Incident Date'] = pd.to_datetime(gun_violence_data['Incident Date']).dt.tz_localize(None)
high_shooting_data['Incident Date'] = pd.to_datetime(high_shooting_data['Incident Date']).dt.tz_localize(None)
elementary_shooting_data['Incident Date'] = pd.to_datetime(elementary_shooting_data['Incident Date']).dt.tz_localize(None)
school_shooting_data = pd.concat([
    high_shooting_data[['Incident Date', 'State']],
    elementary_shooting_data[['Incident Date', 'State']]
])
start_date, end_date = pd.Timestamp('2023-01-01'), pd.Timestamp('2024-09-30')
gun_violence_data = gun_violence_data[(gun_violence_data['Incident Date'] >= start_date) & (gun_violence_data['Incident Date'] <= end_date)]
school_shooting_data = school_shooting_data[(school_shooting_data['Incident Date'] >= start_date) & (school_shooting_data['Incident Date'] <= end_date)]
gun_violence_data['Month'] = gun_violence_data['Incident Date'].dt.to_period('M').dt.to_timestamp()
school_shooting_data['Month'] = school_shooting_data['Incident Date'].dt.to_period('M').dt.to_timestamp()
gun_violence_monthly = gun_violence_data.groupby('Month').size().reset_index(name='Mass Shootings')
school_shooting_monthly = school_shooting_data.groupby('Month').size().reset_index(name='School Shootings')
merged_data = pd.merge(gun_violence_monthly, school_shooting_monthly, on='Month')

chart2 = alt.Chart(merged_data).transform_fold(
    ['Mass Shootings', 'School Shootings'], as_=['Type', 'Count']
).mark_line().encode(
    x='Month:T',
    y='Count:Q',
    color=alt.Color('Type:N', scale=alt.Scale(domain=['Mass Shootings', 'School Shootings'], range=['red', 'blue'])),
    tooltip=['Month:T', 'Count:Q', 'Type:N']
).properties(
    title='Total Mass Shooting and School Shootings per Month (Jan 2023 - Sep 2024)',
    width=500,
    height=300
)

# Chart 3: Total Mass Shootings per Month
gun_violence_monthly = gun_violence_data.groupby('Month').size().reset_index(name='Mass Shootings')

chart3 = alt.Chart(gun_violence_monthly).mark_line(color='red').encode(
    x='Month:T',
    y='Mass Shootings:Q',
    tooltip=['Month:T', 'Mass Shootings:Q']
).properties(
    title='Total Mass Shootings per Month (2021-2024)',
    width=500,
    height=300
)

# Chart 4: Monthly Mass Shootings (Max State vs US Average)
monthly_data = gun_violence_data.groupby(['Month', 'State']).size().reset_index(name='Mass Shootings Max')
max_states = monthly_data.loc[monthly_data.groupby('Month')['Mass Shootings Max'].idxmax()]
avg_gun_violence = monthly_data.groupby('Month')['Mass Shootings Max'].mean().reset_index(name='Mass Shootings Average')

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

chart4 = (max_line + avg_line).properties(
    title='Monthly Mass Shootings (Max State vs US Average)',
    width=500,
    height=300
)

# Streamlit Layout
st.set_page_config(layout="wide")
st.title("Gun Violence Analysis Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.empty()
    st.empty()
    st.empty()
    st.empty()
    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)

with col2:
    st.altair_chart(chart3, use_container_width=True)
    st.altair_chart(chart4, use_container_width=True)
