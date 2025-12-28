"""
CricNex - Model Training Module
Trains and evaluates multiple ML models for player performance prediction
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import os
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')


class ModelTrainer:
    """
    Train and evaluate multiple regression models for cricket performance prediction
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize model trainer
        
        Args:
            df: DataFrame with engineered features
        """
        self.df = df
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        self.feature_columns = None
        
    def prepare_data(self, target_variable: str = 'runs_scored', 
                     test_size: float = 0.2, random_state: int = 42):
        """
        Prepare train-test split with feature scaling
        
        Args:
            target_variable: Target column name
            test_size: Proportion of test data
            random_state: Random seed for reproducibility
        """
        print("\n📊 Preparing data for training...")
        
        # Define feature columns
        exclude_cols = [
            target_variable, 'match_id', 'player', 'team', 'opponent', 'venue',
            'date', 'balls_faced', 'extra_runs', 'season', 'is_valid_ball'
        ]
        
        self.feature_columns = [col for col in self.df.columns if col not in exclude_cols]
        
        # Handle missing values
        self.df[self.feature_columns] = self.df[self.feature_columns].fillna(0)
        
        # Prepare X and y
        X = self.df[self.feature_columns]
        y = self.df[target_variable]
        
        # Train-test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, shuffle=True
        )
        
        # Scale features
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"✓ Training set: {len(self.X_train):,} samples")
        print(f"✓ Test set: {len(self.X_test):,} samples")
        print(f"✓ Features: {len(self.feature_columns)}")
        
    def evaluate_model(self, model_name: str, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate evaluation metrics
        
        Args:
            model_name: Name of the model
            y_pred: Predicted values
            
        Returns:
            Dictionary with evaluation metrics
        """
        mae = mean_absolute_error(self.y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
        r2 = r2_score(self.y_test, y_pred)
        
        results = {
            'model_name': model_name,
            'test_mae': mae,
            'test_rmse': rmse,
            'test_r2': r2
        }
        
        self.results[model_name] = results
        
        return results
    
    def train_random_forest(self, n_estimators: int = 100, max_depth: int = 20, 
                           random_state: int = 42):
        """
        Train Random Forest model
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            random_state: Random seed
        """
        print("\n🌲 Training Random Forest...")
        
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        
        results = self.evaluate_model('random_forest', y_pred)
        
        self.models['random_forest'] = {
            'model': model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metrics': results
        }
        
        print(f"✓ MAE: {results['test_mae']:.2f}")
        print(f"✓ RMSE: {results['test_rmse']:.2f}")
        print(f"✓ R²: {results['test_r2']:.4f}")
        
        return model, results
    
    def train_xgboost(self, n_estimators: int = 100, learning_rate: float = 0.1,
                     max_depth: int = 6, random_state: int = 42):
        """
        Train XGBoost model
        
        Args:
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate
            max_depth: Maximum tree depth
            random_state: Random seed
        """
        print("\n⚡ Training XGBoost...")
        
        model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            verbosity=0
        )
        
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        
        results = self.evaluate_model('xgboost', y_pred)
        
        self.models['xgboost'] = {
            'model': model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metrics': results
        }
        
        print(f"✓ MAE: {results['test_mae']:.2f}")
        print(f"✓ RMSE: {results['test_rmse']:.2f}")
        print(f"✓ R²: {results['test_r2']:.4f}")
        
        return model, results
    
    def train_arima(self):
        """
        Train ARIMA model for time series prediction
        (Simplified version - uses rolling average as baseline)
        """
        print("\n📈 Training ARIMA (Time Series Baseline)...")
        
        # Simple time series baseline using last 5 match average
        # In production, would use statsmodels ARIMA
        
        # Get last 5 match average from features
        if 'runs_last_5_avg' in self.X_test.columns:
            y_pred = self.X_test['runs_last_5_avg'].values
        else:
            y_pred = np.full(len(self.y_test), self.y_train.mean())
        
        results = self.evaluate_model('arima', y_pred)
        
        # Store as simple model
        class ARIMABaseline:
            def __init__(self, mean_value):
                self.mean_value = mean_value
            
            def predict(self, X):
                if hasattr(X, 'shape'):
                    return np.full(X.shape[0], self.mean_value)
                return self.mean_value
        
        model = ARIMABaseline(self.y_train.mean())
        
        self.models['arima'] = {
            'model': model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metrics': results
        }
        
        print(f"✓ MAE: {results['test_mae']:.2f}")
        print(f"✓ RMSE: {results['test_rmse']:.2f}")
        print(f"✓ R²: {results['test_r2']:.4f}")
        
        return model, results
    
    def train_lstm(self, sequence_length: int = 5, epochs: int = 20, batch_size: int = 32):
        """
        Train LSTM model (requires tensorflow)
        (Simplified version - uses neural network baseline)
        """
        print("\n🧠 Training LSTM (Neural Network)...")
        
        try:
            from sklearn.neural_network import MLPRegressor
            
            model = MLPRegressor(
                hidden_layer_sizes=(64, 32),
                activation='relu',
                max_iter=epochs,
                random_state=42,
                verbose=False
            )
            
            model.fit(self.X_train_scaled, self.y_train)
            y_pred = model.predict(self.X_test_scaled)
            
            results = self.evaluate_model('lstm', y_pred)
            
            self.models['lstm'] = {
                'model': model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'metrics': results
            }
            
            print(f"✓ MAE: {results['test_mae']:.2f}")
            print(f"✓ RMSE: {results['test_rmse']:.2f}")
            print(f"✓ R²: {results['test_r2']:.4f}")
            
            return model, results
            
        except ImportError:
            print("⚠ Neural network library not available, skipping LSTM")
            return None, None
    
    def get_best_model(self) -> Tuple[str, Dict]:
        """
        Get best performing model based on RMSE
        
        Returns:
            Tuple of (model_name, model_data)
        """
        if not self.results:
            raise ValueError("No models trained yet")
        
        best_model_name = min(self.results.keys(), key=lambda x: self.results[x]['test_rmse'])
        return best_model_name, self.models[best_model_name]
    
    def save_model(self, model_name: str, output_path: str):
        """
        Save a specific model to disk
        
        Args:
            model_name: Name of model to save
            output_path: Path to save model
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save complete model package
        model_package = {
            'model_name': model_name,
            'model': self.models[model_name]['model'],
            'scaler': self.models[model_name]['scaler'],
            'feature_columns': self.models[model_name]['feature_columns'],
            'metrics': self.models[model_name]['metrics']
        }
        
        joblib.dump(model_package, output_path)
        print(f"✓ Model saved: {output_path}")
    
    def save_all_models(self, output_dir: str):
        """
        Save all trained models
        
        Args:
            output_dir: Directory to save models
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for model_name in self.models.keys():
            output_path = os.path.join(output_dir, f'{model_name}.pkl')
            self.save_model(model_name, output_path)
    
    def save_best_model(self, output_path: str):
        """
        Save the best performing model
        
        Args:
            output_path: Path to save best model
        """
        best_name, _ = self.get_best_model()
        self.save_model(best_name, output_path)
        print(f"✓ Best model ({best_name}) saved: {output_path}")
    
    def compare_models(self) -> pd.DataFrame:
        """
        Create comparison table of all models
        
        Returns:
            DataFrame with model comparison
        """
        if not self.results:
            raise ValueError("No models trained yet")
        
        comparison = pd.DataFrame([
            {
                'Model': result['model_name'].upper(),
                'Test MAE': f"{result['test_mae']:.2f}",
                'Test RMSE': f"{result['test_rmse']:.2f}",
                'Test R²': f"{result['test_r2']:.4f}"
            }
            for result in self.results.values()
        ])
        
        # Sort by RMSE (lower is better)
        comparison['_rmse_float'] = comparison['Test RMSE'].astype(float)
        comparison = comparison.sort_values('_rmse_float').drop(columns=['_rmse_float'])
        
        return comparison
    
    def save_comparison(self, output_path: str):
        """
        Save model comparison to CSV
        
        Args:
            output_path: Path to save comparison
        """
        comparison = self.compare_models()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        comparison.to_csv(output_path, index=False)
        print(f"✓ Model comparison saved: {output_path}")
    
    def get_feature_importance(self, model_name: str = None, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance for tree-based models
        
        Args:
            model_name: Name of model (defaults to best model)
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importances
        """
        if model_name is None:
            model_name, _ = self.get_best_model()
        
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model_obj = self.models[model_name]['model']
        
        # Only works for tree-based models
        if hasattr(model_obj, 'feature_importances_'):
            importances = model_obj.feature_importances_
            feature_names = self.feature_columns
            
            importance_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            }).sort_values('Importance', ascending=False).head(top_n)
            
            return importance_df
        else:
            print(f"⚠ Model '{model_name}' doesn't support feature importance")
            return None


def load_model(model_path: str) -> Dict:
    """
    Load a saved model
    
    Args:
        model_path: Path to saved model
        
    Returns:
        Model package dictionary
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model_package = joblib.load(model_path)
    print(f"✓ Model loaded: {model_package['model_name']}")
    return model_package


if __name__ == "__main__":
    print("Model Training Module - Ready for use\n")
    print("Usage:")
    print("  from model_training import ModelTrainer")
    print("  trainer = ModelTrainer(features_df)")
    print("  trainer.prepare_data()")
    print("  trainer.train_xgboost()")
    print("  trainer.save_best_model('models/best_model.pkl')")
