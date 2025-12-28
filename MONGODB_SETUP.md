# MongoDB Setup for CricNex

## Installation

### Windows

1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select Windows version
   - Download and run the installer

2. **Install MongoDB**
   - Choose "Complete" installation
   - Install as a Service (recommended)
   - Default installation path: `C:\Program Files\MongoDB\Server\7.0\`

3. **Verify Installation**
   ```powershell
   # Check if MongoDB service is running
   Get-Service -Name MongoDB
   
   # Connect to MongoDB
   mongosh
   ```

### Alternative: MongoDB Atlas (Cloud)

If you prefer cloud-hosted MongoDB:

1. Create free account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Set environment variable:
   ```powershell
   $env:MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/"
   ```

## Python Package Installation

```bash
pip install pymongo
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Configuration

### Local MongoDB (Default)

No configuration needed! The application will automatically connect to:
```
mongodb://localhost:27017/
```

Database name: `cricnex`

### Custom MongoDB Connection

Set environment variable before starting the server:

**PowerShell:**
```powershell
$env:MONGODB_URI="mongodb://localhost:27017/"
python src/backend.py
```

**Bash:**
```bash
export MONGODB_URI="mongodb://localhost:27017/"
python src/backend.py
```

## Database Structure

### Collections

1. **predictions** - Stores all predictions made by the system
   - Fields: player, team, opponent, venue, model_name, predicted_runs, predicted_strike_rate, confidence, created_at

2. **player_analytics** - Stores aggregated player statistics
   - Fields: player, total_matches, total_runs, avg_runs, avg_strike_rate, highest_score, updated_at

3. **match_analytics** - Stores match-level analytics (optional)
   - Fields: match_id, date, teams, venue, predictions, created_at

## Testing MongoDB Connection

### Test Script

Create `test_mongodb.py`:
```python
from src.mongo_handler import MongoDBHandler

# Test connection
handler = MongoDBHandler()

if handler.is_connected():
    print("✅ MongoDB connected successfully!")
    
    # Test saving a prediction
    test_data = {
        'player': 'V Kohli',
        'team': 'Royal Challengers Bangalore',
        'opponent': 'Mumbai Indians',
        'venue': 'M Chinnaswamy Stadium',
        'model_name': 'xgboost',
        'predicted_runs': 45.5,
        'predicted_strike_rate': 138.2,
        'confidence': 0.85
    }
    
    pred_id = handler.save_prediction(test_data)
    print(f"✅ Test prediction saved: {pred_id}")
    
    # Get stats
    stats = handler.get_prediction_stats()
    print(f"📊 Total predictions: {stats.get('total_predictions', 0)}")
    
    handler.close()
else:
    print("❌ MongoDB connection failed")
    print("\n💡 Make sure MongoDB is installed and running:")
    print("   - Check service: Get-Service -Name MongoDB")
    print("   - Or install: https://www.mongodb.com/try/download/community")
```

Run test:
```bash
python test_mongodb.py
```

## API Endpoints

Once MongoDB is configured, new endpoints are available:

### Prediction History
- `GET /api/mongo/predictions/recent?limit=50` - Get recent predictions
- `GET /api/mongo/predictions/player/<name>?limit=20` - Get player prediction history
- `GET /api/mongo/predictions/stats` - Get prediction statistics

### Player Analytics
- `GET /api/mongo/analytics/player/<name>` - Get player analytics from MongoDB
- `GET /api/mongo/analytics/all?limit=100` - Get all player analytics

### Status
- `GET /api/mongo/status` - Check MongoDB connection status

## Usage Examples

### Check MongoDB Status
```bash
curl http://localhost:5000/api/mongo/status
```

### Get Recent Predictions
```bash
curl http://localhost:5000/api/mongo/predictions/recent?limit=10
```

### Get Player Analytics
```bash
curl http://localhost:5000/api/mongo/analytics/player/V%20Kohli
```

### Get Prediction Stats
```bash
curl http://localhost:5000/api/mongo/predictions/stats
```

## Viewing Data

### Using MongoDB Compass (GUI)

1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect to: `mongodb://localhost:27017`
3. Browse `cricnex` database

### Using MongoDB Shell

```bash
# Connect to MongoDB
mongosh

# Switch to cricnex database
use cricnex

# View collections
show collections

# Query predictions
db.predictions.find().limit(10)

# Query player analytics
db.player_analytics.find()

# Get count
db.predictions.countDocuments()

# Find specific player
db.predictions.find({player: "V Kohli"})
```

## Troubleshooting

### MongoDB Not Running

**Check Service:**
```powershell
Get-Service -Name MongoDB
```

**Start Service:**
```powershell
Start-Service -Name MongoDB
```

### Connection Issues

1. Verify MongoDB is running on port 27017
2. Check firewall settings
3. Ensure MongoDB service is started
4. Try connecting with MongoDB Compass

### Backend Runs Without MongoDB

The application is designed to work with or without MongoDB:
- ✅ **With MongoDB**: Predictions are saved to database
- ✅ **Without MongoDB**: Predictions work normally, just not saved

You'll see this message if MongoDB is unavailable:
```
⚠ MongoDB handler not available
```

Or:
```
⚠ MongoDB connection failed
  Continuing without MongoDB...
```

## Benefits of MongoDB Integration

✅ **Prediction History** - Track all predictions made over time
✅ **Analytics** - Analyze model performance and prediction patterns
✅ **Player Tracking** - See prediction trends for each player
✅ **Audit Trail** - Complete record of all predictions
✅ **Insights** - Identify most-predicted players, popular matchups

## Optional: Disable MongoDB

If you don't want to use MongoDB, simply don't install pymongo:

```bash
# The application will work fine without it
# You'll just see a warning message
```

Or set environment variable:
```powershell
$env:DISABLE_MONGODB="true"
```
