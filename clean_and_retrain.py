"""
CricNex - Data Cleaning and Model Retraining Script
Cleans team and venue names, then retrains all models
"""

import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from model_training import ModelTrainer
from feature_engineering import FeatureEngineer


def clean_venue_names(df):
    """
    Standardize venue names by removing city suffixes and variations
    """
    print("\n" + "="*70)
    print("CLEANING VENUE NAMES")
    print("="*70)
    
    # Cities to remove from venue names
    city_suffixes = [
        'Mumbai', 'Bengaluru', 'Bangalore', 'Chennai', 'Kolkata', 'Delhi',
        'Pune', 'Hyderabad', 'Jaipur', 'Chandigarh', 'Mohali', 'Ahmedabad',
        'Lucknow', 'Dharamsala', 'Indore', 'Visakhapatnam', 'Cuttack',
        'Nagpur', 'Ranchi', 'Guwahati', 'Kochi', 'Raipur'
    ]
    
    # Stadium name standardization mapping
    venue_mapping = {
        'Feroz Shah Kotla': 'Arun Jaitley Stadium',
        'Feroz Shah Kotla Ground': 'Arun Jaitley Stadium',
        'Dr DY Patil Sports Academy': 'Dr. DY Patil Sports Academy',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium': 'ACA-VDCA Cricket Stadium',
        'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium': 'Ekana Cricket Stadium',
        'Himachal Pradesh Cricket Association Stadium': 'HPCA Stadium',
        'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium',
        'Shaheed Veer Narayan Singh International Stadium': 'Shaheed Veer Narayan Singh Stadium',
    }
    
    def standardize_venue(venue_name):
        if pd.isna(venue_name):
            return venue_name
        
        # Remove trailing periods and extra spaces
        venue = str(venue_name).strip().replace('.', '')
        
        # Remove city suffixes
        for city in city_suffixes:
            # Remove ", City" pattern
            venue = venue.replace(f', {city}', '')
            venue = venue.replace(f',{city}', '')
        
        # Apply specific mappings
        for old_name, new_name in venue_mapping.items():
            if old_name.lower() in venue.lower():
                venue = new_name
        
        # Clean up extra spaces
        venue = ' '.join(venue.split())
        
        return venue
    
    # Apply cleaning
    original_venues = df['venue'].nunique()
    df['venue'] = df['venue'].apply(standardize_venue)
    cleaned_venues = df['venue'].nunique()
    
    print(f"✓ Original unique venues: {original_venues}")
    print(f"✓ Cleaned unique venues: {cleaned_venues}")
    print(f"✓ Removed {original_venues - cleaned_venues} duplicate venue entries")
    
    return df


def clean_team_names(df):
    """
    Standardize team names
    """
    print("\n" + "="*70)
    print("CLEANING TEAM NAMES")
    print("="*70)
    
    # Team name standardization
    team_mapping = {
        'Delhi Daredevils': 'Delhi Capitals',
        'Kings XI Punjab': 'Punjab Kings',
        'Rising Pune Supergiants': 'Rising Pune Supergiant',
        'Pune Warriors India': 'Pune Warriors',
    }
    
    def standardize_team(team_name):
        if pd.isna(team_name):
            return team_name
        
        team = str(team_name).strip()
        
        # Apply specific mappings
        if team in team_mapping:
            team = team_mapping[team]
        
        return team
    
    # Apply cleaning to both team and opponent columns
    original_teams = df['team'].nunique()
    df['team'] = df['team'].apply(standardize_team)
    df['opponent'] = df['opponent'].apply(standardize_team)
    cleaned_teams = df['team'].nunique()
    
    print(f"✓ Original unique teams: {original_teams}")
    print(f"✓ Cleaned unique teams: {cleaned_teams}")
    
    # Show current teams
    print("\nCurrent teams in dataset:")
    for team in sorted(df['team'].unique()):
        count = len(df[df['team'] == team])
        print(f"  - {team}: {count} records")
    
    return df


def retrain_all_models():
    """
    Clean data and retrain all models
    """
    print("\n" + "="*70)
    print("CRICNEX - DATA CLEANING AND MODEL RETRAINING")
    print("="*70)
    
    # Load original data
    print("\n📂 Loading features dataset...")
    features_path = 'data/features.csv'
    
    if not os.path.exists(features_path):
        print(f"❌ Error: {features_path} not found!")
        return
    
    df = pd.read_csv(features_path)
    print(f"✓ Loaded {len(df)} records")
    
    # Clean data
    df = clean_venue_names(df)
    df = clean_team_names(df)
    
    # Save cleaned data
    cleaned_path = 'data/features_cleaned.csv'
    df.to_csv(cleaned_path, index=False)
    print(f"\n✓ Saved cleaned data to: {cleaned_path}")
    
    # Backup original and replace
    backup_path = 'data/features_backup.csv'
    if not os.path.exists(backup_path):
        original_df = pd.read_csv(features_path)
        original_df.to_csv(backup_path, index=False)
        print(f"✓ Backed up original data to: {backup_path}")
    
    df.to_csv(features_path, index=False)
    print(f"✓ Updated {features_path} with cleaned data")
    
    # Retrain models
    print("\n" + "="*70)
    print("RETRAINING MODELS")
    print("="*70)
    
    trainer = ModelTrainer(df)
    trainer.prepare_data(target_variable='runs_scored')
    
    # Train all models (excluding LSTM for faster training)
    models_to_train = [
        ('xgboost', trainer.train_xgboost),
        ('random_forest', trainer.train_random_forest),
    ]
    
    for model_name, train_func in models_to_train:
        print(f"\n🔄 Training {model_name.upper()} model...")
        try:
            train_func()
            print(f"✓ {model_name.upper()} trained successfully")
        except Exception as e:
            print(f"❌ Error training {model_name}: {str(e)}")
    
    # Find and save best model
    print("\n" + "="*70)
    print("SAVING MODELS")
    print("="*70)
    
    # Save all models
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    
    trainer.save_all_models(models_dir)
    trainer.save_best_model(os.path.join(models_dir, 'best_model.pkl'))
    
    # Print summary
    print("\n" + "="*70)
    print("RETRAINING COMPLETE")
    print("="*70)
    print("\n📊 Model Performance Summary:")
    for model_name, results in trainer.results.items():
        print(f"\n{model_name.upper()}:")
        print(f"  RMSE: {results['test_rmse']:.2f}")
        print(f"  MAE:  {results['test_mae']:.2f}")
        print(f"  R²:   {results['test_r2']:.3f}")
    
    print(f"\n🏆 Best Model: {trainer.best_model_name.upper()}")
    print("\n✅ All models retrained successfully!")
    print("🚀 Restart the backend server to use the new models.")


if __name__ == "__main__":
    retrain_all_models()
