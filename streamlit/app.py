import streamlit as st
import duckdb
import pandas as pd
import numpy as np

df = duckdb.read_csv('./data/cleansed/national_cataract_data_regions.csv').df()

drop_cols = st.multiselect(label='Select columns to drop from df', options=df.columns)
drop_cols_str = ",".join(f'"{i}"' for i in drop_cols)
df.drop(columns=drop_cols,inplace=True)
st.code(f'df.drop(columns=({drop_cols_str}))')


edited_df = st.data_editor(df, num_rows="dynamic")


group_col = st.selectbox(label='Select a grouping column',options=df.columns)
measure_col = st.selectbox(label='Select a measure column',options=df.columns)
aggregate = st.selectbox(label='Select aggregate for measure',options=('Sum','Avg'))

agg_df = duckdb.sql(f'SELECT {group_col}, {aggregate}({measure_col}) FROM edited_df GROUP BY {group_col} ').df()
st.dataframe(agg_df)
