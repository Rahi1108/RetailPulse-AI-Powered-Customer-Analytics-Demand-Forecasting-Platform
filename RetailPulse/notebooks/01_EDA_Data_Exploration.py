"""
RetailPulse: Week 1, Days 1-2 - EDA & Data Exploration
Comprehensive Exploratory Data Analysis of Online Retail Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import logging

# Add RetailPulse root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import load_data, check_data_quality, handle_missing_values, create_date_features
from src.figure_utils import save_figure, save_plotly_figure, FIGURES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"📁 Figures will be saved to: {FIGURES_DIR}")

# Set styling
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

# ============================================================================
# SECTION 1: DATA LOADING & INITIAL EXPLORATION
# ============================================================================

def load_retail_data():
    """Load Online Retail datasets"""
    print("="*80)
    print("SECTION 1: DATA LOADING & INITIAL EXPLORATION")
    print("="*80)
    
    data_path_1 = Path(__file__).parent.parent.parent / "Online Retail.xlsx"
    data_path_2 = Path(__file__).parent.parent.parent / "online_retail_II.xlsx"
    
    if data_path_1.exists():
        df1 = load_data(str(data_path_1))
        print(f"\nDataset 1 loaded: {df1.shape}")
    else:
        print(f"Dataset 1 not found at {data_path_1}")
        df1 = None
    
    if data_path_2.exists():
        df2 = load_data(str(data_path_2))
        print(f"Dataset 2 loaded: {df2.shape}")
    else:
        print(f"Dataset 2 not found at {data_path_2}")
        df2 = None
    
    # Combine datasets if both exist
    if df1 is not None and df2 is not None:
        df = pd.concat([df1, df2], ignore_index=True)
        print(f"\nCombined dataset: {df.shape}")
    elif df1 is not None:
        df = df1
    else:
        df = df2
    
    return df


def initial_exploration(df):
    """Perform initial data exploration"""
    print("\n" + "="*80)
    print("BASIC DATASET INFORMATION")
    print("="*80)
    
    print(f"\nDataset Shape: {df.shape}")
    print(f"\nColumn Names & Data Types:")
    print(df.dtypes)
    print(f"\nFirst 5 Rows:")
    print(df.head())
    print(f"\nBasic Statistics:")
    print(df.describe())
    
    # Data Quality Report
    quality_report = check_data_quality(df)
    print(f"\nData Quality Report:")
    print(f"  - Total Rows: {quality_report['total_rows']}")
    print(f"  - Total Columns: {quality_report['total_columns']}")
    print(f"  - Duplicate Rows: {quality_report['duplicates']}")
    print(f"  - Memory Usage: {quality_report['memory_usage_mb']:.2f} MB")
    
    return quality_report


# ============================================================================
# SECTION 2: MISSING VALUES ANALYSIS
# ============================================================================

def analyze_missing_values(df):
    """Analyze and visualize missing values"""
    print("\n" + "="*80)
    print("SECTION 2: MISSING VALUES ANALYSIS")
    print("="*80)
    
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing_Count': missing.values,
        'Missing_Percentage': missing_pct.values
    }).sort_values('Missing_Count', ascending=False)
    
    print("\nMissing Values Summary:")
    print(missing_df[missing_df['Missing_Count'] > 0])
    
    # Visualize missing values
    if missing_df['Missing_Count'].sum() > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        missing_df[missing_df['Missing_Count'] > 0].plot(
            x='Column', y='Missing_Percentage', kind='bar', ax=ax
        )
        ax.set_title('Missing Values Percentage by Column')
        ax.set_ylabel('Missing %')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    return missing_df


# ============================================================================
# SECTION 3: DISTRIBUTION ANALYSIS
# ============================================================================

def analyze_distributions(df):
    """Analyze distributions of key variables"""
    print("\n" + "="*80)
    print("SECTION 3: DISTRIBUTION ANALYSIS")
    print("="*80)
    
    # Convert InvoiceDate to datetime
    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    
    # Numerical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    print(f"\nNumerical Columns: {list(numeric_cols)}")
    
    # Plot distributions
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    if 'Quantity' in df.columns:
        axes[0, 0].hist(df['Quantity'].dropna(), bins=50, edgecolor='black')
        axes[0, 0].set_title('Quantity Distribution')
        axes[0, 0].set_xlabel('Quantity')
    
    if 'UnitPrice' in df.columns:
        axes[0, 1].hist(df['UnitPrice'].dropna(), bins=50, edgecolor='black')
        axes[0, 1].set_title('Unit Price Distribution')
        axes[0, 1].set_xlabel('Unit Price')
    
    # Create Total Sales
    if 'Quantity' in df.columns and 'UnitPrice' in df.columns:
        df['TotalSales'] = df['Quantity'] * df['UnitPrice']
        axes[1, 0].hist(df['TotalSales'].dropna(), bins=50, edgecolor='black')
        axes[1, 0].set_title('Total Sales Distribution')
        axes[1, 0].set_xlabel('Total Sales')
    
    if 'InvoiceDate' in df.columns:
        daily_sales = df.groupby(df['InvoiceDate'].dt.date).agg({
            'TotalSales': 'sum' if 'TotalSales' in df.columns else 'count'
        })
        axes[1, 1].plot(daily_sales.index, daily_sales.iloc[:, 0])
        axes[1, 1].set_title('Daily Sales Trend')
        axes[1, 1].set_xlabel('Date')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return df


# ============================================================================
# SECTION 4: CORRELATION ANALYSIS
# ============================================================================

def analyze_correlations(df):
    """Analyze correlations between variables"""
    print("\n" + "="*80)
    print("SECTION 4: CORRELATION ANALYSIS")
    print("="*80)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        
        print("\nCorrelation Matrix:")
        print(corr_matrix)
        
        # Visualize correlation heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Correlation Heatmap - Numeric Variables')
        plt.tight_layout()
        plt.show()
    
    return corr_matrix if len(numeric_cols) > 1 else None


# ============================================================================
# SECTION 5: CATEGORICAL ANALYSIS
# ============================================================================

def analyze_categorical(df):
    """Analyze categorical variables"""
    print("\n" + "="*80)
    print("SECTION 5: CATEGORICAL ANALYSIS")
    print("="*80)
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    print(f"\nCategorical Columns: {list(categorical_cols)}")
    
    for col in categorical_cols:
        print(f"\n{col}:")
        print(f"  - Unique Values: {df[col].nunique()}")
        print(f"  - Top 10 Values:")
        print(df[col].value_counts().head(10))


# ============================================================================
# SECTION 6: CUSTOMER ANALYSIS
# ============================================================================

def analyze_customers(df):
    """Analyze customer patterns"""
    print("\n" + "="*80)
    print("SECTION 6: CUSTOMER ANALYSIS")
    print("="*80)
    
    if 'CustomerID' in df.columns and 'TotalSales' in df.columns:
        customer_stats = df.groupby('CustomerID').agg({
            'TotalSales': ['sum', 'mean', 'count'],
            'InvoiceDate': ['min', 'max']
        }).round(2)
        
        customer_stats.columns = ['Total_Sales', 'Avg_Sale', 'Transaction_Count', 
                                  'First_Purchase', 'Last_Purchase']
        
        print("\nCustomer Statistics Summary:")
        print(customer_stats.describe())
        
        # Top customers by revenue
        print("\nTop 10 Customers by Revenue:")
        print(customer_stats.nlargest(10, 'Total_Sales')[['Total_Sales', 'Transaction_Count']])
        
        return customer_stats
    return None


# ============================================================================
# SECTION 7: TEMPORAL ANALYSIS
# ============================================================================

def analyze_temporal(df):
    """Analyze temporal patterns"""
    print("\n" + "="*80)
    print("SECTION 7: TEMPORAL ANALYSIS")
    print("="*80)
    
    if 'InvoiceDate' in df.columns:
        df = create_date_features(df, 'InvoiceDate')
        
        print("\nTemporal Features Created:")
        print(f"  - Year Range: {df['Year'].min()} to {df['Year'].max()}")
        print(f"  - Month Distribution:\n{df['Month'].value_counts().sort_index()}")
        print(f"  - Day of Week Distribution:\n{df['DayOfWeek'].value_counts().sort_index()}")
        
        # Monthly sales trend
        monthly_sales = df.groupby(['Year', 'Month']).agg({
            'TotalSales': 'sum',
            'InvoiceDate': 'count'
        }).reset_index()
        
        fig = px.line(monthly_sales, x='Month', y='TotalSales', color='Year',
                     title='Monthly Sales Trend', labels={'TotalSales': 'Total Sales'})
        fig.show()
    
    return df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load data
    df = load_retail_data()
    
    # Perform analyses
    quality_report = initial_exploration(df)
    missing_df = analyze_missing_values(df)
    df = analyze_distributions(df)
    corr_matrix = analyze_correlations(df)
    analyze_categorical(df)
    customer_stats = analyze_customers(df)
    df = analyze_temporal(df)
    
    # Save processed data
    output_path = Path(__file__).parent.parent / "data" / "processed_eda.csv"
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✓ Processed data saved to: {output_path}")
    
    print("\n" + "="*80)
    print("WEEK 1 CHECKPOINT: EDA Complete")
    print("="*80)
