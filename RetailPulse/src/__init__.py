"""
RetailPulse - AI-Powered Customer Analytics & Demand Forecasting Platform

This package contains all utilities and configurations for the RetailPulse project.
"""

__version__ = "2.0"
__author__ = "Zidio Development"
__description__ = "End-to-End Data Science Platform for Retail Analytics"

from config.config import *
from src.utils import *

__all__ = [
    'load_data',
    'check_data_quality',
    'handle_missing_values',
    'remove_outliers',
    'train_test_split_time_series',
    'calculate_metrics',
    'create_date_features',
    'aggregate_daily_sales',
    'normalize_features'
]
