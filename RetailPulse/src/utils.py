"""
Utility functions for RetailPulse project
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
import logging
from pathlib import Path
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_data(filepath: str) -> pd.DataFrame:
    """Load data from Excel or CSV file"""
    logger.info(f"Loading data from {filepath}")
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath}")
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def check_data_quality(df: pd.DataFrame) -> Dict:
    """Check data quality metrics"""
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicates': df.duplicated().sum(),
        'data_types': df.dtypes.to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    logger.info(f"Data Quality Report: {quality_report}")
    return quality_report


def handle_missing_values(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
    """Handle missing values in dataframe"""
    logger.info(f"Handling missing values with strategy: {strategy}")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    # Handle numeric columns
    if strategy == 'mean':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    elif strategy == 'median':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif strategy == 'forward_fill':
        df[numeric_cols] = df[numeric_cols].fillna(method='ffill')
    
    # Handle categorical columns
    df[categorical_cols] = df[categorical_cols].fillna('Unknown')
    
    logger.info(f"Remaining missing values: {df.isnull().sum().sum()}")
    return df


def remove_outliers(df: pd.DataFrame, columns: List[str], method: str = 'iqr', threshold: float = 3.0) -> pd.DataFrame:
    """Remove outliers from specified columns"""
    logger.info(f"Removing outliers from {columns} using {method}")
    
    if method == 'iqr':
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    
    elif method == 'zscore':
        from scipy import stats
        z_scores = np.abs(stats.zscore(df[columns].select_dtypes(include=[np.number])))
        df = df[(z_scores < threshold).all(axis=1)]
    
    logger.info(f"Rows after outlier removal: {len(df)}")
    return df


def train_test_split_time_series(df: pd.DataFrame, date_column: str, train_size: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split time series data into train and test sets"""
    logger.info(f"Splitting time series with train_size={train_size}")
    
    df_sorted = df.sort_values(by=date_column)
    split_point = int(len(df_sorted) * train_size)
    
    train_df = df_sorted.iloc[:split_point]
    test_df = df_sorted.iloc[split_point:]
    
    logger.info(f"Train set: {len(train_df)} rows, Test set: {len(test_df)} rows")
    return train_df, test_df


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Calculate common evaluation metrics"""
    from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error, mean_squared_error, r2_score
    
    mape = mean_absolute_percentage_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        'MAPE': round(mape, 4),
        'MAE': round(mae, 4),
        'RMSE': round(rmse, 4),
        'R2': round(r2, 4)
    }
    
    logger.info(f"Metrics: {metrics}")
    return metrics


def save_model(model, filepath: str):
    """Save model to disk"""
    import pickle
    logger.info(f"Saving model to {filepath}")
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)


def load_model(filepath: str):
    """Load model from disk"""
    import pickle
    logger.info(f"Loading model from {filepath}")
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model


def save_config(config: Dict, filepath: str):
    """Save configuration to JSON file"""
    logger.info(f"Saving config to {filepath}")
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4, default=str)


def log_metrics_to_mlflow(metrics: Dict, step: int = 0):
    """Log metrics to MLflow"""
    try:
        import mlflow
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
        logger.info(f"Logged metrics to MLflow: {metrics}")
    except Exception as e:
        logger.warning(f"Could not log to MLflow: {e}")


def log_params_to_mlflow(params: Dict):
    """Log parameters to MLflow"""
    try:
        import mlflow
        for key, value in params.items():
            mlflow.log_param(key, value)
        logger.info(f"Logged parameters to MLflow: {params}")
    except Exception as e:
        logger.warning(f"Could not log to MLflow: {e}")


def create_date_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """Create temporal features from date column"""
    logger.info(f"Creating date features from {date_column}")
    
    df[date_column] = pd.to_datetime(df[date_column])
    df['Year'] = df[date_column].dt.year
    df['Month'] = df[date_column].dt.month
    df['Quarter'] = df[date_column].dt.quarter
    df['DayOfWeek'] = df[date_column].dt.dayofweek
    df['DayOfMonth'] = df[date_column].dt.day
    df['WeekOfYear'] = df[date_column].dt.isocalendar().week
    df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
    
    logger.info("Date features created successfully")
    return df


def aggregate_daily_sales(df: pd.DataFrame, date_col: str, amount_col: str) -> pd.DataFrame:
    """Aggregate sales data to daily level"""
    logger.info("Aggregating sales to daily level")
    
    df[date_col] = pd.to_datetime(df[date_col])
    daily_sales = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
    daily_sales.columns = [date_col, amount_col]
    daily_sales[date_col] = pd.to_datetime(daily_sales[date_col])
    daily_sales = daily_sales.sort_values(date_col)
    
    logger.info(f"Daily aggregated data: {len(daily_sales)} days")
    return daily_sales


def normalize_features(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, Dict]:
    """Normalize features using min-max scaling"""
    from sklearn.preprocessing import MinMaxScaler
    
    logger.info(f"Normalizing features: {columns}")
    scaler = MinMaxScaler()
    
    scaling_params = {}
    for col in columns:
        if col in df.columns:
            df[col] = scaler.fit_transform(df[[col]])
            scaling_params[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max())
            }
    
    return df, scaling_params
