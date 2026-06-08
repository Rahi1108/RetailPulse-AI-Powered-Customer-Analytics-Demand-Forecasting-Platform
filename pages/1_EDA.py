import streamlit as st
import pandas as pd

st.title("Exploratory Data Analysis")

df = pd.read_csv("data/cleaned_retail.csv")

st.subheader("Dataset Overview")
st.write(df.head())

st.subheader("Basic Stats")
st.write(df.describe())