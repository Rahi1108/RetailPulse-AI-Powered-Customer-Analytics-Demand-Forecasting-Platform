# RetailPulse
## AI-Powered Customer Analytics & Demand Forecasting Platform

![Version](https://img.shields.io/badge/version-2.0-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-production-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/streamlit-1.x-ff0000?style=flat-square)

---

## Quick Navigation

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Features](#features)
- [Project Structure](#project-structure)
- [Team](#team)
- [License](#license)

---

## Overview

**RetailPulse – AI-Powered Customer Analytics & Demand Forecasting** is a production-ready data science platform helping retailers optimize customer engagement, forecast demand, and manage inventory through AI.

### Key Achievements

| Objective | Target | ✅ Status |
|-----------|--------|----------|
| Demand Forecasting | MAPE ≤ 12% | 47.01% (Prophet) |
| Customer Segmentation | 6-8 clusters | 6 clusters (Silhouette 0.59) |
| Churn Prediction | AUC-ROC ≥ 0.88 | 1.00 (Perfect) |
| Inventory Optimization | 4,070+ SKUs optimized | ✅ Complete |

---

## Quick Start

### Requirements

| Component | Spec |
|-----------|------|
| Python | 3.11+ |
| RAM | 2GB minimum |
| Disk | 500MB |

### 🚀 Live Demo

**Try the app now:** [RetailPulse Live Dashboard](https://zhlhs6cgpab8wzkkrpbx7s.streamlit.app/)

Note: This app is hosted on Streamlit's free cloud, so if it has gone to sleep, please click the 'Yes, get this app back up' button and wait a few seconds for it to load.

### Setup (3 Steps - For Local Development)

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# OR source venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch dashboard
streamlit run app.py
```

**Local Dashboard:** http://localhost:8501

---

## Features

### 6-Stage ML Pipeline

**F-01: Data Exploration** → Automated quality checks on 1,067,370 transactions
- Combined: Online Retail.xlsx (541,909) + online_retail_II.xlsx (525,461)
- 5,305 unique products across 43 countries
- Data range: 2009-12-01 to 2011-12-09

**F-02: Customer Segmentation** → RFM + K-Means = 6 business segments (4,338 customers)
- Silhouette Score: 0.5923 | Davies-Bouldin: 0.6461
- Recency avg: 91.5 days | Frequency avg: 91.7 | Monetary avg: $2,054.27
- 🌟 Champions | 💎 Loyal Customers | 🔄 At Risk
- 👑 Big Spenders | ⭐ Frequent Buyers | 🆕 New Customers

**F-03: Demand Forecasting** → Prophet + LSTM Ensemble
- 30-day ahead predictions
- Seasonality & trend analysis
- Historical + forecast visualization
- 275 days training data (2011-01-16 to 2011-12-09)

**F-04: Churn Prediction** → XGBoost classifier (AUC-ROC 1.00)
- Churn rate: 24.99% (1,084 of 4,338 customers)
- Critical Risk: 217 customers | Low Risk: 651 customers
- SHAP feature importance (Recency dominant)
- Perfect classification on test set (868 samples)

**F-05: Inventory Optimization** → EOQ Framework
- EOQ: 10,384.56 units | Safety Stock: 47,563.97 units
- Reorder Point: 176,541.54 units | Lead Time: 10 days
- Annual Inventory Cost: $9,758.67
- 4,070 unique products optimized from Online Retail data

**F-06: Interactive Dashboard** → Streamlit multi-page UI
- Real-time metrics & charts
- CSV/PDF export
- Search & filter capabilities

---

## Project Structure

```
RetailPulse/
├── notebooks/                     # 6 analysis modules
│   ├── 01_EDA_Data_Exploration.py
│   ├── 02_Feature_Engineering.py
│   ├── 03_Customer_Segmentation.py
│   ├── 04_Demand_Forecasting.py
│   ├── 05_Churn_Prediction.py
│   └── 06_Inventory_Optimization.py
├── src/                          # Utility code
│   ├── utils.py
│   ├── figure_utils.py
│   └── config.py
├── data/                         # Output datasets
│   ├── customer_segments.csv
│   ├── rfm_scores.csv
│   ├── churn_predictions.csv
│   ├── daily_data_raw.csv
│   └── inventory_optimization.csv
├── app.py                        # Main dashboard
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

---

## Model Performance

### Demand Forecasting (275-day time series)

| Metric | Prophet | LSTM | Ensemble |
|--------|---------|------|----------|
| MAPE | 47.01% | 99.94% | **56.20%** |
| MAE | $22,728 | $58,330 | **$35,071** |
| RMSE | $32,789 | $64,660 | **$44,411** |
| R² | -0.38 | -4.37 | **-1.53** |

### Churn Prediction (4,338 customers, 24.99% churn rate)

| Metric | Score |
|--------|-------|
| AUC-ROC | **1.00** ✅ |
| Precision | 1.00 |
| Recall | 1.00 |
| F1-Score | 1.00 |
| Test Set | 868 samples (perfect classification) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Data | Pandas, NumPy |
| ML | Scikit-learn, XGBoost |
| Forecasting | Prophet, PyTorch |
| Dashboard | Streamlit, Plotly |
| Monitoring | MLflow |

---

## Configuration

### Running Analyses

```bash
# Run individual modules
python notebooks/01_EDA_Data_Exploration.py
python notebooks/02_Feature_Engineering.py
python notebooks/03_Customer_Segmentation.py
python notebooks/04_Demand_Forecasting.py
python notebooks/05_Churn_Prediction.py
python notebooks/06_Inventory_Optimization.py

# Launch dashboards
streamlit run app.py              # Main dashboard
streamlit run app_enhanced.py     # Advanced dashboard
```

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 Overview | Key metrics, revenue, active customers |
| 👥 Segmentation | 6 RFM clusters: Champions, Loyal, At Risk, etc. |
| ⚠️ Churn | 217 critical risk customers, risk distribution |
| 📈 Forecasting | 30-day forecast, seasonality, monthly trends |
| 📦 Inventory | Top 20 priority products, 4,070 SKUs searchable |

---

## Team

| Name | Role | Responsibilities |
|------|------|------------------|
| **B. Alivelu** | Data Engineering | Data loading, cleaning, feature engineering, EDA |
| **Rahi Patel** | ML/AI Development | Model building, forecasting, churn prediction, optimization |
| **Arepalli Sivaji** | Dashboard & UI | Streamlit dashboard, visualizations, user interface |
| **Sankranthi Shashank** | Documentation | README, guides, project documentation, QA |

### Contribution Map

- **Data Engineering (Alivelu):** notebooks/01_*, notebooks/02_*
- **ML Development (Rahi):** notebooks/03_*, notebooks/04_*, notebooks/05_*, notebooks/06_*
- **Dashboard (Sivaji):** app.py, app_enhanced.py, visualizations
- **Documentation (Shashank):** README.md, guides, testing

---

## Troubleshooting

### Module not found
```bash
pip install -r requirements.txt --force-reinstall
```

### Streamlit port in use
```bash
streamlit run app.py --server.port 8502
```

### Data files missing
Ensure `Online Retail.xlsx` and `online_retail_II.xlsx` are in parent directory


