import streamlit as st
import pandas as pd

st.title("👥 Customer Segmentation")

try:
    df = pd.read_csv("data/segmentation.csv")
    st.dataframe(df)

    if "Segment" in df.columns:
        st.bar_chart(df["Segment"].value_counts())
except Exception as e:
    st.error(f"Segmentation file missing: {e}")