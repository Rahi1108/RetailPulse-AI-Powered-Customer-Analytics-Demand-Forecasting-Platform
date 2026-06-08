import streamlit as st
import pandas as pd

st.title("📊 Exploratory Data Analysis")

try:
    df = pd.read_csv("data/sales_data.csv")
    st.dataframe(df)

    if "Revenue" in df.columns:
        st.line_chart(df["Revenue"])
except Exception as e:
    st.error(f"EDA file missing: {e}")