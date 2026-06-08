import streamlit as st
import pandas as pd

st.title("📈 Forecasting")

try:
    df = pd.read_csv("data/forecast.csv")
    st.dataframe(df)

    if "yhat" in df.columns:
        st.line_chart(df["yhat"])
except Exception as e:
    st.error(f"Forecast file missing: {e}")
    