"""
Configuration module for RetailPulse project
Contains all hardcoded parameters and paths
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "retailpulse")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# MLflow Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = "RetailPulse"

# Model Configuration
SEGMENTATION_N_CLUSTERS = 6  # K-Means clusters
CHURN_THRESHOLD = 0.5
DEMAND_FORECAST_DAYS = 30
INVENTORY_SAFETY_STOCK_DAYS = 7

# Time Series Configuration
TRAIN_TEST_SPLIT = 0.8
VALIDATION_SPLIT = 0.1
SEQUENCE_LENGTH = 30  # LSTM sequence length

# Forecasting Model Parameters
PROPHET_SEASONALITY_MODE = "multiplicative"
PROPHET_YEARLY_SEASONALITY = True
PROPHET_WEEKLY_SEASONALITY = True
PROPHET_DAILY_SEASONALITY = False

LSTM_HIDDEN_SIZE = 64
LSTM_NUM_LAYERS = 2
LSTM_DROPOUT = 0.2
LSTM_EPOCHS = 50
LSTM_BATCH_SIZE = 32
LSTM_LEARNING_RATE = 0.001

# Feature Engineering
RFM_RECENCY_WEIGHT = 0.4
RFM_FREQUENCY_WEIGHT = 0.3
RFM_MONETARY_WEIGHT = 0.3

# Performance Targets
TARGET_MAPE = 0.12  # 12% MAPE for demand forecasting
TARGET_AUC_ROC = 0.88  # For churn prediction
TARGET_PROCESSING_TIME = 300  # seconds for daily batch jobs

# Drift Detection
DRIFT_THRESHOLD = 0.3
RETRAINING_FREQUENCY_DAYS = 7

# Feature Importance Threshold
FEATURE_IMPORTANCE_THRESHOLD = 0.01

# Random seed for reproducibility
RANDOM_SEED = 42
