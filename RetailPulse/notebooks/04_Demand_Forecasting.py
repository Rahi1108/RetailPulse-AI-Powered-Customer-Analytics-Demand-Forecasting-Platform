"""
RetailPulse: Week 2, Days 5-8 - Demand Forecasting with Prophet + LSTM Ensemble
Time-series forecasting for inventory optimization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pytorch_lightning as pl
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from pathlib import Path
import sys
import logging
import warnings

warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import calculate_metrics
from config.config import RANDOM_SEED, LSTM_HIDDEN_SIZE, LSTM_NUM_LAYERS, LSTM_EPOCHS
from src.figure_utils import save_figure, save_plotly_figure, FIGURES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"[Figures] Figures will be saved to: {FIGURES_DIR}")

plt.rcParams['figure.figsize'] = (14, 6)
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

# ============================================================================
# SECTION 1: PROPHET BASELINE FORECASTING MODEL
# ============================================================================

def prepare_prophet_data(daily_data):
    """
    Prepare data for Prophet (requires 'ds' and 'y' columns)
    """
    print("="*80)
    print("SECTION 1: PROPHET BASELINE DEMAND FORECASTING")
    print("="*80)
    
    prophet_df = daily_data[['Date', 'Sales']].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    prophet_df = prophet_df.sort_values('ds')
    
    print(f"\nProphet Data Shape: {prophet_df.shape}")
    print(f"Date Range: {prophet_df['ds'].min()} to {prophet_df['ds'].max()}")
    print(f"Sales Statistics:")
    print(prophet_df['y'].describe())
    
    return prophet_df


def train_prophet_model(prophet_df, split_date=None):
    """
    Train Prophet forecasting model
    """
    print("\nTraining Prophet Model...")
    
    # Split data
    if split_date is None:
        split_idx = int(len(prophet_df) * 0.8)
        split_date = prophet_df.iloc[split_idx]['ds']
    
    train_df = prophet_df[prophet_df['ds'] < split_date]
    test_df = prophet_df[prophet_df['ds'] >= split_date]
    
    print(f"Train: {len(train_df)}, Test: {len(test_df)}")
    
    # Initialize and train Prophet
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        interval_width=0.95
    )
    
    model.fit(train_df)
    
    # Make predictions
    future = model.make_future_dataframe(periods=len(test_df))
    forecast = model.predict(future)
    
    # Evaluate on test set
    test_forecast = forecast[forecast['ds'].isin(test_df['ds'])][['ds', 'yhat']].reset_index(drop=True)
    test_forecast = test_forecast.merge(test_df, left_on='ds', right_on='ds')
    
    prophet_metrics = calculate_metrics(test_forecast['y'].values, test_forecast['yhat'].values)
    
    print(f"\nProphet Model Performance:")
    for metric, value in prophet_metrics.items():
        print(f"  - {metric}: {value}")
    
    # Visualize
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    axes[0].plot(train_df['ds'], train_df['y'], label='Train', linewidth=2)
    axes[0].plot(test_df['ds'], test_df['y'], label='Test Actual', linewidth=2)
    axes[0].plot(test_forecast['ds'], test_forecast['yhat'], label='Test Forecast', 
                linewidth=2, linestyle='--')
    axes[0].set_title('Prophet Demand Forecast')
    axes[0].set_ylabel('Sales')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Residuals
    residuals = test_forecast['y'].values - test_forecast['yhat'].values
    axes[1].plot(test_forecast['ds'], residuals, label='Residuals', color='red', alpha=0.6)
    axes[1].axhline(y=0, color='black', linestyle='--')
    axes[1].set_title('Forecast Residuals')
    axes[1].set_ylabel('Residual')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.close()
    
    return model, prophet_metrics, test_forecast


# ============================================================================
# SECTION 2: LSTM NEURAL NETWORK FORECASTING
# ============================================================================

class LSTMForecaster(pl.LightningModule):
    """LSTM-based time-series forecasting model"""
    
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1, learning_rate=0.001):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.learning_rate = learning_rate
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.linear = nn.Linear(hidden_size, output_size)
        self.mse_loss = nn.MSELoss()
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.linear(lstm_out[:, -1, :])
        return predictions
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.mse_loss(y_hat, y)
        self.log('train_loss', loss)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.mse_loss(y_hat, y)
        self.log('val_loss', loss)
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)


def prepare_lstm_data(daily_data, sequence_length=30, train_split=0.8):
    """
    Prepare sequences for LSTM training (aligned with Prophet test set)
    """
    print("\n" + "="*80)
    print("SECTION 2: LSTM NEURAL NETWORK FORECASTING")
    print("="*80)
    
    data = daily_data['Sales'].values.reshape(-1, 1).astype(np.float32)
    
    # Create sequences
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i:i+sequence_length])
        y.append(data[i+sequence_length])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split data to match Prophet test set proportionally
    # Prophet: 275 samples -> 220 train, 55 test (20% test)
    # LSTM: 245 sequences -> ~196 train, ~49 test
    train_size = int(len(X) * train_split)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"\nLSTM Data Shapes:")
    print(f"  - X_train: {X_train.shape}, y_train: {y_train.shape}")
    print(f"  - X_test: {X_test.shape}, y_test: {y_test.shape}")
    
    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train)
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.FloatTensor(y_test)
    
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    return train_loader, test_loader, X_test_tensor, y_test_tensor


def train_lstm_model(train_loader, test_loader, hidden_size=64, num_layers=2, epochs=50):
    """
    Train LSTM forecasting model
    """
    print("\nTraining LSTM Model...")
    
    model = LSTMForecaster(
        input_size=1,
        hidden_size=hidden_size,
        num_layers=num_layers,
        output_size=1,
        learning_rate=0.001
    )
    
    trainer = pl.Trainer(
        max_epochs=epochs,
        enable_progress_bar=True,
        enable_model_summary=False,
        accelerator='auto'
    )
    
    trainer.fit(model, train_loader, test_loader)
    
    return model


def evaluate_lstm_model(model, X_test_tensor, y_test_tensor):
    """
    Evaluate LSTM model performance
    """
    model.eval()
    with torch.no_grad():
        predictions = model(X_test_tensor).numpy().flatten()
        y_test = y_test_tensor.numpy().flatten()
    
    lstm_metrics = calculate_metrics(y_test, predictions)
    
    print(f"\nLSTM Model Performance:")
    for metric, value in lstm_metrics.items():
        print(f"  - {metric}: {value}")
    
    # Visualize
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    axes[0].plot(y_test, label='Actual', linewidth=2)
    axes[0].plot(predictions, label='LSTM Forecast', linewidth=2, linestyle='--')
    axes[0].set_title('LSTM Demand Forecast')
    axes[0].set_ylabel('Sales')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    residuals = y_test - predictions
    axes[1].plot(residuals, label='Residuals', color='red', alpha=0.6)
    axes[1].axhline(y=0, color='black', linestyle='--')
    axes[1].set_title('LSTM Forecast Residuals')
    axes[1].set_ylabel('Residual')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.close()
    
    return lstm_metrics, predictions


# ============================================================================
# SECTION 3: ENSEMBLE FORECASTING
# ============================================================================

def create_ensemble_forecast(prophet_forecast, lstm_predictions, weights=(0.5, 0.5)):
    """
    Combine Prophet and LSTM predictions using weighted ensemble
    """
    print("\n" + "="*80)
    print("SECTION 3: HYBRID ENSEMBLE FORECASTING MODEL")
    print("="*80)
    
    # Align predictions - use the minimum length to ensure both arrays are compatible
    min_len = min(len(prophet_forecast['yhat'].values), len(lstm_predictions))
    prophet_preds = prophet_forecast['yhat'].values[-min_len:]
    lstm_preds_aligned = lstm_predictions[-min_len:]
    
    print(f"\nAligning predictions:")
    print(f"  - Prophet predictions shape: {prophet_preds.shape}")
    print(f"  - LSTM predictions shape: {lstm_preds_aligned.shape}")
    
    # Weighted ensemble
    w_prophet, w_lstm = weights
    ensemble_predictions = (w_prophet * prophet_preds + w_lstm * lstm_preds_aligned)
    
    print(f"\nEnsemble Weights:")
    print(f"  - Prophet: {w_prophet}")
    print(f"  - LSTM: {w_lstm}")
    
    return ensemble_predictions


# ============================================================================
# SECTION 4: PERFORMANCE COMPARISON
# ============================================================================

def compare_models(y_test, prophet_pred, lstm_pred, ensemble_pred):
    """
    Compare all forecasting models
    """
    print("\n" + "="*80)
    print("SECTION 4: MODEL COMPARISON & PERFORMANCE METRICS")
    print("="*80)
    
    prophet_metrics = calculate_metrics(y_test, prophet_pred)
    lstm_metrics = calculate_metrics(y_test, lstm_pred)
    ensemble_metrics = calculate_metrics(y_test, ensemble_pred)
    
    # Create comparison table
    comparison_df = pd.DataFrame({
        'Prophet': prophet_metrics,
        'LSTM': lstm_metrics,
        'Ensemble': ensemble_metrics
    })
    
    print(f"\nModel Comparison:")
    print(comparison_df)
    
    # Visualize
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Predictions comparison
    axes[0].plot(y_test, label='Actual', linewidth=2, marker='o', markersize=4)
    axes[0].plot(prophet_pred, label='Prophet', linewidth=1.5, linestyle='--', alpha=0.7)
    axes[0].plot(lstm_pred, label='LSTM', linewidth=1.5, linestyle='--', alpha=0.7)
    axes[0].plot(ensemble_pred, label='Ensemble', linewidth=2, linestyle='-', alpha=0.8)
    axes[0].set_title('Demand Forecast Comparison')
    axes[0].set_ylabel('Sales')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Metrics comparison
    comparison_df.loc['MAPE'].plot(kind='bar', ax=axes[1], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    axes[1].set_title('MAPE Comparison (Lower is Better)')
    axes[1].set_ylabel('MAPE')
    axes[1].set_xlabel('')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].legend().remove()
    
    plt.tight_layout()
    plt.close()
    
    return comparison_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load daily data
    daily_data = pd.read_csv(Path(__file__).parent.parent / "data" / "daily_data_raw.csv")
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    
    # Prophet forecasting
    prophet_df = prepare_prophet_data(daily_data)
    model_prophet, prophet_metrics, test_forecast = train_prophet_model(prophet_df)
    
    # LSTM forecasting
    train_loader, test_loader, X_test, y_test = prepare_lstm_data(daily_data)
    model_lstm = train_lstm_model(train_loader, test_loader, epochs=LSTM_EPOCHS)
    lstm_metrics, lstm_pred = evaluate_lstm_model(model_lstm, X_test, y_test)
    
    # Ensemble
    ensemble_pred = create_ensemble_forecast(test_forecast, lstm_pred, weights=(0.5, 0.5))
    
    # Compare models - align all predictions to the same length
    min_len = min(len(test_forecast), len(lstm_pred))
    prophet_pred_aligned = test_forecast['yhat'].values[-min_len:]
    lstm_pred_aligned = lstm_pred[-min_len:]
    ensemble_pred_aligned = ensemble_pred[-min_len:]
    y_test_aligned = y_test.numpy().flatten()[-min_len:]
    
    comparison = compare_models(y_test_aligned, prophet_pred_aligned, lstm_pred_aligned, ensemble_pred_aligned)
    
    # Save models
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Try to export to ONNX if available
    try:
        model_lstm.to_onnx(str(models_dir / "lstm_forecaster.onnx"), (X_test,), export_params=True)
        print("✓ LSTM model exported to ONNX format")
    except ModuleNotFoundError:
        print("⚠ ONNX export skipped (onnx package not installed). Install with: pip install onnx")
    
    comparison.to_csv(models_dir / "forecasting_comparison.csv")
    
    print("\n" + "="*80)
    print("✓ Demand Forecasting Models Complete")
    print("="*80)
