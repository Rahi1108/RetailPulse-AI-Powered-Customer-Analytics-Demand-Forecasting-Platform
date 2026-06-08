import streamlit as st
import pandas as pd

st.title("Customer Segmentation")

seg = pd.read_csv("data/segments.csv")

st.subheader("Segment Counts")
st.bar_chart(seg["Segment"].value_counts())

st.subheader("Segment Table")
st.dataframe(seg)