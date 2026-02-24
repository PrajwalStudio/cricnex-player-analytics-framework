"""
CricNex - API Module
Flask REST API for cricket player performance prediction
"""

import os
import sys

# Add src to path
sys.path.append(os.path.dirname(__file__))

from backend import create_backend


def create_api():
    """
    Create and configure API instance
    
    Returns:
        CricNexBackend instance
    """
    # Determine paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    model_path = os.path.join(project_root, "models", "best_model.pkl")
    features_path = os.path.join(project_root, "data", "features.csv")
    models_dir = os.path.join(project_root, "models")
    
    # Check if model exists
    if not os.path.exists(model_path):
        print("\nWarning: Model not found!")
        print(f"   Looking for: {model_path}")
        print("\nPlease run the training pipeline first:")
        print("   python src/main.py")
        print("\nThis will:")
        print("   1. Load and process IPL data")
        print("   2. Engineer features")
        print("   3. Train all models")
        print("   4. Save best model to models/best_model.pkl")
        
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
            if model_files:
                print(f"\nFound these models: {', '.join(model_files)}")
                model_path = os.path.join(models_dir, model_files[0])
                print(f"Using: {model_path}")
        else:
            print("\nNo models directory found. Please run: python src/main.py")
            sys.exit(1)
    
    # Create backend
    backend = create_backend(model_path, features_path, models_dir)
    
    return backend


if __name__ == "__main__":
    print("="*70)
    print("CRICNEX API SERVER")
    print("="*70)
    print("")
    
    # Create API
    api = create_api()
    
    print("\nAPI Server Ready!")
    print("\nServer Information:")
    print("   URL: http://localhost:5000")
    print("   Status: Running")
    print("\nAvailable Endpoints:")
    print("   GET  /api/health              - Health check")
    print("   GET  /api/model/info          - Model information")
    print("   GET  /api/models              - List all models")
    print("   POST /api/predict             - Make prediction")
    print("   POST /api/predict/batch       - Batch predictions")
    print("   GET  /api/players             - Get all players")
    print("   GET  /api/player/<name>       - Get player stats")
    print("   GET  /api/teams               - Get all teams")
    print("   GET  /api/venues              - Get all venues")
    print("   GET  /api/stats/overview      - Overall statistics")
    print("   GET  /api/stats/leaderboard   - Player leaderboard")
    print("\nTesting:")
    print("   Run test script: python test_api.py")
    print("   Manual test: curl http://localhost:5000/api/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    print("")
    
    # Run server
    api.run(host='0.0.0.0', port=5000, debug=False)
