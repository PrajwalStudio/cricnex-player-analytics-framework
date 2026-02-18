"""
CricNex WSGI entry point for production deployment (Gunicorn)
"""
import os
import sys

# Ensure src is on the path
sys.path.insert(0, os.path.dirname(__file__))

from backend import create_backend

# Resolve paths relative to project root (one level above src/)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

backend = create_backend(
    model_path=os.path.join(ROOT, "models", "best_model.pkl"),
    features_path=os.path.join(ROOT, "data", "features.csv"),
    models_dir=os.path.join(ROOT, "models"),
)

# Expose the Flask app for gunicorn
app = backend.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
