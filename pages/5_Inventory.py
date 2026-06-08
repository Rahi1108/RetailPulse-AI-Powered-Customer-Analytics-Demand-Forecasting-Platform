import streamlit as st
import pandas as pd

st.title("Inventory Optimization")

inv = pd.read_csv("data/inventory_recs.csv")

st.subheader("Reorder Suggestions")
st.dataframe(inv)