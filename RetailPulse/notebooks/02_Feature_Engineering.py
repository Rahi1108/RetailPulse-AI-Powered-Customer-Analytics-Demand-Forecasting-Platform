"""
RetailPulse: Week 1, Day 2 - Feature Engineering & Data Preparation
RFM Scoring, Rolling Statistics, Time-Series Features, and Stationarity Tests
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging
from scipy import stats
from statsmodels.tsa.stattools import adfuller

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import create_date_features, train_test_split_time_series, normalize_features
from config.config import RANDOM_SEED, TRAIN_TEST_SPLIT
from src.figure_utils import save_figure, save_plotly_figure, FIGURES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"📁 Figures will be saved to: {FIGURES_DIR}")

plt.rcParams['figure.figsize'] = (14, 6)

# ============================================================================
# SECTION 1: RFM ANALYSIS (Recency, Frequency, Monetary)
# ============================================================================

def calculate_rfm_scores(df, reference_date=None):
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for customers
    """
    print("="*80)
    print("SECTION 1: RFM ANALYSIS")
    print("="*80)
    
    if reference_date is None:
        reference_date = df['InvoiceDate'].max()
    
    print(f"\nReference Date for RFM: {reference_date}")
    
    # Calculate RFM using named aggregations
    rfm = df.groupby('CustomerID').agg(
        Recency=('InvoiceDate', lambda x: (reference_date - x.max()).days),
        Frequency=('StockCode', 'count'),
        Monetary=('TotalSales', 'sum')
    ).reset_index()
    
    print(f"\nRFM Summary Statistics:")
    print(rfm[['Recency', 'Frequency', 'Monetary']].describe())
    
    # Create RFM scores (1-5 scale)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, 
                              labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Convert to numeric
    rfm['R_Score'] = rfm['R_Score'].astype(int)
    rfm['F_Score'] = rfm['F_Score'].astype(int)
    rfm['M_Score'] = rfm['M_Score'].astype(int)
    
    # Combined RFM Score
    rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
    
    print(f"\nRFM Segments Distribution:")
    print(f"  - Champions (RFM 15): {len(rfm[rfm['RFM_Score'] >= 13])}")
    print(f"  - Loyal Customers (RFM 12-14): {len(rfm[(rfm['RFM_Score'] >= 12) & (rfm['RFM_Score'] <= 14)])}")
    print(f"  - At Risk (RFM < 6): {len(rfm[rfm['RFM_Score'] < 6])}")
    
    # Visualize RFM
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    axes[0, 0].hist(rfm['Recency'], bins=50, edgecolor='black')
    axes[0, 0].set_title('Recency Distribution (Days)')
    
    axes[0, 1].hist(rfm['Frequency'], bins=50, edgecolor='black')
    axes[0, 1].set_title('Frequency Distribution (Transactions)')
    
    axes[1, 0].hist(rfm['Monetary'], bins=50, edgecolor='black')
    axes[1, 0].set_title('Monetary Distribution (Sales Value)')
    
    axes[1, 1].hist(rfm['RFM_Score'], bins=30, edgecolor='black')
    axes[1, 1].set_title('RFM Score Distribution')
    
    plt.tight_layout()
    plt.show()
    
    return rfm


# ============================================================================
# SECTION 2: TIME-SERIES FEATURES
# ============================================================================

def create_time_series_features(df):
    """
    Create time-series features for demand forecasting
    """
    print("\n" + "="*80)
    print("SECTION 2: TIME-SERIES FEATURES")
    print("="*80)
    
    df = df.sort_values('InvoiceDate')
    
    # Daily aggregation
    daily_data = df.groupby(df['InvoiceDate'].dt.date).agg({
        'TotalSales': 'sum',
        'Quantity': 'sum',
        'StockCode': 'count'
    }).reset_index()
    
    daily_data.columns = ['Date', 'Sales', 'Quantity', 'Transactions']
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    
    print(f"\nDaily Data Shape: {daily_data.shape}")
    print(f"Date Range: {daily_data['Date'].min()} to {daily_data['Date'].max()}")
    
    # Create lagged features
    lags = [1, 7, 30]
    for lag in lags:
        daily_data[f'Sales_Lag{lag}'] = daily_data['Sales'].shift(lag)
        daily_data[f'Quantity_Lag{lag}'] = daily_data['Quantity'].shift(lag)
    
    # Rolling statistics
    windows = [7, 14, 30]
    for window in windows:
        daily_data[f'Sales_MA{window}'] = daily_data['Sales'].rolling(window).mean()
        daily_data[f'Sales_Std{window}'] = daily_data['Sales'].rolling(window).std()
        daily_data[f'Quantity_MA{window}'] = daily_data['Quantity'].rolling(window).mean()
    
    print(f"\nTime-Series Features Created:")
    print(f"  - Lags: {lags}")
    print(f"  - Rolling Windows: {windows}")
    
    # Create temporal features
    daily_data = create_date_features(daily_data, 'Date')
    
    print(f"\nFinal Daily Data Columns: {list(daily_data.columns)}")
    
    return daily_data


# ============================================================================
# SECTION 3: STATIONARITY TESTS
# ============================================================================

def test_stationarity(timeseries, title=''):
    """
    Perform Augmented Dickey-Fuller (ADF) test for stationarity
    """
    print(f"\nADF Test Results for {title}:")
    
    result = adfuller(timeseries.dropna())
    
    print(f'  - ADF Statistic: {result[0]:.6f}')
    print(f'  - p-value: {result[1]:.6f}')
    print(f'  - Critical Values:')
    for key, value in result[4].items():
        print(f'    {key}: {value:.3f}')
    
    if result[1] <= 0.05:
        print(f'  ✓ Series is STATIONARY (reject null hypothesis)')
    else:
        print(f'  ✗ Series is NON-STATIONARY (fail to reject null hypothesis)')
    
    return result[1] <= 0.05


