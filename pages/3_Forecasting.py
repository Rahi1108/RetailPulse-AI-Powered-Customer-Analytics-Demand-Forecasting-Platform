import streamlit as st
import pandas as pd

st.title("Demand Forecasting")

fc = pd.read_csv("data/forecast.csv")

st.line_chart(fc.set_index("ds")["yhat"])