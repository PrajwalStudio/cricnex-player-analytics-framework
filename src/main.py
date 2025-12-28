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
    
    # ==================== STEP 1: DATA LOADING ====================
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
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure the dataset files are in the 'ballbyball' directory:")
        print("   - deliveries_updated_mens_ipl_upto_2024.csv")
        print("   - matches_updated_mens_ipl_upto_2024.csv")
        return
    
    # ==================== STEP 2: FEATURE ENGINEERING ====================
    print("\n" + "="*70)
    print("STEP 2: FEATURE ENGINEERING")
    print("="*70)
    
    engineer = FeatureEngineer(player_match_data)
    features_df = engineer.engineer_all_features()
    
    # Save features
    features_path = "data/features.csv"
    engineer.save_features(features_path)
    
    # ==================== STEP 3: MODEL TRAINING ====================
    print("\n" + "="*70)
    print("STEP 3: MODEL TRAINING")
    print("="*70)
    
    trainer = ModelTrainer(features_df)
    trainer.prepare_data(target_variable='runs_scored')
    
    # Train all models
    print("\n🤖 Training multiple models...")
    
    try:
        # Train XGBoost
        trainer.train_xgboost(n_estimators=100, learning_rate=0.1, max_depth=6)
    except Exception as e:
        print(f"⚠ XGBoost training failed: {e}")
    
    try:
        # Train Random Forest
        trainer.train_random_forest(n_estimators=100, max_depth=20)
    except Exception as e:
        print(f"⚠ Random Forest training failed: {e}")
    
    try:
        # Train ARIMA (baseline)
        trainer.train_arima()
    except Exception as e:
        print(f"⚠ ARIMA training failed: {e}")
    
    try:
        # Train LSTM (neural network)
        trainer.train_lstm(epochs=20)
    except Exception as e:
        print(f"⚠ LSTM training failed: {e}")
    
    # ==================== STEP 4: MODEL EVALUATION ====================
    print("\n" + "="*70)
    print("STEP 4: MODEL EVALUATION")
    print("="*70)
    
    # Compare models
    comparison = trainer.compare_models()
    print("\n📊 Model Comparison:")
    print(comparison.to_string(index=False))
    
    # Save comparison
    comparison_path = "results/model_comparison.csv"
    trainer.save_comparison(comparison_path)
    
    # Get best model
    best_name, best_model = trainer.get_best_model()
    print(f"\n🏆 Best Model: {best_name.upper()}")
    print(f"   RMSE: {best_model['metrics']['test_rmse']:.2f}")
    print(f"   MAE: {best_model['metrics']['test_mae']:.2f}")
    print(f"   R²: {best_model['metrics']['test_r2']:.4f}")
    
    # ==================== STEP 5: SAVE MODELS ====================
    print("\n" + "="*70)
    print("STEP 5: SAVE MODELS")
    print("="*70)
    
    # Save all models
    trainer.save_all_models("models")
    
    # Save best model
    best_model_path = "models/best_model.pkl"
    trainer.save_best_model(best_model_path)
    
    # ==================== STEP 6: FEATURE IMPORTANCE ====================
    print("\n" + "="*70)
    print("STEP 6: FEATURE IMPORTANCE")
    print("="*70)
    
    feature_importance = trainer.get_feature_importance(top_n=15)
    if feature_importance is not None:
        print(f"\n🎯 Top 15 Most Important Features ({best_name}):")
        print(feature_importance.to_string(index=False))
        
        # Save feature importance
        importance_path = "results/feature_importance.csv"
        os.makedirs(os.path.dirname(importance_path), exist_ok=True)
        feature_importance.to_csv(importance_path, index=False)
        print(f"\n✓ Feature importance saved: {importance_path}")
    
    # ==================== COMPLETION ====================
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    
    print("\n✅ All steps completed successfully!")
    print("\n📁 Output Files:")
    print(f"   • Features:          {features_path}")
    print(f"   • Best Model:        {best_model_path}")
    print(f"   • All Models:        models/*.pkl")
    print(f"   • Comparison:        {comparison_path}")
    
    print("\n🚀 Next Steps:")
    print("   1. Start API server:  python src/api.py")
    print("   2. Test predictions:  python test_api.py")
    print("   3. Start frontend:    cd frontend && npm start")
    
    print(f"\n✓ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
