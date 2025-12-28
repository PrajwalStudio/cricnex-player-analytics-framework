"""
CricNex - Project Health Check Script
Verifies all components are working correctly
"""

import sys
import os
import importlib.util

def check_color(passed):
    """Return color code for pass/fail"""
    return "✅" if passed else "❌"

def check_python_packages():
    """Check if all required Python packages are installed"""
    print("\n" + "="*70)
    print("CHECKING PYTHON PACKAGES")
    print("="*70)
    
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'flask': 'flask',
        'flask_cors': 'flask-cors',
        'joblib': 'joblib',
        'pymongo': 'pymongo'
    }
    
    all_passed = True
    for package, pip_name in required_packages.items():
        spec = importlib.util.find_spec(package)
        passed = spec is not None
        all_passed = all_passed and passed
        print(f"{check_color(passed)} {pip_name:20s} - {'Installed' if passed else 'MISSING'}")
    
    return all_passed

def check_project_files():
    """Check if all required project files exist"""
    print("\n" + "="*70)
    print("CHECKING PROJECT FILES")
    print("="*70)
    
    required_files = [
        'src/backend.py',
        'src/api.py',
        'src/data_loader.py',
        'src/feature_engineering.py',
        'src/model_training.py',
        'src/main.py',
        'src/mongo_handler.py',
        'requirements.txt',
        'README.md',
        'clean_and_retrain.py'
    ]
    
    all_passed = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        all_passed = all_passed and exists
        print(f"{check_color(exists)} {file_path:40s} - {'Found' if exists else 'MISSING'}")
    
    return all_passed

def check_data_files():
    """Check if data files exist"""
    print("\n" + "="*70)
    print("CHECKING DATA FILES")
    print("="*70)
    
    data_files = [
        'ballbyball/deliveries_updated_mens_ipl_upto_2024.csv',
        'ballbyball/matches_updated_mens_ipl_upto_2024.csv',
        'data/features.csv'
    ]
    
    all_passed = True
    for file_path in data_files:
        exists = os.path.exists(file_path)
        all_passed = all_passed and exists
        if exists:
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"{check_color(exists)} {file_path:50s} - {size:.1f} MB")
        else:
            print(f"{check_color(exists)} {file_path:50s} - MISSING")
    
    return all_passed

def check_model_files():
    """Check if trained models exist"""
    print("\n" + "="*70)
    print("CHECKING MODEL FILES")
    print("="*70)
    
    model_files = [
        'models/xgboost.pkl',
        'models/random_forest.pkl',
        'models/best_model.pkl'
    ]
    
    all_passed = False  # At least one model should exist
    for file_path in model_files:
        exists = os.path.exists(file_path)
        if exists:
            all_passed = True
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"{check_color(exists)} {file_path:40s} - {size:.1f} MB")
        else:
            print(f"⚠️  {file_path:40s} - Not found")
    
    return all_passed

def check_frontend_files():
    """Check if frontend files exist"""
    print("\n" + "="*70)
    print("CHECKING FRONTEND FILES")
    print("="*70)
    
    frontend_files = [
        'frontend/package.json',
        'frontend/src/App.js',
        'frontend/src/pages/Dashboard.js',
        'frontend/src/pages/Prediction.js',
        'frontend/src/pages/Players.js',
        'frontend/src/pages/Leaderboard.js',
        'frontend/src/pages/Teams.js',
        'frontend/src/pages/Analytics.js',
        'frontend/src/services/api.js',
        'frontend/src/components/Layout.js',
        'frontend/src/components/StatCard.js'
    ]
    
    all_passed = True
    for file_path in frontend_files:
        exists = os.path.exists(file_path)
        all_passed = all_passed and exists
        print(f"{check_color(exists)} {file_path:50s} - {'Found' if exists else 'MISSING'}")
    
    return all_passed

def check_mongodb_connection():
    """Check MongoDB connection (optional)"""
    print("\n" + "="*70)
    print("CHECKING MONGODB CONNECTION (OPTIONAL)")
    print("="*70)
    
    try:
        from src.mongo_handler import MongoDBHandler
        handler = MongoDBHandler()
        connected = handler.is_connected()
        
        if connected:
            stats = handler.get_prediction_stats()
            print(f"✅ MongoDB Connected")
            print(f"   - Total Predictions: {stats.get('total_predictions', 0)}")
            print(f"   - Unique Players: {stats.get('unique_players', 0)}")
            handler.close()
        else:
            print("⚠️  MongoDB Not Connected (Optional - predictions will still work)")
        
        return True  # Not critical
    except Exception as e:
        print(f"⚠️  MongoDB Check Failed: {e}")
        print("   (This is optional - application will work without MongoDB)")
        return True  # Not critical

def test_backend_import():
    """Test if backend can be imported"""
    print("\n" + "="*70)
    print("TESTING BACKEND IMPORT")
    print("="*70)
    
    try:
        sys.path.insert(0, 'src')
        from backend import CricNexBackend
        print("✅ Backend imports successfully")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def main():
    """Run all checks"""
    print("\n" + "="*70)
    print("CRICNEX PROJECT HEALTH CHECK")
    print("="*70)
    print("Running comprehensive system check...\n")
    
    results = {
        'Python Packages': check_python_packages(),
        'Project Files': check_project_files(),
        'Data Files': check_data_files(),
        'Model Files': check_model_files(),
        'Frontend Files': check_frontend_files(),
        'Backend Import': test_backend_import(),
        'MongoDB': check_mongodb_connection()
    }
    
    # Summary
    print("\n" + "="*70)
    print("HEALTH CHECK SUMMARY")
    print("="*70)
    
    for check_name, passed in results.items():
        print(f"{check_color(passed)} {check_name:25s} - {'PASSED' if passed else 'FAILED'}")
    
    critical_checks = ['Python Packages', 'Project Files', 'Data Files', 'Backend Import']
    critical_passed = all(results[check] for check in critical_checks if check in results)
    
    print("\n" + "="*70)
    if critical_passed:
        print("✅ ALL CRITICAL CHECKS PASSED")
        print("="*70)
        print("\n✨ Your CricNex project is ready!")
        print("\n📋 Next Steps:")
        print("   1. Start servers: .\\start_servers.ps1")
        print("   2. Access frontend: http://localhost:3001")
        print("   3. Access API: http://localhost:5000/api/health")
        
        if not results.get('Model Files', False):
            print("\n⚠️  Note: No models found. Run: python src/main.py")
        
        return 0
    else:
        print("❌ SOME CRITICAL CHECKS FAILED")
        print("="*70)
        print("\n⚠️  Please fix the issues above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
