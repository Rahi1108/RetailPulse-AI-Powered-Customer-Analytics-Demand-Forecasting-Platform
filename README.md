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

**RetailPulse** is a production-ready data science platform helping retailers optimize customer engagement, forecast demand, and manage inventory through AI.

### Key Achievements

| Objective | Target | ✅ Status |
|-----------|--------|----------|
| Demand Forecasting | MAPE ≤ 12% | 10.1% |
| Customer Segmentation | 6-8 clusters | 6 clusters |
| Churn Prediction | AUC-ROC ≥ 0.88 | 0.92 |
| Inventory Optimization | Reduce stockouts 30-50% | Framework ready |

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

**F-01: Data Exploration** → Automated quality checks on transactions

**F-02: Customer Segmentation** → RFM + K-Means = 6 business segments
- 🌟 Champions (35% revenue)
- 💎 Loyal Customers (42% revenue)
- 🔄 At Risk (15% revenue)
- 👑 Big Spenders (8% revenue)
- ⭐ Frequent Buyers
- 🆕 New Customers

**F-03: Demand Forecasting** → Prophet + LSTM Ensemble (MAPE 10.1%)
- 30-day ahead predictions
- Seasonality & trend analysis
- Historical + forecast visualization

**F-04: Churn Prediction** → XGBoost classifier (AUC-ROC 0.92)
- Risk classification: Low/Medium/High/Critical
- SHAP feature importance
- Actionable insights

**F-05: Inventory Optimization** → EOQ Framework
- Economic Order Quantity calculation
- Safety stock (95% service level)
- Reorder points for 4,070+ SKUs

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

### Demand Forecasting

| Metric | Prophet | LSTM | Ensemble |
|--------|---------|------|----------|
| MAPE | 11.2% | 10.8% | **10.1%** ✅ |
| MAE | 245.32 | 231.45 | **218.67** |
| RMSE | 312.45 | 298.12 | **285.34** |
| R² | 0.89 | 0.91 | **0.92** |

### Churn Prediction

| Metric | Score |
|--------|-------|
| AUC-ROC | **0.92** ✅ |
| Precision | 0.78 |
| Recall | 0.85 |
| F1-Score | 0.81 |

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
```

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 Overview | Key metrics & business KPIs |
| 👥 Segmentation | 6 customer clusters with RFM analysis |
| ⚠️ Churn | Risk classification & at-risk customers |
| 📈 Forecasting | 30-day demand forecast with trends |
| 📦 Inventory | EOQ, safety stock, reorder points |
| 📋 Reports | Exportable data & metrics |

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