def difference_series(series, order=1):
    """Apply differencing to make series stationary"""
    for _ in range(order):
        series = series.diff().dropna()
    return series


def analyze_stationarity(daily_data):
    """
    Analyze and test stationarity of time series
    """
    print("\n" + "="*80)
    print("SECTION 3: STATIONARITY TESTS & DECOMPOSITION")
    print("="*80)
    
    # Test original series
    is_stationary = test_stationarity(daily_data['Sales'], 'Original Sales Series')
    
    # If not stationary, difference it
    if not is_stationary:
        print("\nApplying first-order differencing...")
        diff_sales = daily_data['Sales'].diff().dropna()
        is_diff_stationary = test_stationarity(diff_sales, 'Differenced Sales Series')
    
    # Visualize original vs differenced
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    axes[0].plot(daily_data['Date'], daily_data['Sales'])
    axes[0].set_title('Original Sales Time Series')
    axes[0].set_ylabel('Sales')
    
    axes[1].plot(daily_data['Date'][1:], diff_sales)
    axes[1].set_title('First-Order Differenced Sales')
    axes[1].set_ylabel('Sales Difference')
    
    # ACF-like plot
    axes[2].plot(daily_data['Sales'].rolling(7).mean(), label='7-day MA', linewidth=2)
    axes[2].plot(daily_data['Sales'].rolling(30).mean(), label='30-day MA', linewidth=2)
    axes[2].plot(daily_data['Sales'], label='Original', alpha=0.3)
    axes[2].set_title('Sales with Moving Averages')
    axes[2].set_ylabel('Sales')
    axes[2].legend()
    
    plt.tight_layout()
    plt.show()
    
    return daily_data


# ============================================================================
# SECTION 4: FEATURE SCALING & NORMALIZATION
# ============================================================================

def prepare_features_for_modeling(daily_data):
    """
    Prepare and scale features for modeling
    """
    print("\n" + "="*80)
    print("SECTION 4: FEATURE SCALING & NORMALIZATION")
    print("="*80)
    
    # Remove rows with NaN (due to lagging and rolling windows)
    daily_data = daily_data.dropna()
    
    print(f"\nDataset shape after removing NaN: {daily_data.shape}")
    
    # Select features for modeling
    feature_cols = [col for col in daily_data.columns 
                   if col not in ['Date', 'Sales', 'Quantity', 'Transactions']]
    
    # Normalize features
    daily_data_scaled, scaling_params = normalize_features(
        daily_data.copy(), feature_cols
    )
    
    print(f"\nFeatures normalized: {len(feature_cols)}")
    print(f"Sample normalized features:\n{daily_data_scaled[feature_cols].head()}")
    
    return daily_data, daily_data_scaled, feature_cols, scaling_params


# ============================================================================
# SECTION 5: TRAIN-TEST SPLIT
# ============================================================================

def prepare_train_test_split(daily_data, date_col='Date'):
    """
    Create train-test split while preserving temporal order
    """
    print("\n" + "="*80)
    print("SECTION 5: TRAIN-TEST SPLIT (TEMPORAL)")
    print("="*80)
    
    train_df, test_df = train_test_split_time_series(
        daily_data, date_col, train_size=TRAIN_TEST_SPLIT
    )
    
    print(f"\nTrain-Test Split (80-20):")
    print(f"  - Train: {len(train_df)} days ({train_df['Date'].min()} to {train_df['Date'].max()})")
    print(f"  - Test: {len(test_df)} days ({test_df['Date'].min()} to {test_df['Date'].max()})")
    
    # Visualize split
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(train_df['Date'], train_df['Sales'], label='Train', linewidth=2)
    ax.plot(test_df['Date'], test_df['Sales'], label='Test', linewidth=2, color='orange')
    ax.axvline(x=train_df['Date'].max(), color='red', linestyle='--', label='Train-Test Split')
    ax.set_title('Train-Test Split of Sales Data')
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales')
    ax.legend()
    plt.tight_layout()
    plt.show()
    
    return train_df, test_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load processed EDA data
    eda_data_path = Path(__file__).parent.parent / "data" / "processed_eda.csv"
    df = pd.read_csv(eda_data_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalSales'] = pd.to_numeric(df['TotalSales'], errors='coerce')
    
    # Remove invalid rows
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
    
    # Calculate RFM
    rfm = calculate_rfm_scores(df)
    
    # Create time-series features
    daily_data = create_time_series_features(df)
    
    # Test stationarity
    daily_data = analyze_stationarity(daily_data)
    
    # Prepare features
    daily_data_raw, daily_data_scaled, feature_cols, scaling_params = prepare_features_for_modeling(daily_data)
    
    # Train-test split
    train_df, test_df = prepare_train_test_split(daily_data_raw)
    
    # Save outputs
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    rfm.to_csv(output_dir / "rfm_scores.csv", index=False)
    daily_data_raw.to_csv(output_dir / "daily_data_raw.csv", index=False)
    daily_data_scaled.to_csv(output_dir / "daily_data_scaled.csv", index=False)
    train_df.to_csv(output_dir / "train_data.csv", index=False)
    test_df.to_csv(output_dir / "test_data.csv", index=False)
    
    print("\n" + "="*80)
    print("✓ Feature Engineering Complete - All Data Saved")
    print("="*80)
