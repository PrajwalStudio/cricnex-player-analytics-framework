# CricNex - Cricket Player Performance Prediction System

## 📊 Project Overview

**CricNex** is a production-ready machine learning system that predicts cricket player performance in the Indian Premier League (IPL) using historical data from 2008-2024. The system implements multiple ML algorithms and provides predictions through a REST API.

## 🎯 Objectives

Predict player performance metrics:
- **Runs Scored**: Expected runs in next match
- **Strike Rate**: Batting strike rate
- **Wickets Taken**: Expected wickets (for bowlers)

## ✨ Key Features

- **Multiple ML Models**: Choose from 4 trained models (XGBoost, Random Forest, LSTM, ARIMA)
- **Model Selection**: Select which model to use via API or frontend UI
- **Real-time Predictions**: REST API with 18 endpoints
- **Interactive Dashboard**: React-based frontend with 6 pages
- **Comprehensive Analytics**: Player stats, team analysis, venue insights
- **Model Comparison**: Compare predictions across different algorithms

## 📁 Project Structure

```
CRICNEX/
├── ballbyball/
│   ├── deliveries_updated_mens_ipl_upto_2024.csv
│   └── matches_updated_mens_ipl_upto_2024.csv
├── src/
│   ├── data_loader.py          # Data loading and preprocessing
│   ├── feature_engineering.py  # Feature creation
│   ├── model_training.py       # Model training and evaluation
│   ├── api.py                  # Flask REST API
│   └── main.py                 # Main pipeline orchestrator
├── models/                     # Trained models (generated)
├── data/                       # Processed features (generated)
├── results/                    # Model comparison results (generated)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd CRICNEX
pip install -r requirements.txt
```

### 2. Run Complete Pipeline

```bash
python src/main.py
```

This executes:
- ✅ Data loading and merging
- ✅ Feature engineering
- ✅ Training 4 models (Random Forest, XGBoost, ARIMA, LSTM)
- ✅ Model evaluation and comparison
- ✅ Best model selection and saving

### 3. Start API Server

```bash
python src/api.py
```

Server runs on `http://localhost:5000`

### 4. Test Predictions

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Make Prediction:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "player": "V Kohli",
    "team": "Royal Challengers Bangalore",
    "opponent": "Mumbai Indians",
    "venue": "M Chinnaswamy Stadium",
    "model_name": "xgboost",
    "runs_last_5_avg": 45.5,
    "strike_rate_last_5": 140.2,
    "batting_position": 3
  }'
```

**Response:**
```json
{
  "player": "V Kohli",
  "team": "Royal Challengers Bangalore",
  "opponent": "Mumbai Indians",
  "venue": "M Chinnaswamy Stadium",
  "predicted_runs": 42.5,
  "predicted_strike_rate": 138.4,
  "predicted_wickets": 0.0,
  "confidence": "high",
  "model_used": "xgboost"
}
```

**Choose Different Model:**
```bash
# Available models: xgboost, random_forest, lstm, arima
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "player": "V Kohli",
    "team": "Royal Challengers Bangalore",
    "opponent": "Mumbai Indians",
    "venue": "M Chinnaswamy Stadium",
    "model_name": "random_forest"
  }'
