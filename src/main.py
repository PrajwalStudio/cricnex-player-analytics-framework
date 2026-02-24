"""
CricNex - Main Pipeline Orchestrator
Executes complete ML pipeline from data loading to model deployment
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(__file__))

from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from model_training import ModelTrainer


def run_pipeline():
    """
    Execute complete CricNex ML pipeline
    """
    print("="*70)
    print("CRICNEX - CRICKET PLAYER PERFORMANCE PREDICTION SYSTEM")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("\n" + "="*70)
    print("STEP 1: DATA LOADING")
    print("="*70)
    
    deliveries_path = "../ballbyball/deliveries_updated_mens_ipl_upto_2024.csv"
    matches_path = "../ballbyball/matches_updated_mens_ipl_upto_2024.csv"
    
    if not os.path.exists(deliveries_path):
        deliveries_path = "ballbyball/deliveries_updated_mens_ipl_upto_2024.csv"
        matches_path = "ballbyball/matches_updated_mens_ipl_upto_2024.csv"
    
    loader = DataLoader(deliveries_path, matches_path)
    
    try:
        loader.load_data()
        player_match_data = loader.aggregate_match_stats()
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nMake sure the dataset files are in the 'ballbyball' directory:")
        print("   - deliveries_updated_mens_ipl_upto_2024.csv")
        print("   - matches_updated_mens_ipl_upto_2024.csv")
        return
    
    print("\n" + "="*70)
    print("STEP 2: FEATURE ENGINEERING")
    print("="*70)
    
    engineer = FeatureEngineer(player_match_data)
    features_df = engineer.engineer_all_features()
    
    features_path = "data/features.csv"
    engineer.save_features(features_path)
    
    print("\n" + "="*70)
    print("STEP 3: MODEL TRAINING")
    print("="*70)
    
    trainer = ModelTrainer(features_df)
    trainer.prepare_data(target_variable='runs_scored')
    
    print("\nTraining multiple models...")
    
    try:
        trainer.train_xgboost(n_estimators=100, learning_rate=0.1, max_depth=6)
    except Exception as e:
        print(f"Warning: XGBoost training failed: {e}")
    
    try:
        trainer.train_random_forest(n_estimators=100, max_depth=20)
    except Exception as e:
        print(f"Warning: Random Forest training failed: {e}")
    
    try:
        trainer.train_arima()
    except Exception as e:
        print(f"Warning: ARIMA training failed: {e}")
    
    try:
        trainer.train_lstm(epochs=20)
    except Exception as e:
        print(f"Warning: LSTM training failed: {e}")
    
    print("\n" + "="*70)
    print("STEP 4: MODEL EVALUATION")
    print("="*70)
    
    comparison = trainer.compare_models()
    print("\nModel Comparison:")
    print(comparison.to_string(index=False))
    
    comparison_path = "results/model_comparison.csv"
    trainer.save_comparison(comparison_path)
    
    best_name, best_model = trainer.get_best_model()
    print(f"\nBest Model: {best_name.upper()}")
    print(f"   RMSE: {best_model['metrics']['test_rmse']:.2f}")
    print(f"   MAE: {best_model['metrics']['test_mae']:.2f}")
    print(f"   R2: {best_model['metrics']['test_r2']:.4f}")
    
    print("\n" + "="*70)
    print("STEP 5: SAVE MODELS")
    print("="*70)
    
    trainer.save_all_models("models")
    
    best_model_path = "models/best_model.pkl"
    trainer.save_best_model(best_model_path)
    
    print("\n" + "="*70)
    print("STEP 6: FEATURE IMPORTANCE")
    print("="*70)
    
    feature_importance = trainer.get_feature_importance(top_n=15)
    if feature_importance is not None:
        print(f"\nTop 15 Most Important Features ({best_name}):")
        print(feature_importance.to_string(index=False))
        
        importance_path = "results/feature_importance.csv"
        os.makedirs(os.path.dirname(importance_path), exist_ok=True)
        feature_importance.to_csv(importance_path, index=False)
        print(f"\nFeature importance saved: {importance_path}")
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    
    print("\nAll steps completed successfully!")
    print("\nOutput Files:")
    print(f"   Features:          {features_path}")
    print(f"   Best Model:        {best_model_path}")
    print(f"   All Models:        models/*.pkl")
    print(f"   Comparison:        {comparison_path}")
    
    print("\nNext Steps:")
    print("   1. Start API server:  python src/api.py")
    print("   2. Test predictions:  python test_api.py")
    print("   3. Start frontend:    cd frontend && npm start")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
    except Exception as e:
        print(f"\n\nPipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
