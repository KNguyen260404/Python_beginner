#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Data Science Platform
-----------------------------
A comprehensive data science platform that implements:
- Automated machine learning (AutoML)
- Advanced statistical analysis
- Time series forecasting
- Deep learning model training
- Feature engineering automation
- Model interpretability and explainability
- A/B testing framework
- Real-time data processing
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
import json
import pickle
import time
import argparse
from pathlib import Path

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder # type: ignore
from sklearn.feature_selection import SelectKBest, RFE, RFECV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Deep Learning
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.utils import plot_model

# Time Series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

# Statistical Analysis
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu

# Feature Engineering
from sklearn.decomposition import PCA, ICA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE

# Model Interpretability
import shap
from lime import lime_tabular

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Types of machine learning models"""
    CLASSIFICATION = auto()
    REGRESSION = auto()
    CLUSTERING = auto()
    TIME_SERIES = auto()
    DEEP_LEARNING = auto()

class FeatureType(Enum):
    """Types of features"""
    NUMERICAL = auto()
    CATEGORICAL = auto()
    TEXT = auto()
    DATETIME = auto()
    BOOLEAN = auto()

@dataclass
class DatasetInfo:
    """Information about a dataset"""
    name: str
    shape: Tuple[int, int]
    features: Dict[str, FeatureType]
    target_column: Optional[str] = None
    missing_values: Dict[str, int] = field(default_factory=dict)
    data_types: Dict[str, str] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelResult:
    """Result of model training and evaluation"""
    model_name: str
    model_type: ModelType
    model: Any
    metrics: Dict[str, float]
    training_time: float
    feature_importance: Optional[Dict[str, float]] = None
    predictions: Optional[np.ndarray] = None
    cross_val_scores: Optional[List[float]] = None

class DataPreprocessor:
    """Advanced data preprocessing and feature engineering"""
    
    def __init__(self):
        """Initialize the data preprocessor"""
        self.scalers = {}
        self.encoders = {}
        self.feature_selectors = {}
        self.preprocessing_steps = []
    
    def analyze_dataset(self, df: pd.DataFrame, target_column: str = None) -> DatasetInfo:
        """Analyze a dataset and return comprehensive information
        
        Args:
            df: Input dataframe
            target_column: Name of the target column
            
        Returns:
            Dataset information
        """
        # Detect feature types
        features = {}
        for col in df.columns:
            if col == target_column:
                continue
                
            if df[col].dtype in ['int64', 'float64']:
                features[col] = FeatureType.NUMERICAL
            elif df[col].dtype == 'object':
                # Check if it's datetime
                try:
                    pd.to_datetime(df[col].head())
                    features[col] = FeatureType.DATETIME
                except:
                    # Check if it's boolean-like
                    unique_vals = df[col].unique()
                    if len(unique_vals) == 2 and all(str(v).lower() in ['true', 'false', '1', '0', 'yes', 'no'] for v in unique_vals):
                        features[col] = FeatureType.BOOLEAN
                    else:
                        features[col] = FeatureType.CATEGORICAL
            elif df[col].dtype == 'bool':
                features[col] = FeatureType.BOOLEAN
            else:
                features[col] = FeatureType.TEXT
        
        # Calculate statistics
        statistics = {
            'numerical_stats': df.select_dtypes(include=[np.number]).describe().to_dict(),
            'categorical_stats': df.select_dtypes(include=['object']).describe().to_dict(),
            'correlation_matrix': df.select_dtypes(include=[np.number]).corr().to_dict()
        }
        
        return DatasetInfo(
            name="dataset",
            shape=df.shape,
            features=features,
            target_column=target_column,
            missing_values=df.isnull().sum().to_dict(),
            data_types=df.dtypes.astype(str).to_dict(),
            statistics=statistics
        )
    
    def preprocess_data(self, df: pd.DataFrame, dataset_info: DatasetInfo, 
                       test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Preprocess data with automatic feature engineering
        
        Args:
            df: Input dataframe
            dataset_info: Dataset information
            test_size: Test set size
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        df_processed = df.copy()
        
        # Handle missing values
        df_processed = self._handle_missing_values(df_processed, dataset_info)
        
        # Feature engineering
        df_processed = self._engineer_features(df_processed, dataset_info)
        
        # Encode categorical variables
        df_processed = self._encode_categorical(df_processed, dataset_info)
        
        # Scale numerical features
        df_processed = self._scale_numerical(df_processed, dataset_info)
        
        # Split data
        if dataset_info.target_column:
            X = df_processed.drop(columns=[dataset_info.target_column])
            y = df_processed[dataset_info.target_column]
            return train_test_split(X, y, test_size=test_size, random_state=42)
        else:
            return df_processed, None, None, None
    
    def _handle_missing_values(self, df: pd.DataFrame, dataset_info: DatasetInfo) -> pd.DataFrame:
        """Handle missing values intelligently"""
        for col, missing_count in dataset_info.missing_values.items():
            if missing_count > 0:
                feature_type = dataset_info.features.get(col, FeatureType.NUMERICAL)
                
                if feature_type == FeatureType.NUMERICAL:
                    # Use median for numerical features
                    df[col].fillna(df[col].median(), inplace=True)
                elif feature_type == FeatureType.CATEGORICAL:
                    # Use mode for categorical features
                    df[col].fillna(df[col].mode()[0], inplace=True)
                elif feature_type == FeatureType.BOOLEAN:
                    # Use mode for boolean features
                    df[col].fillna(df[col].mode()[0], inplace=True)
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame, dataset_info: DatasetInfo) -> pd.DataFrame:
        """Automatic feature engineering"""
        for col, feature_type in dataset_info.features.items():
            if feature_type == FeatureType.DATETIME:
                # Extract datetime features
                df[col] = pd.to_datetime(df[col])
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_dayofweek'] = df[col].dt.dayofweek
                df[f'{col}_hour'] = df[col].dt.hour
                df.drop(columns=[col], inplace=True)
            
            elif feature_type == FeatureType.NUMERICAL:
                # Create polynomial features for important numerical columns
                if col in df.columns and df[col].nunique() > 10:
                    df[f'{col}_squared'] = df[col] ** 2
                    df[f'{col}_log'] = np.log1p(np.abs(df[col]))
        
        return df
    
    def _encode_categorical(self, df: pd.DataFrame, dataset_info: DatasetInfo) -> pd.DataFrame:
        """Encode categorical variables"""
        categorical_cols = [col for col, ftype in dataset_info.features.items() 
                           if ftype == FeatureType.CATEGORICAL and col in df.columns]
        
        for col in categorical_cols:
            if df[col].nunique() > 10:
                # Use target encoding for high cardinality
                if dataset_info.target_column and dataset_info.target_column in df.columns:
                    target_mean = df.groupby(col)[dataset_info.target_column].mean()
                    df[f'{col}_encoded'] = df[col].map(target_mean)
                else:
                    # Use frequency encoding
                    freq_map = df[col].value_counts().to_dict()
                    df[f'{col}_freq'] = df[col].map(freq_map)
                df.drop(columns=[col], inplace=True)
            else:
                # Use one-hot encoding for low cardinality
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df, dummies], axis=1)
                df.drop(columns=[col], inplace=True)
        
        return df
    
    def _scale_numerical(self, df: pd.DataFrame, dataset_info: DatasetInfo) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_cols = [col for col in df.columns 
                         if df[col].dtype in ['int64', 'float64'] and col != dataset_info.target_column]
        
        if numerical_cols:
            scaler = StandardScaler()
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            self.scalers['standard'] = scaler
        
        return df

class AutoMLEngine:
    """Automated Machine Learning engine"""
    
    def __init__(self):
        """Initialize AutoML engine"""
        self.models = {}
        self.results = []
        self.best_model = None
        
        # Define model configurations
        self.classification_models = {
            'RandomForest': RandomForestClassifier(random_state=42),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42),
            'SVM': SVC(random_state=42),
            'MLP': MLPClassifier(random_state=42, max_iter=1000)
        }
        
        self.regression_models = {
            'RandomForest': RandomForestRegressor(random_state=42),
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(random_state=42),
            'Lasso': Lasso(random_state=42),
            'SVR': SVR(),
            'MLP': MLPRegressor(random_state=42, max_iter=1000)
        }
        
        # Hyperparameter grids
        self.param_grids = {
            'RandomForest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            },
            'GradientBoosting': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'LogisticRegression': {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2']
            }
        }
    
    def auto_train(self, X_train: pd.DataFrame, y_train: pd.Series, 
                   X_test: pd.DataFrame, y_test: pd.Series, 
                   model_type: ModelType = None) -> List[ModelResult]:
        """Automatically train and evaluate multiple models
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_test: Test features
            y_test: Test targets
            model_type: Type of models to train
            
        Returns:
            List of model results
        """
        # Determine model type if not specified
        if model_type is None:
            if self._is_classification_task(y_train):
                model_type = ModelType.CLASSIFICATION
            else:
                model_type = ModelType.REGRESSION
        
        # Select appropriate models
        if model_type == ModelType.CLASSIFICATION:
            models_to_try = self.classification_models
        else:
            models_to_try = self.regression_models
        
        results = []
        
        for model_name, model in models_to_try.items():
            logger.info(f"Training {model_name}...")
            
            start_time = time.time()
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                if model_type == ModelType.CLASSIFICATION:
                    metrics = self._calculate_classification_metrics(y_test, y_pred, model, X_test)
                else:
                    metrics = self._calculate_regression_metrics(y_test, y_pred)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                
                # Feature importance
                feature_importance = None
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(X_train.columns, model.feature_importances_))
                elif hasattr(model, 'coef_'):
                    feature_importance = dict(zip(X_train.columns, np.abs(model.coef_).flatten()))
                
                training_time = time.time() - start_time
                
                result = ModelResult(
                    model_name=model_name,
                    model_type=model_type,
                    model=model,
                    metrics=metrics,
                    training_time=training_time,
                    feature_importance=feature_importance,
                    predictions=y_pred,
                    cross_val_scores=cv_scores.tolist()
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                continue
        
        # Sort by primary metric
        primary_metric = 'accuracy' if model_type == ModelType.CLASSIFICATION else 'r2'
        results.sort(key=lambda x: x.metrics.get(primary_metric, 0), reverse=True)
        
        self.results = results
        self.best_model = results[0] if results else None
        
        return results
    
    def hyperparameter_optimization(self, model_name: str, X_train: pd.DataFrame, 
                                   y_train: pd.Series, cv: int = 5) -> ModelResult:
        """Perform hyperparameter optimization for a specific model
        
        Args:
            model_name: Name of the model
            X_train: Training features
            y_train: Training targets
            cv: Cross-validation folds
            
        Returns:
            Optimized model result
        """
        if model_name not in self.param_grids:
            raise ValueError(f"No parameter grid defined for {model_name}")
        
        # Get base model
        if self._is_classification_task(y_train):
            base_model = self.classification_models[model_name]
            scoring = 'accuracy'
        else:
            base_model = self.regression_models[model_name]
            scoring = 'r2'
        
        # Perform grid search
        grid_search = GridSearchCV(
            base_model,
            self.param_grids[model_name],
            cv=cv,
            scoring=scoring,
            n_jobs=-1
        )
        
        start_time = time.time()
        grid_search.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Create result
        result = ModelResult(
            model_name=f"{model_name}_optimized",
            model_type=ModelType.CLASSIFICATION if self._is_classification_task(y_train) else ModelType.REGRESSION,
            model=grid_search.best_estimator_,
            metrics={'cv_score': grid_search.best_score_},
            training_time=training_time,
            cross_val_scores=[grid_search.best_score_]
        )
        
        return result
    
    def _is_classification_task(self, y: pd.Series) -> bool:
        """Determine if the task is classification or regression"""
        return y.dtype == 'object' or y.nunique() < 20
    
    def _calculate_classification_metrics(self, y_true: pd.Series, y_pred: np.ndarray, 
                                        model: Any, X_test: pd.DataFrame) -> Dict[str, float]:
        """Calculate classification metrics"""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1': f1_score(y_true, y_pred, average='weighted')
        }
        
        # Add AUC if binary classification and model supports probability prediction
        if len(np.unique(y_true)) == 2 and hasattr(model, 'predict_proba'):
            try:
                y_prob = model.predict_proba(X_test)[:, 1]
                metrics['auc'] = roc_auc_score(y_true, y_prob)
            except:
                pass
        
        return metrics
    
    def _calculate_regression_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate regression metrics"""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred))
        }

