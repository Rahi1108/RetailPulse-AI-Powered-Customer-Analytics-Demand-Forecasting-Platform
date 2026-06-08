import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="RetailPulse Dashboard", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def load_csv(name):
    path = DATA_DIR / name
    if path.exists():
        return pd.read_csv(path)
    else:
        st.warning(f"Missing file: {name}")
        return pd.DataFrame()

st.title("📊 RetailPulse Dashboard")

menu = st.sidebar.radio("Navigate", [
    "Inventory",
    "Sales",
    "Customers",
    "Forecast",
    "Demand"
])

if menu == "Inventory":
    st.header("Inventory Dashboard")
    df = load_csv("inventory_recs.csv")
    st.dataframe(df)
    if not df.empty:
        st.bar_chart(df.set_index("Product")["Stock"])

elif menu == "Sales":
    st.header("Sales Dashboard")
    df = load_csv("sales_data.csv")
    st.dataframe(df)
    if not df.empty:
        st.line_chart(df.set_index("Date")["Revenue"])

elif menu == "Customers":
    st.header("Customer Segmentation")
    df = load_csv("customer_segments.csv")
    st.dataframe(df)
    if not df.empty:
        st.bar_chart(df.set_index("CustomerID")["SpendingScore"])

elif menu == "Forecast":
    st.header("Forecast")
    df = load_csv("forecast_data.csv")
    st.dataframe(df)
    if not df.empty:
        st.line_chart(df.set_index("Month")["Sales"])

elif menu == "Demand":
    st.header("Demand vs Supply")
    df = load_csv("demand_data.csv")
    st.dataframe(df)
    if not df.empty:
        st.bar_chart(df.set_index("Product"))