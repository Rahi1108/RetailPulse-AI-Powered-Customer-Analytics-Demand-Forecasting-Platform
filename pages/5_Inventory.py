import streamlit as st
from app import load_csv

st.title("Inventory Dashboard")

df = load_csv("inventory_recs.csv")

st.dataframe(df)

if not df.empty:
    st.bar_chart(df.set_index("Product")["Stock"])