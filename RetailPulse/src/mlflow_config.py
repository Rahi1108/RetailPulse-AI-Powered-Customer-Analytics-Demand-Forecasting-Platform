"""
RetailPulse - MLflow Configuration
Model tracking and experiment management setup
"""

import mlflow
from pathlib import Path

def setup_mlflow():
    """Initialize MLflow for experiment tracking"""
    
    # Set tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    # Create experiment
    experiment_name = "RetailPulse"
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
    except:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
    
    mlflow.set_experiment(experiment_name)
    
    return experiment_id


def log_model_metrics(model_name, metrics):
    """Log model metrics to MLflow"""
    
    with mlflow.start_run(run_name=model_name):
        for metric_name, value in metrics.items():
            mlflow.log_metric(metric_name, value)
        
        mlflow.end_run()


def log_model_artifacts(model, artifact_path):
    """Log model artifacts"""
    
    mlflow.log_artifact(artifact_path)


if __name__ == "__main__":
    setup_mlflow()
    print("✓ MLflow configured successfully")