```

## 🔬 Technical Implementation

### Step 1: Data Loading & Merging

**Module:** `data_loader.py`

- Loads ball-by-ball deliveries (260,922 records)
- Loads match metadata (1,097 matches)
- Merges datasets on `matchId`
- Handles missing values:
  - Categorical: Mode/Unknown
  - Numeric: 0 or group-based mean
- Removes irrelevant columns

### Step 2: Feature Engineering

**Module:** `feature_engineering.py`

**Created Features:**

| Feature | Description |
|---------|-------------|
| `runs_last_5_avg` | Average runs in last 5 matches |
| `strike_rate_last_5` | Average strike rate in last 5 matches |
| `wickets_last_5_avg` | Average wickets in last 5 matches |
| `venue_avg_runs` | Average runs at venue |
| `opponent_avg_runs` | Average runs against opponent |
| `venue_avg_strike_rate` | Average strike rate at venue |
| `opponent_avg_strike_rate` | Average strike rate vs opponent |
| `is_home_match` | Binary indicator for home venue |
| `batting_position` | Estimated batting order position |
| `player_encoded` | Label-encoded player ID |
| `team_encoded` | Label-encoded team ID |
| `opponent_encoded` | Label-encoded opponent ID |
| `venue_encoded` | Label-encoded venue ID |

### Step 3: Dataset Preparation

- **Train-Test Split:** 80-20
- **Scaling:** StandardScaler for numeric features
- **Sequence Creation:** Rolling windows for LSTM

### Step 4: Model Training

#### All 4 Models Available

The system includes 4 trained ML models with model selection capability:

#### 1. XGBoost Regressor ⭐ (Default - Best Performance)
- **Hyperparameters:** 100 estimators, learning_rate=0.1
- **RMSE:** 20.68 | **MAE:** 15.58 | **R²:** 0.065
- **Strengths:** Gradient boosting, best accuracy, feature importance

#### 2. Random Forest Regressor
- **Hyperparameters:** 100 trees, max_depth=20
- **RMSE:** 20.84 | **MAE:** 15.91 | **R²:** 0.051
- **Strengths:** Handles non-linear relationships, robust to outliers

#### 3. LSTM Neural Network
- **Architecture:** 64→32 LSTM units + Dense layers
- **Sequence Length:** 5 matches
- **RMSE:** 22.17 | **MAE:** 16.12 | **R²:** 0.029
- **Strengths:** Sequential dependency modeling, captures time patterns

#### 4. ARIMA Time Series
- **Order:** (1,1,1)
- **Applied to:** Top 20 players by runs
- **RMSE:** 24.74 | **MAE:** 20.28 | **R²:** 0.015
- **Strengths:** Captures temporal patterns, statistical baseline

**Model Selection:** Users can choose which model to use via API parameter or frontend dropdown

### Step 5: Evaluation Metrics

All models evaluated using:

| Metric | Description |
|--------|-------------|
| **MAE** | Mean Absolute Error |
| **RMSE** | Root Mean Squared Error |
| **R²** | R-squared Score |

### Step 6: Model Selection

- **Selection Criteria:** Lowest RMSE on test set
- **Saved Artifacts:**
  - Best model (`.pkl`)
  - Scaler
  - Metrics
  - Model metadata

## 📈 API Endpoints

### `GET /`
Returns API information and available endpoints

### `GET /health`
Health check for deployment monitoring

### `GET /model_info`
Returns loaded model details and performance metrics

### `POST /predict`
Single player prediction

**Required Fields:**
- `player`: Player name
- `team`: Player's team
- `opponent`: Opposing team
- `venue`: Match venue

**Optional Fields:**
- `runs_last_5_avg`: Recent form
- `strike_rate_last_5`: Recent strike rate
- `batting_position`: Order position
- `is_home_match`: 0 or 1

### `POST /predict_batch`
Batch predictions for multiple players

## 🧪 Example Usage (Python)

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/predict"

# Prediction request
payload = {
    "player": "MS Dhoni",
    "team": "Chennai Super Kings",
    "opponent": "Royal Challengers Bangalore",
    "venue": "M. A. Chidambaram Stadium",
    "runs_last_5_avg": 32.4,
    "strike_rate_last_5": 155.8,
    "batting_position": 6,
    "is_home_match": 1
}

# Make request
response = requests.post(url, json=payload)
result = response.json()

print(f"Predicted Runs: {result['predicted_runs']:.2f}")
print(f"Predicted Strike Rate: {result['predicted_strike_rate']:.2f}")
print(f"Confidence: {result['confidence']}")
```

## 📊 Model Performance Comparison

After training, the system generates a comparison table:

```
Model              Test MAE    Test RMSE    Test R²
Random Forest      8.5432      12.3456      0.7234
XGBoost            7.8921      11.5678      0.7456
ARIMA              9.2341      13.2109      0.6987
LSTM               8.1234      11.9876      0.7321
```

*(Example metrics - actual values generated during training)*

## 🎓 Academic Features

### Code Quality
- ✅ Modular design (separate modules for each component)
- ✅ Comprehensive docstrings
- ✅ Type hints for function parameters
- ✅ PEP 8 compliant
- ✅ Error handling and validation

### Documentation
- ✅ Inline comments explaining logic
- ✅ Function-level documentation
- ✅ Pipeline step descriptions
- ✅ API endpoint documentation

### Best Practices
- ✅ Train-test split for validation
- ✅ Feature scaling
- ✅ Cross-validation ready
- ✅ Model persistence
- ✅ RESTful API design

## 🔧 Configuration

### Hyperparameter Tuning

Edit `src/main.py` to modify model parameters:

```python
# Random Forest
trainer.train_random_forest(n_estimators=150, max_depth=25)

# XGBoost
trainer.train_xgboost(n_estimators=200, learning_rate=0.05)

# LSTM
trainer.train_lstm(sequence_length=10, epochs=50, batch_size=64)
```

### Feature Selection

Edit `src/model_training.py` to modify features:

```python
feature_columns = [
    'player_encoded', 'team_encoded', 'opponent_encoded', 'venue_encoded',
    'runs_last_5_avg', 'strike_rate_last_5',
    # Add more features here
]
```

## 📦 Output Files

### `models/best_model.pkl`
Serialized best-performing model with metadata

### `data/features.csv`
Complete feature-engineered dataset

### `results/model_comparison.csv`
Performance comparison of all trained models

## 🐛 Troubleshooting

### Issue: "Model not loaded"
**Solution:** Run `python src/main.py` first to train and save models

### Issue: Low prediction accuracy
**Solution:** 
- Increase training data
- Tune hyperparameters
- Add more features
- Increase LSTM epochs

### Issue: API connection refused
**Solution:** Check if Flask server is running on port 5000

## 🚀 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.api:create_api().app
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/api.py"]
```

## 📝 Future Enhancements

- [ ] Real-time data updates
- [ ] Player comparison feature
- [ ] Historical trend visualization
- [ ] Ensemble model stacking
- [ ] Hyperparameter optimization (Grid Search)
- [ ] Player form decay modeling
- [ ] Weather and pitch condition features

## 👥 Contributors

Developed following SRS specifications for academic evaluation

## 📄 License

Educational project - IPL datasets used for academic purposes

## 🙏 Acknowledgments

- **Data Source:** Kaggle IPL Datasets (2008-2024)
- **Frameworks:** scikit-learn, XGBoost, TensorFlow, Flask
- **Inspired by:** Cricket analytics and sports prediction research

---

**CricNex** - Predicting Cricket Excellence with Machine Learning 🏏
