import streamlit as st
import duckdb
# import pandas as pd
# import numpy as np

df = duckdb.read_csv('./data/cleansed/national_cataract_data_regions.csv').df()

drop_cols = st.multiselect(label='Select columns to drop from df', options=df.columns)
drop_cols_str = ",".join(f'"{i}"' for i in drop_cols)
df.drop(columns=drop_cols,inplace=True)
st.code(f'df.drop(columns=({drop_cols_str}))')


edited_df = st.data_editor(df, num_rows="dynamic")

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