class TimeSeriesAnalyzer:
    """Advanced time series analysis and forecasting"""
    
    def __init__(self):
        """Initialize time series analyzer"""
        self.models = {}
        self.forecasts = {}
    
    def analyze_time_series(self, data: pd.Series, freq: str = 'D') -> Dict[str, Any]:
        """Analyze time series data
        
        Args:
            data: Time series data
            freq: Frequency of the data
            
        Returns:
            Analysis results
        """
        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # Basic statistics
        stats = {
            'mean': data.mean(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'trend': self._detect_trend(data),
            'seasonality': self._detect_seasonality(data),
            'stationarity': self._test_stationarity(data)
        }
        
        # Decomposition
        try:
            decomposition = seasonal_decompose(data, model='additive', period=30)
            stats['decomposition'] = {
                'trend': decomposition.trend.dropna(),
                'seasonal': decomposition.seasonal.dropna(),
                'residual': decomposition.resid.dropna()
            }
        except:
            stats['decomposition'] = None
        
        return stats
    
    def forecast_arima(self, data: pd.Series, steps: int = 30, 
                      order: Tuple[int, int, int] = None) -> Dict[str, Any]:
        """ARIMA forecasting
        
        Args:
            data: Time series data
            steps: Number of steps to forecast
            order: ARIMA order (p, d, q)
            
        Returns:
            Forecast results
        """
        # Auto-determine order if not provided
        if order is None:
            order = self._auto_arima_order(data)
        
        # Fit ARIMA model
        model = ARIMA(data, order=order)
        fitted_model = model.fit()
        
        # Generate forecast
        forecast = fitted_model.forecast(steps=steps)
        conf_int = fitted_model.get_forecast(steps=steps).conf_int()
        
        return {
            'forecast': forecast,
            'confidence_interval': conf_int,
            'model': fitted_model,
            'order': order,
            'aic': fitted_model.aic,
            'bic': fitted_model.bic
        }
    
    def forecast_lstm(self, data: pd.Series, steps: int = 30, 
                     lookback: int = 60) -> Dict[str, Any]:
        """LSTM neural network forecasting
        
        Args:
            data: Time series data
            steps: Number of steps to forecast
            lookback: Number of previous time steps to use
            
        Returns:
            Forecast results
        """
        # Prepare data for LSTM
        X, y = self._prepare_lstm_data(data.values, lookback)
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Build LSTM model
        model = models.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
            layers.LSTM(50, return_sequences=False),
            layers.Dense(25),
            layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train model
        history = model.fit(
            X_train, y_train,
            batch_size=32,
            epochs=50,
            validation_data=(X_test, y_test),
            verbose=0
        )
        
        # Generate forecast
        last_sequence = data.values[-lookback:].reshape(1, lookback, 1)
        forecast = []
        
        for _ in range(steps):
            pred = model.predict(last_sequence, verbose=0)[0, 0]
            forecast.append(pred)
            
            # Update sequence
            last_sequence = np.roll(last_sequence, -1, axis=1)
            last_sequence[0, -1, 0] = pred
        
        return {
            'forecast': np.array(forecast),
            'model': model,
            'history': history.history,
            'train_loss': history.history['loss'][-1],
            'val_loss': history.history['val_loss'][-1]
        }
    
    def _detect_trend(self, data: pd.Series) -> str:
        """Detect trend in time series"""
        x = np.arange(len(data))
        slope, _, _, p_value, _ = stats.linregress(x, data.values)
        
        if p_value < 0.05:
            return 'increasing' if slope > 0 else 'decreasing'
        else:
            return 'no_trend'
    
    def _detect_seasonality(self, data: pd.Series) -> bool:
        """Detect seasonality in time series"""
        try:
            decomposition = seasonal_decompose(data, model='additive', period=min(30, len(data)//2))
            seasonal_strength = np.var(decomposition.seasonal.dropna()) / np.var(data.dropna())
            return seasonal_strength > 0.1
        except:
            return False
    
    def _test_stationarity(self, data: pd.Series) -> Dict[str, Any]:
        """Test stationarity using Augmented Dickey-Fuller test"""
        result = adfuller(data.dropna())
        
        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < 0.05
        }
    
    def _auto_arima_order(self, data: pd.Series) -> Tuple[int, int, int]:
        """Automatically determine ARIMA order"""
        # Simple heuristic for order selection
        # In practice, you'd use more sophisticated methods
        best_aic = float('inf')
        best_order = (1, 1, 1)
        
        for p in range(3):
            for d in range(2):
                for q in range(3):
                    try:
                        model = ARIMA(data, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order
    
    def _prepare_lstm_data(self, data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM training"""
        X, y = [], []
        
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i])
            y.append(data[i])
        
        return np.array(X).reshape(-1, lookback, 1), np.array(y)

class ModelInterpreter:
    """Model interpretability and explainability"""
    
    def __init__(self):
        """Initialize model interpreter"""
        self.explainers = {}
    
    def explain_model_shap(self, model: Any, X_train: pd.DataFrame, 
                          X_test: pd.DataFrame, model_type: ModelType) -> Dict[str, Any]:
        """Explain model using SHAP values
        
        Args:
            model: Trained model
            X_train: Training data
            X_test: Test data
            model_type: Type of model
            
        Returns:
            SHAP explanation results
        """
        try:
            # Choose appropriate explainer
            if hasattr(model, 'predict_proba'):
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.LinearExplainer(model, X_train)
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(X_test)
            
            # For classification, take the positive class
            if model_type == ModelType.CLASSIFICATION and isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # Calculate feature importance
            feature_importance = np.abs(shap_values).mean(axis=0)
            feature_importance_dict = dict(zip(X_test.columns, feature_importance))
            
            return {
                'shap_values': shap_values,
                'feature_importance': feature_importance_dict,
                'explainer': explainer
            }
            
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            return {}
    
    def explain_prediction_lime(self, model: Any, X_train: pd.DataFrame, 
                               instance: pd.Series, model_type: ModelType) -> Dict[str, Any]:
        """Explain individual prediction using LIME
        
        Args:
            model: Trained model
            X_train: Training data
            instance: Instance to explain
            model_type: Type of model
            
        Returns:
            LIME explanation results
        """
        try:
            # Create LIME explainer
            if model_type == ModelType.CLASSIFICATION:
                explainer = lime_tabular.LimeTabularExplainer(
                    X_train.values,
                    feature_names=X_train.columns,
                    class_names=['0', '1'],
                    mode='classification'
                )
                explanation = explainer.explain_instance(
                    instance.values,
                    model.predict_proba,
                    num_features=len(X_train.columns)
                )
            else:
                explainer = lime_tabular.LimeTabularExplainer(
                    X_train.values,
                    feature_names=X_train.columns,
                    mode='regression'
                )
                explanation = explainer.explain_instance(
                    instance.values,
                    model.predict,
                    num_features=len(X_train.columns)
                )
            
            # Extract feature contributions
            feature_contributions = dict(explanation.as_list())
            
            return {
                'explanation': explanation,
                'feature_contributions': feature_contributions,
                'prediction': model.predict([instance.values])[0]
            }
            
        except Exception as e:
            logger.error(f"LIME explanation failed: {e}")
            return {}

class ABTestFramework:
    """A/B testing framework for data science experiments"""
    
    def __init__(self):
        """Initialize A/B testing framework"""
        self.experiments = {}
    
    def create_experiment(self, name: str, control_data: pd.DataFrame, 
                         treatment_data: pd.DataFrame, metric_column: str) -> Dict[str, Any]:
        """Create and analyze an A/B test experiment
        
        Args:
            name: Experiment name
            control_data: Control group data
            treatment_data: Treatment group data
            metric_column: Column containing the metric to analyze
            
        Returns:
            Experiment results
        """
        # Basic statistics
        control_metric = control_data[metric_column]
        treatment_metric = treatment_data[metric_column]
        
        control_stats = {
            'mean': control_metric.mean(),
            'std': control_metric.std(),
            'count': len(control_metric)
        }
        
        treatment_stats = {
            'mean': treatment_metric.mean(),
            'std': treatment_metric.std(),
            'count': len(treatment_metric)
        }
        
        # Statistical tests
        # T-test
        t_stat, t_pvalue = ttest_ind(control_metric, treatment_metric)
        
        # Mann-Whitney U test (non-parametric)
        u_stat, u_pvalue = mannwhitneyu(control_metric, treatment_metric)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(control_metric) - 1) * control_metric.var() + 
                             (len(treatment_metric) - 1) * treatment_metric.var()) / 
                            (len(control_metric) + len(treatment_metric) - 2))
        cohens_d = (treatment_metric.mean() - control_metric.mean()) / pooled_std
        
        # Confidence interval for difference
        diff_mean = treatment_metric.mean() - control_metric.mean()
        diff_se = np.sqrt(control_metric.var()/len(control_metric) + 
                         treatment_metric.var()/len(treatment_metric))
        ci_lower = diff_mean - 1.96 * diff_se
        ci_upper = diff_mean + 1.96 * diff_se
        
        results = {
            'experiment_name': name,
            'control_stats': control_stats,
            'treatment_stats': treatment_stats,
            'difference': diff_mean,
            'relative_difference': diff_mean / control_stats['mean'] * 100,
            'statistical_tests': {
                't_test': {'statistic': t_stat, 'p_value': t_pvalue},
                'mann_whitney': {'statistic': u_stat, 'p_value': u_pvalue}
            },
            'effect_size': cohens_d,
            'confidence_interval': {'lower': ci_lower, 'upper': ci_upper},
            'is_significant': t_pvalue < 0.05
        }
        
        self.experiments[name] = results
        return results
    
    def power_analysis(self, effect_size: float, alpha: float = 0.05, 
                      power: float = 0.8) -> int:
        """Calculate required sample size for given power
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            alpha: Significance level
            power: Desired statistical power
            
        Returns:
            Required sample size per group
        """
        # Simplified power analysis calculation
        # In practice, you'd use more sophisticated methods
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        return int(np.ceil(n))

class DataSciencePlatform:
    """Main data science platform integrating all components"""
    
    def __init__(self):
        """Initialize the data science platform"""
        self.preprocessor = DataPreprocessor()
        self.automl = AutoMLEngine()
        self.time_series = TimeSeriesAnalyzer()
        self.interpreter = ModelInterpreter()
        self.ab_testing = ABTestFramework()
        
        # Project state
        self.current_dataset = None
        self.current_models = []
        self.project_history = []
    
    def load_dataset(self, file_path: str, target_column: str = None) -> DatasetInfo:
        """Load and analyze a dataset
        
        Args:
            file_path: Path to the dataset file
            target_column: Name of the target column
            
        Returns:
            Dataset information
        """
        # Load data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Analyze dataset
        dataset_info = self.preprocessor.analyze_dataset(df, target_column)
        self.current_dataset = (df, dataset_info)
        
        logger.info(f"Loaded dataset: {dataset_info.shape[0]} rows, {dataset_info.shape[1]} columns")
        
        return dataset_info
    
    def run_automl_pipeline(self, test_size: float = 0.2) -> List[ModelResult]:
        """Run complete AutoML pipeline
        
        Args:
            test_size: Test set size
            
        Returns:
            List of model results
        """
        if self.current_dataset is None:
            raise ValueError("No dataset loaded")
        
        df, dataset_info = self.current_dataset
        
        # Preprocess data
        X_train, X_test, y_train, y_test = self.preprocessor.preprocess_data(
            df, dataset_info, test_size
        )
        
        # Run AutoML
        results = self.automl.auto_train(X_train, y_train, X_test, y_test)
        self.current_models = results
        
        return results
    
    def explain_best_model(self) -> Dict[str, Any]:
        """Explain the best performing model
        
        Returns:
            Model explanation results
        """
        if not self.current_models:
            raise ValueError("No models trained")
        
        best_model_result = self.current_models[0]
        df, dataset_info = self.current_dataset
        
        # Preprocess data again for explanation
        X_train, X_test, y_train, y_test = self.preprocessor.preprocess_data(
            df, dataset_info, 0.2
        )
        
        # SHAP explanation
        shap_results = self.interpreter.explain_model_shap(
            best_model_result.model, X_train, X_test, best_model_result.model_type
        )
        
        return {
            'model_name': best_model_result.model_name,
            'metrics': best_model_result.metrics,
            'shap_explanation': shap_results,
            'feature_importance': best_model_result.feature_importance
        }
    
    def generate_report(self, output_path: str = "data_science_report.html"):
        """Generate comprehensive data science report
        
        Args:
            output_path: Path to save the report
        """
        if self.current_dataset is None:
            raise ValueError("No dataset loaded")
        
        df, dataset_info = self.current_dataset
        
        # Create visualizations
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Dataset overview
        numerical_cols = [col for col, dtype in dataset_info.data_types.items() 
                         if dtype in ['int64', 'float64'] and col != dataset_info.target_column]
        
        if len(numerical_cols) >= 2:
            # Correlation heatmap
            corr_matrix = df[numerical_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=axes[0, 0])
            axes[0, 0].set_title('Feature Correlation Matrix')
            
            # Distribution of first numerical feature
            df[numerical_cols[0]].hist(bins=30, ax=axes[0, 1])
            axes[0, 1].set_title(f'Distribution of {numerical_cols[0]}')
        
        # Model performance comparison
        if self.current_models:
            model_names = [result.model_name for result in self.current_models]
            primary_metric = 'accuracy' if self.current_models[0].model_type == ModelType.CLASSIFICATION else 'r2'
            scores = [result.metrics.get(primary_metric, 0) for result in self.current_models]
            
            axes[1, 0].bar(model_names, scores)
            axes[1, 0].set_title(f'Model Performance ({primary_metric})')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Feature importance of best model
            if self.current_models[0].feature_importance:
                importance_items = list(self.current_models[0].feature_importance.items())
                importance_items.sort(key=lambda x: x[1], reverse=True)
                features, importances = zip(*importance_items[:10])
                
                axes[1, 1].barh(features, importances)
                axes[1, 1].set_title('Top 10 Feature Importances')
        
        plt.tight_layout()
        plt.savefig(output_path.replace('.html', '.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate HTML report
        html_content = self._generate_html_report(dataset_info)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Report generated: {output_path}")
    
    def _generate_html_report(self, dataset_info: DatasetInfo) -> str:
        """Generate HTML report content"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Science Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Science Analysis Report</h1>
                <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Dataset Overview</h2>
                <p><strong>Shape:</strong> {dataset_info.shape[0]} rows × {dataset_info.shape[1]} columns</p>
                <p><strong>Target Column:</strong> {dataset_info.target_column or 'None specified'}</p>
                
                <h3>Feature Types</h3>
                <table>
                    <tr><th>Feature</th><th>Type</th><th>Missing Values</th></tr>
        """
        
        for feature, ftype in dataset_info.features.items():
            missing = dataset_info.missing_values.get(feature, 0)
            html += f"<tr><td>{feature}</td><td>{ftype.name}</td><td>{missing}</td></tr>"
        
        html += """
                </table>
            </div>
        """
        
        if self.current_models:
            html += """
            <div class="section">
                <h2>Model Results</h2>
                <table>
                    <tr><th>Model</th><th>Metrics</th><th>Training Time (s)</th></tr>
            """
            
            for result in self.current_models:
                metrics_str = ", ".join([f"{k}: {v:.4f}" for k, v in result.metrics.items()])
                html += f"<tr><td>{result.model_name}</td><td>{metrics_str}</td><td>{result.training_time:.2f}</td></tr>"
            
            html += """
                </table>
            </div>
            """
        
        html += """
            <div class="section">
                <h2>Visualizations</h2>
                <img src="data_science_report.png" alt="Analysis Visualizations" style="max-width: 100%;">
            </div>
        </body>
        </html>
        """
        
        return html

class DSApplication:
    """Main application class for the data science platform"""
    
    def __init__(self):
        """Initialize the application"""
        self.platform = DataSciencePlatform()
        self.parse_arguments()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Advanced Data Science Platform')
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Load dataset command
        load_parser = subparsers.add_parser('load', help='Load dataset')
        load_parser.add_argument('--file', required=True, help='Dataset file path')
        load_parser.add_argument('--target', help='Target column name')
        
        # AutoML command
        automl_parser = subparsers.add_parser('automl', help='Run AutoML pipeline')
        automl_parser.add_argument('--test-size', type=float, default=0.2, help='Test set size')
        
        # Time series command
        ts_parser = subparsers.add_parser('timeseries', help='Time series analysis')
        ts_parser.add_argument('--file', required=True, help='Time series data file')
        ts_parser.add_argument('--column', required=True, help='Time series column')
        ts_parser.add_argument('--forecast-steps', type=int, default=30, help='Forecast steps')
        
        # A/B test command
        ab_parser = subparsers.add_parser('abtest', help='A/B test analysis')
        ab_parser.add_argument('--control', required=True, help='Control group data file')
        ab_parser.add_argument('--treatment', required=True, help='Treatment group data file')
        ab_parser.add_argument('--metric', required=True, help='Metric column name')
        
        # Report command
        report_parser = subparsers.add_parser('report', help='Generate report')
        report_parser.add_argument('--output', default='report.html', help='Output file path')
        
        self.args = parser.parse_args()
    
    def run(self):
        """Run the data science application"""
        if self.args.command == 'load':
            self.load_dataset()
        elif self.args.command == 'automl':
            self.run_automl()
        elif self.args.command == 'timeseries':
            self.analyze_time_series()
        elif self.args.command == 'abtest':
            self.run_ab_test()
        elif self.args.command == 'report':
            self.generate_report()
        else:
            print("No command specified. Use --help for usage information.")
    
    def load_dataset(self):
        """Load dataset command"""
        try:
            dataset_info = self.platform.load_dataset(self.args.file, self.args.target)
            
            print("Dataset loaded successfully!")
            print(f"Shape: {dataset_info.shape}")
            print(f"Features: {len(dataset_info.features)}")
            print(f"Target: {dataset_info.target_column}")
            
            # Show feature types
            print("\nFeature Types:")
            for feature, ftype in dataset_info.features.items():
                missing = dataset_info.missing_values.get(feature, 0)
                print(f"  {feature}: {ftype.name} ({missing} missing)")
                
        except Exception as e:
            print(f"Error loading dataset: {e}")
    
    def run_automl(self):
        """Run AutoML command"""
        try:
            results = self.platform.run_automl_pipeline(self.args.test_size)
            
            print("AutoML pipeline completed!")
            print(f"Trained {len(results)} models")
            
            print("\nModel Results:")
            for i, result in enumerate(results, 1):
                primary_metric = 'accuracy' if result.model_type == ModelType.CLASSIFICATION else 'r2'
                score = result.metrics.get(primary_metric, 0)
                print(f"  {i}. {result.model_name}: {primary_metric}={score:.4f}")
            
            # Explain best model
            explanation = self.platform.explain_best_model()
            print(f"\nBest Model: {explanation['model_name']}")
            
            if explanation.get('feature_importance'):
                print("Top 5 Important Features:")
                sorted_features = sorted(explanation['feature_importance'].items(), 
                                       key=lambda x: x[1], reverse=True)
                for feature, importance in sorted_features[:5]:
                    print(f"  {feature}: {importance:.4f}")
                    
        except Exception as e:
            print(f"Error running AutoML: {e}")
    
    def analyze_time_series(self):
        """Analyze time series command"""
        try:
            # Load time series data
            df = pd.read_csv(self.args.file)
            ts_data = pd.Series(df[self.args.column].values, 
                              index=pd.to_datetime(df.index))
            
            # Analyze time series
            analysis = self.platform.time_series.analyze_time_series(ts_data)
            
            print("Time Series Analysis Results:")
            print(f"  Mean: {analysis['mean']:.4f}")
            print(f"  Std: {analysis['std']:.4f}")
            print(f"  Trend: {analysis['trend']}")
            print(f"  Seasonality: {analysis['seasonality']}")
            print(f"  Stationary: {analysis['stationarity']['is_stationary']}")
            
            # ARIMA forecast
            arima_forecast = self.platform.time_series.forecast_arima(
                ts_data, self.args.forecast_steps
            )
            
            print(f"\nARIMA Forecast ({self.args.forecast_steps} steps):")
            print(f"  Order: {arima_forecast['order']}")
            print(f"  AIC: {arima_forecast['aic']:.2f}")
            print(f"  First 5 forecasts: {arima_forecast['forecast'][:5].values}")
            
        except Exception as e:
            print(f"Error in time series analysis: {e}")
    
    def run_ab_test(self):
        """Run A/B test command"""
        try:
            # Load data
            control_df = pd.read_csv(self.args.control)
            treatment_df = pd.read_csv(self.args.treatment)
            
            # Run A/B test
            results = self.platform.ab_testing.create_experiment(
                "CLI_Experiment",
                control_df,
                treatment_df,
                self.args.metric
            )
            
            print("A/B Test Results:")
            print(f"  Control Mean: {results['control_stats']['mean']:.4f}")
            print(f"  Treatment Mean: {results['treatment_stats']['mean']:.4f}")
            print(f"  Difference: {results['difference']:.4f}")
            print(f"  Relative Difference: {results['relative_difference']:.2f}%")
            print(f"  P-value: {results['statistical_tests']['t_test']['p_value']:.4f}")
            print(f"  Significant: {results['is_significant']}")
            print(f"  Effect Size (Cohen's d): {results['effect_size']:.4f}")
            
        except Exception as e:
            print(f"Error in A/B test: {e}")
    
    def generate_report(self):
        """Generate report command"""
        try:
            self.platform.generate_report(self.args.output)
            print(f"Report generated: {self.args.output}")
        except Exception as e:
            print(f"Error generating report: {e}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Advanced Data Science Platform".center(60))
    print("AutoML, Time Series, and Statistical Analysis".center(60))
    print("=" * 60)
    
    app = DSApplication()
    app.run()

if __name__ == "__main__":
    main() 