import streamlit as st
import pandas as pd

st.title("Customer Churn Analysis")

churn = pd.read_csv("data/churn.csv")

st.subheader("Churn Overview")
st.dataframe(churn)