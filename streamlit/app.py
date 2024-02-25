import streamlit as st
from streamlit_folium import st_folium, folium_static
import duckdb
import folium
import pandas as pd
# import numpy as np

st.set_page_config(
    page_title="ComMission ImPossible",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': """This is part of NHS Hack Day 2024 at Moorfields! 
http://nhshackday.com 
Looking at tools to help layer and aggregate data over different regions for NHS commissioning"""
    }
)

st.header('ComMission ImPossible')

st.write(f"""This app is being developed as part of NHS Hack Day 2024 @ Moorfields.""")
st.write(f"""The intention of this is to overlay different sets of data relating to cataracts services to point to areas of greatest need of additional services""")

st.write("""
Blue is the NHS regions - funding is distributed by regions
Purple- hospital and their number of surgeries per year
Colours: red, green and orange is the average waiting times (provisional 2022) if red the average times is above 80 days
""")

geolist = pd.read_csv("./exploration/geospatialData.csv")
eye = pd.read_csv("./exploration/national_cataract_data_regions-2.csv")
location = pd.read_csv("./exploration/ons_postcodes_latlong.csv")
regions = pd.read_csv("./exploration/NHS_England_Regions_July_2022_EN_BFC_2022_8847953782386516656.csv")

# st.multiselect(label=)
eye = duckdb.sql('SELECT * FROM eye WHERE lat IS NOT NULL AND long IS NOT NULL').df()
geolist = duckdb.sql("""
SELECT *, 
CASE WHEN WMean_2022 > 80
THEN 'red'
WHEN WMean_2022 >=60 THEN 'orange'
ELSE 'green' END AS color
FROM geolist""").df()

# Your DataFrame 'eye' with 'latitude', 'longitude', 'tooltip_text', and 'popup_text' columns

m = folium.Map(location=[50.8194, -0.118177], zoom_start=12)

# Iterate over DataFrame rows
for index, row in eye.iterrows():
    # Create a Marker for each point in the DataFrame
    folium.Marker(
        location=[row['lat'], row['long']],
        tooltip=row['TrustName'],  # Use the text from the 'tooltip_text' column
        popup=row['NumberHESOperations'],  # Use the text from the 'popup_text' column
        icon=folium.Icon(color="purple"),  # You can change the color or icon as needed
    ).add_to(m)

# Add markers to the map
for index, row in regions.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['NHSER22NM'],  # Show the region name in the popup
        tooltip=row['NHSER22CD']  # Show the region code in the tooltip
    ).add_to(m)  
    
for index, row in geolist.iterrows():
 
    # Create a Marker with the determined color
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['ICB23NM'],  # Show the region name in the popup
        tooltip=row['WMean_2022'],  # Show the value in the tooltip
        icon=folium.Icon(color=row['color'])  # Use the determined color
    ).add_to(m)


st_map = folium_static(m, width=700, height=450)



# importing our CSV of data - most of this script should be fairly generic based on this input
df = duckdb.read_csv('./data/cleansed/national_cataract_data_regions.csv').df()

drop_cols = st.multiselect(label='Select columns to drop from df', options=df.columns)
drop_cols_str = ",".join(f'"{i}"' for i in drop_cols)
df.drop(columns=drop_cols,inplace=True)
st.code(f'df.drop(columns=({drop_cols_str}))')


# showing an example of editable dataframe as a first draft way of seeing how changes would look 
edited_df = st.data_editor(df, num_rows="dynamic")


# sample year slider  
years = ['17-18','18-19','19-20','20-21']
waiting_list_slider = st.select_slider(label='What year of waiting list times do you want to see?',options=years)

# for this map, everything needs to have lat/long
map_df = duckdb.sql('SELECT * FROM edited_df WHERE lat IS NOT NULL').df()

st.map(data=map_df,latitude ='lat',longitude='long')


group_col = st.selectbox(label='Select a grouping column',options=df.columns)
measure_cols = st.multiselect(label='Select a measure column',options=df.columns)

measure_cols_agg = []
for measure in measure_cols:
    measure_str = st.selectbox(label=f'Select aggregate for {measure}',options=('Sum','Avg','Min','Max'), key=measure) + f'({measure})'
    st.write(measure_str)
    measure_cols_agg.append(measure_str)

measure_cols_str = ",".join(measure_cols_agg)
st.write(measure_cols_str)

agg_df = duckdb.sql(f'SELECT {group_col}, {measure_cols_str} FROM edited_df GROUP BY {group_col} ').df()
st.dataframe(agg_df)
