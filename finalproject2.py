"""
Name: Annika S.
CS230: Section CS 230
Data: World Air Quality Index
URL: https://www.kaggle.com/datasets/adityaramachandran27/world-air-quality-index-by-city-and-coordinates

Description:
This program analyzes air quality data by city and time using interactive filters and visualizations.
It includes AQI-based filtering, summary statistics, interactive visualizations, and geolocation mapping.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

# [ST4] Page Configuration
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

# [ST4] Custom CSS styling for dark theme and visible text
st.markdown("""
    <style>
    body, .stApp, .block-container {
        background-color: #1e1e1e;
        color: white;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMarkdown p, .stMarkdown div, .stTextInput, .stSelectbox, .stSlider, .stMultiselect,
    .stDataFrame, .stTable, .css-q8sbsg, .css-1d391kg, .css-ffhzg2, label, span, .stRadio > div {
        color: white !important;
    }
    .stSelectbox, .stSlider, .stMultiselect, .stDataFrame, .stTable {
        background-color: #2f2f2f;
    }
    </style>
""", unsafe_allow_html=True)

# [PY3] Try/Except for file loading
try:
    df = pd.read_csv("air_quality_index.csv", encoding='utf-8')
    df.columns = df.columns.str.strip()
except FileNotFoundError:
    st.error("File not found. Please upload the correct file.")
    st.stop()

# [DA9] Add a new column via mapping
category_to_value = {
    "Good": 25,
    "Moderate": 75,
    "Unhealthy for Sensitive Groups": 125,
    "Unhealthy": 175,
    "Very Unhealthy": 250,
    "Hazardous": 350
}

# [DA1] Clean or manipulate data
if 'PM2.5 AQI Category' not in df.columns:
    st.error("'PM2.5 AQI Category' column is missing.")
    st.stop()

df['Estimated AQI'] = df['PM2.5 AQI Category'].map(category_to_value)
df.dropna(subset=['Estimated AQI'], inplace=True)

# [DA7] Grouping and [PY4] List Comprehension
cities = sorted([city for city in df['City'].unique() if isinstance(city, str) and city.strip() != ''])

# [PY1] Function with parameters and default
# [DA4] Filter data by one condition
# [DA5] Filter data by two or more conditions with AND/OR
def filter_data(df, city=None, threshold=50):
    if city:
        return df[(df['City'] == city) & (df['Estimated AQI'] > threshold)]
    return df[df['Estimated AQI'] > threshold]

# [PY2] Function returning multiple values
def get_summary(df):
    return df['Estimated AQI'].mean(), df['Estimated AQI'].max()

# [PY5] Dictionary access by key
city_stats = {city: df[df['City'] == city]['Estimated AQI'].mean() for city in cities}

# [ST1] Tabs UI
selected_tab = st.radio("Navigation", ["Home", "City View", "AQI Summary", "Map View"])

if selected_tab == "Home":
    st.title("Air Quality Index Explorer")
    st.subheader("Dataset Overview")
    st.markdown("""
        This application presents a visualization of the World Air Quality Index dataset, which combines global pollution data
        with geographic coordinates and city-level information. The dataset includes PM2.5 AQI categories, helping us understand
        the air quality classification across multiple regions. Data was sourced from Kaggle and reflects conditions around the globe.

        Use the tabs above to explore AQI data by city, review summary statistics, or view pollution maps interactively.
    """)

elif selected_tab == "City View":
    st.header("City-Based Air Quality Analysis")

    # [ST2] Only define in City View tab
    selected_city = st.selectbox("Choose a City", cities)
    # [ST1] Only define in City View tab
    aqi_threshold = st.slider("Select Estimated AQI Threshold", 0, 500, 100)

    # [ST3] Multiselect widget
    pollutants = st.multiselect("Select Pollutants to Display", df.columns[3:])

    filtered_df = filter_data(df, selected_city, aqi_threshold)

    # [DA7] Grouped mean
    grouped_df = df.groupby('City')['Estimated AQI'].mean().reset_index()

    # [VIZ3] Display a data table
    st.subheader("Filtered Data Table")
    if filtered_df.empty:
        st.warning("No data matches your filter. Try a different city or lower the AQI threshold.")
    else:
        st.dataframe(filtered_df)

    # [VIZ1] Bar chart of AQI by city
    st.subheader("Average Estimated AQI by City")
    st.bar_chart(grouped_df.set_index('City'))

elif selected_tab == "AQI Summary":
    st.header("Overall AQI Summary and Statistics")
    avg_aqi, max_aqi = get_summary(df)
    st.markdown(f"**Average Estimated AQI:** {avg_aqi:.2f}")
    st.markdown(f"**Max Estimated AQI:** {max_aqi}")

    # [DA3] Find top values
    st.subheader("Top 10 Highest AQI Readings")
    top10_df = df.nlargest(10, 'Estimated AQI')
    st.dataframe(top10_df)

    st.subheader("Moderate AQI Records")
    moderate_df = df[df['PM2.5 AQI Category'] == 'Moderate']
    st.dataframe(moderate_df)

    # Use default threshold and city for fallback
    default_city = cities[0] if cities else None
    default_threshold = 50
    st.subheader("Multi-Filtered AQI (by threshold and city)")
    multi_filter_df = df[(df['Estimated AQI'] > default_threshold) & (df['City'] == default_city)]
    st.dataframe(multi_filter_df)

    # [VIZ2] Pie chart for AQI category distribution
    st.subheader("AQI Category Distribution (Pie Chart)")
    pie_data = df['PM2.5 AQI Category'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', textprops={'color':"white"})
    ax.set_title("Distribution of AQI Categories", color='white')
    fig.patch.set_facecolor('#1e1e1e')
    st.pyplot(fig)

elif selected_tab == "Map View":
    st.header("Geolocation-Based Air Quality Map")
    # [VIZ4] Interactive Map
    if {'lat', 'lng'}.issubset(df.columns):
        map_city = st.selectbox("Select city to view on map", cities)
        map_df = df[df['City'] == map_city]
        st.map(map_df.rename(columns={"lat": "latitude", "lng": "longitude"}))
    else:
        st.warning("Latitude/Longitude data not available in the file.")