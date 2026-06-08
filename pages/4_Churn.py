import streamlit as st
import pandas as pd

st.title("🔄 Churn Analysis")

try:
    df = pd.read_csv("data/churn.csv")
    st.dataframe(df)

    if "Churn" in df.columns:
        st.bar_chart(df["Churn"].value_counts())
except Exception as e:
    st.error(f"Churn file missing: {e}")