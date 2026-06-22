"""
RetailPulse: Week 2, Days 9-11 - Churn Prediction with XGBoost & SHAP
Customer retention analysis with explainability
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, roc_curve,
    precision_score, recall_score, f1_score, auc
)
from pathlib import Path
import sys
import logging
import warnings

warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import RANDOM_SEED, CHURN_THRESHOLD
from src.figure_utils import save_figure, save_plotly_figure, FIGURES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"📁 Figures will be saved to: {FIGURES_DIR}")

plt.rcParams['figure.figsize'] = (14, 6)

# ============================================================================
# SECTION 1: FEATURE ENGINEERING FOR CHURN PREDICTION
# ============================================================================

def create_churn_features(df, rfm):
    """
    Create features for churn prediction from RFM and transaction data
    """
    print("="*80)
    print("SECTION 1: CHURN PREDICTION FEATURE ENGINEERING")
    print("="*80)
    
    # Merge RFM with customer data
    customer_features = rfm.copy()
    
    # Define churn (customers with high recency = not purchased recently)
    recency_75th = customer_features['Recency'].quantile(0.75)
    customer_features['Churn'] = (customer_features['Recency'] > recency_75th).astype(int)
    
    print(f"\nChurn Definition: Recency > {recency_75th} days")
    print(f"Churn Distribution:")
    print(customer_features['Churn'].value_counts())
    print(f"Churn Rate: {customer_features['Churn'].mean():.2%}")
    
    # Additional features
    customer_features['RFM_Score'] = customer_features['R_Score'] + \
                                     customer_features['F_Score'] + \
                                     customer_features['M_Score']
    
    customer_features['Recency_Normalized'] = customer_features['Recency'] / customer_features['Recency'].max()
    customer_features['Frequency_Normalized'] = customer_features['Frequency'] / customer_features['Frequency'].max()
    customer_features['Monetary_Normalized'] = customer_features['Monetary'] / customer_features['Monetary'].max()
    
    print(f"\nFeatures Created: {customer_features.shape[1]}")
    print(f"Columns: {list(customer_features.columns)}")
    
    return customer_features


# ============================================================================
# SECTION 2: DATA PREPARATION FOR MODELING
# ============================================================================

def prepare_modeling_data(customer_features):
    """
    Prepare data for XGBoost training
    """
    print("\n" + "="*80)
    print("SECTION 2: DATA PREPARATION FOR CHURN MODELING")
    print("="*80)
    
    # Select features
    feature_cols = ['Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score',
                   'RFM_Score', 'Recency_Normalized', 'Frequency_Normalized', 'Monetary_Normalized']
    
    X = customer_features[feature_cols]
    y = customer_features['Churn']
    
    # Check for missing values
    print(f"\nMissing Values:")
    print(X.isnull().sum())
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )
    
    print(f"\nTrain-Test Split:")
    print(f"  - Train: {len(X_train)} samples")
    print(f"  - Test: {len(X_test)} samples")
    print(f"  - Churn Rate (Train): {y_train.mean():.2%}")
    print(f"  - Churn Rate (Test): {y_test.mean():.2%}")
    
    return X_train, X_test, y_train, y_test, feature_cols


# ============================================================================
# SECTION 3: XGBOOST MODEL TRAINING
# ============================================================================

def train_xgboost_model(X_train, X_test, y_train, y_test):
    """
    Train XGBoost classification model for churn prediction
    """
    print("\n" + "="*80)
    print("SECTION 3: XGBOOST CHURN PREDICTION MODEL")
    print("="*80)
    
    # Initialize model
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        max_depth=7,
        learning_rate=0.1,
        n_estimators=200,
        random_state=RANDOM_SEED,
        eval_metric='logloss',
        scale_pos_weight=1  # Adjust for imbalance if needed
    )
    
    # Train model
    print("\nTraining XGBoost model...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Predictions
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    
    # Evaluate
    auc_roc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\nXGBoost Model Evaluation:")
    print(f"  - AUC-ROC: {auc_roc:.4f}")
    print(f"  - Precision: {precision:.4f}")
    print(f"  - Recall: {recall:.4f}")
    print(f"  - F1 Score: {f1:.4f}")
    
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # ROC Curve
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].plot(fpr, tpr, label=f'ROC Curve (AUC={auc_roc:.3f})', linewidth=2)
    axes[0].plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    axes[0].set_xlabel('False Positive Rate')
    axes[0].set_ylabel('True Positive Rate')
    axes[0].set_title('ROC Curve - Churn Prediction')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1], cbar=False)
    axes[1].set_title('Confusion Matrix')
    axes[1].set_ylabel('Actual')
    axes[1].set_xlabel('Predicted')
    
    plt.tight_layout()
    plt.close()
    
    return model, y_pred_proba, y_pred, auc_roc


# ============================================================================
# SECTION 4: SHAP EXPLAINABILITY
# ============================================================================

def explain_model_with_shap(model, X_test, feature_cols):
    """
    Generate SHAP explanations for model predictions
    """
    print("\n" + "="*80)
    print("SECTION 4: MODEL EXPLAINABILITY WITH SHAP")
    print("="*80)
    
    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    print(f"\nSHAP Values Shape: {shap_values.shape}")
    
    # Feature importance from SHAP
    feature_importance = np.abs(shap_values).mean(axis=0)
    feature_importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'SHAP_Importance': feature_importance
    }).sort_values('SHAP_Importance', ascending=False)
    
    print(f"\nFeature Importance (SHAP):")
    print(feature_importance_df)
    
    # Visualizations
    fig = plt.figure(figsize=(14, 10))
    
    # SHAP summary plot
    plt.subplot(2, 2, 1)
    shap.summary_plot(shap_values, X_test, feature_names=feature_cols, show=False)
    
    plt.subplot(2, 2, 2)
    shap.summary_plot(shap_values, X_test, feature_names=feature_cols, plot_type='bar', show=False)
    
    # Top features
    plt.subplot(2, 2, 3)
    top_features = feature_importance_df.head(10)
    plt.barh(top_features['Feature'], top_features['SHAP_Importance'])
    plt.xlabel('SHAP Importance')
    plt.title('Top 10 Features by SHAP Importance')
    plt.gca().invert_yaxis()
    
    # Feature importance comparison
    plt.subplot(2, 2, 4)
    model_importance = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False).head(10)
    plt.barh(model_importance['Feature'], model_importance['Importance'])
    plt.xlabel('XGBoost Importance')
    plt.title('Top 10 Features by XGBoost')
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    plt.close()
    
    return shap_values, feature_importance_df


# ============================================================================
# SECTION 5: CHURN RISK SEGMENTATION
# ============================================================================

def segment_churn_risk(customer_features, y_pred_proba):
    """
    Segment customers by churn risk
    """
    print("\n" + "="*80)
    print("SECTION 5: CHURN RISK SEGMENTATION")
    print("="*80)
    
    # Add churn probability to customer features
    customer_features_risk = customer_features.copy()
    customer_features_risk['Churn_Probability'] = y_pred_proba
    
    # Define risk segments
    customer_features_risk['Risk_Segment'] = pd.cut(
        customer_features_risk['Churn_Probability'],
        bins=[0, 0.2, 0.5, 0.8, 1.0],
        labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk']
    )
    
    print(f"\nChurn Risk Segmentation:")
    print(customer_features_risk['Risk_Segment'].value_counts())
    
    # Risk segment analysis
    risk_analysis = customer_features_risk.groupby('Risk_Segment').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean',
        'Churn_Probability': ['min', 'max', 'mean']
    }).round(2)
    
    print(f"\nRisk Segment Characteristics:")
    print(risk_analysis)
    
    # Visualize
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    axes[0, 0].hist(customer_features_risk['Churn_Probability'], bins=50, edgecolor='black')
    axes[0, 0].set_title('Churn Probability Distribution')
    axes[0, 0].set_xlabel('Churn Probability')
    
    risk_counts = customer_features_risk['Risk_Segment'].value_counts()
    axes[0, 1].bar(risk_counts.index, risk_counts.values, color=['green', 'yellow', 'orange', 'red'])
    axes[0, 1].set_title('Customer Distribution by Risk Segment')
    axes[0, 1].set_ylabel('Number of Customers')
    
    axes[1, 0].scatter(customer_features_risk['Monetary'], 
                      customer_features_risk['Churn_Probability'],
                      c=customer_features_risk['Recency'], cmap='viridis', alpha=0.6)
    axes[1, 0].set_xlabel('Monetary Value')
    axes[1, 0].set_ylabel('Churn Probability')
    axes[1, 0].set_title('Monetary vs Churn Risk')
    
    axes[1, 1].scatter(customer_features_risk['Recency'], 
                      customer_features_risk['Churn_Probability'],
                      c=customer_features_risk['Frequency'], cmap='viridis', alpha=0.6)
    axes[1, 1].set_xlabel('Recency (Days)')
    axes[1, 1].set_ylabel('Churn Probability')
    axes[1, 1].set_title('Recency vs Churn Risk')
    
    plt.tight_layout()
    plt.close()
    
    return customer_features_risk


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load customer segments
    customer_segments = pd.read_csv(Path(__file__).parent.parent / "data" / "customer_segments.csv")
    
    # Create churn features
    churn_data = create_churn_features(customer_segments, customer_segments)
    
    # Prepare data
    X_train, X_test, y_train, y_test, feature_cols = prepare_modeling_data(churn_data)
    
    # Train model
    model, y_pred_proba, y_pred, auc = train_xgboost_model(X_train, X_test, y_train, y_test)
    
    # SHAP explanations
    shap_values, feature_importance = explain_model_with_shap(model, X_test, feature_cols)
    
    # Segment by churn risk - use only test set data with test indices
    churn_data_test = churn_data.loc[X_test.index].reset_index(drop=True)
    churn_risk = segment_churn_risk(churn_data_test, y_pred_proba)
    
    # Save results
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    churn_risk.to_csv(output_dir / "churn_predictions.csv", index=False)
    feature_importance.to_csv(output_dir / "shap_feature_importance.csv", index=False)
    
    # Save model
    model.save_model(str(Path(__file__).parent.parent / "models" / "churn_model.xgb"))
    
    print("\n" + "="*80)
    print("✓ Churn Prediction Model Complete")
    print("="*80)
