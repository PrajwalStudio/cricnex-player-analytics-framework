"""
CricNex - MongoDB Handler
Store and retrieve player analytics and prediction history
"""

from pymongo import MongoClient, DESCENDING
from datetime import datetime, timezone
from typing import Dict, List, Optional
import os


class MongoDBHandler:
    """
    MongoDB handler for storing player analytics and predictions
    """
    
    def __init__(self, connection_string: str = None, database_name: str = "cricnex"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (defaults to localhost)
            database_name: Database name to use
        """
        if connection_string is None:
            connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            
            # Collections
            self.predictions = self.db['predictions']
            self.player_analytics = self.db['player_analytics']
            self.match_analytics = self.db['match_analytics']
            
            # Create indexes for better performance
            self._create_indexes()
            
            print(f"✓ MongoDB connected: {database_name}")
            
        except Exception as e:
            print(f"⚠ MongoDB connection failed: {e}")
            print("  Continuing without MongoDB...")
            self.client = None
            self.db = None
    
    def _create_indexes(self):
        """Create indexes for faster queries"""
        if self.db is None:
            return
        
        try:
            # Predictions indexes
            self.predictions.create_index([('player', 1)])
            self.predictions.create_index([('created_at', DESCENDING)])
            self.predictions.create_index([('team', 1)])
            
            # Player analytics indexes
            self.player_analytics.create_index([('player', 1)], unique=True)
            self.player_analytics.create_index([('updated_at', DESCENDING)])
            
            # Match analytics indexes
            self.match_analytics.create_index([('match_id', 1)])
            self.match_analytics.create_index([('date', DESCENDING)])
            
        except Exception as e:
            print(f"⚠ Error creating indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self.client is not None and self.db is not None
    
    # ==================== PREDICTION HISTORY ====================
    
    def save_prediction(self, prediction_data: Dict) -> Optional[str]:
        """
        Save prediction to MongoDB
        
        Args:
            prediction_data: Dictionary containing prediction details
            
        Returns:
            Inserted document ID or None if failed
        """
        if not self.is_connected():
            return None
        
        try:
            document = {
                'player': prediction_data['player'],
                'team': prediction_data['team'],
                'opponent': prediction_data['opponent'],
                'venue': prediction_data['venue'],
                'model_name': prediction_data.get('model_name', 'xgboost'),
                'predicted_runs': prediction_data['predicted_runs'],
                'predicted_strike_rate': prediction_data.get('predicted_strike_rate', 0),
                'confidence': prediction_data.get('confidence', 0),
                'factors': prediction_data.get('factors', {}),
                'created_at': datetime.now(timezone.utc)
            }
            
            result = self.predictions.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return None
    
    def get_recent_predictions(self, limit: int = 50) -> List[Dict]:
        """Get recent predictions"""
        if not self.is_connected():
            return []
        
        try:
            predictions = self.predictions.find().sort('created_at', DESCENDING).limit(limit)
            
            results = []
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
                results.append(pred)
            
            return results
            
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    def get_player_predictions(self, player_name: str, limit: int = 20) -> List[Dict]:
        """Get predictions for specific player"""
        if not self.is_connected():
            return []
        
        try:
            predictions = self.predictions.find(
                {'player': player_name}
            ).sort('created_at', DESCENDING).limit(limit)
            
            results = []
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
                results.append(pred)
            
            return results
            
        except Exception as e:
            print(f"Error fetching player predictions: {e}")
            return []
    
    def get_prediction_stats(self) -> Dict:
        """Get overall prediction statistics"""
        if not self.is_connected():
            return {}
        
        try:
            total_predictions = self.predictions.count_documents({})
            
            unique_players = len(self.predictions.distinct('player'))
            unique_models = len(self.predictions.distinct('model_name'))
            
            # Model usage stats
            pipeline = [
                {'$group': {'_id': '$model_name', 'count': {'$sum': 1}}}
            ]
            model_counts = list(self.predictions.aggregate(pipeline))
            models_dict = {item['_id']: item['count'] for item in model_counts}
            
            return {
                'total_predictions': total_predictions,
                'unique_players': unique_players,
                'models_used': unique_models,
                'predictions_by_model': models_dict
            }
            
        except Exception as e:
            print(f"Error fetching prediction stats: {e}")
            return {}
    
    # ==================== PLAYER ANALYTICS ====================
    
    def update_player_analytics(self, player_name: str, analytics_data: Dict) -> bool:
        """
        Update or create player analytics
        
        Args:
            player_name: Player name
            analytics_data: Analytics data to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            document = {
                'player': player_name,
                'total_predictions': analytics_data.get('total_predictions', 0),
                'avg_predicted_runs': analytics_data.get('avg_predicted_runs', 0),
                'avg_predicted_sr': analytics_data.get('avg_predicted_sr', 0),
                'matches_analyzed': analytics_data.get('matches_analyzed', 0),
                'total_runs': analytics_data.get('total_runs', 0),
                'total_matches': analytics_data.get('total_matches', 0),
                'avg_runs': analytics_data.get('avg_runs', 0),
                'avg_strike_rate': analytics_data.get('avg_strike_rate', 0),
                'highest_score': analytics_data.get('highest_score', 0),
                'form_trend': analytics_data.get('form_trend', []),
                'venue_stats': analytics_data.get('venue_stats', {}),
                'opponent_stats': analytics_data.get('opponent_stats', {}),
                'updated_at': datetime.now(timezone.utc)
            }
            
            self.player_analytics.update_one(
                {'player': player_name},
                {'$set': document},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating player analytics: {e}")
            return False
    
    def get_player_analytics(self, player_name: str) -> Optional[Dict]:
        """Get player analytics"""
        if not self.is_connected():
            return None
        
        try:
            analytics = self.player_analytics.find_one({'player': player_name})
            
            if analytics:
                analytics['_id'] = str(analytics['_id'])
                return analytics
            
            return None
            
        except Exception as e:
            print(f"Error fetching player analytics: {e}")
            return None
    
    def get_all_player_analytics(self, limit: int = 100) -> List[Dict]:
        """Get analytics for all players"""
        if not self.is_connected():
            return []
        
        try:
            analytics = self.player_analytics.find().sort('updated_at', DESCENDING).limit(limit)
            
            results = []
            for player in analytics:
                player['_id'] = str(player['_id'])
                results.append(player)
            
            return results
            
        except Exception as e:
            print(f"Error fetching all player analytics: {e}")
            return []
    
    # ==================== MATCH ANALYTICS ====================
    
    def save_match_analytics(self, match_data: Dict) -> Optional[str]:
        """Save match analytics"""
        if not self.is_connected():
            return None
        
        try:
            document = {
                'match_id': match_data.get('match_id'),
                'date': match_data.get('date'),
                'team1': match_data.get('team1'),
                'team2': match_data.get('team2'),
                'venue': match_data.get('venue'),
                'total_predictions': match_data.get('total_predictions', 0),
                'player_performances': match_data.get('player_performances', []),
                'created_at': datetime.now(timezone.utc)
            }
            
            result = self.match_analytics.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error saving match analytics: {e}")
            return None
    
    def get_match_analytics(self, match_id: str) -> Optional[Dict]:
        """Get analytics for specific match"""
        if not self.is_connected():
            return None
        
        try:
            match = self.match_analytics.find_one({'match_id': match_id})
            
            if match:
                match['_id'] = str(match['_id'])
                return match
            
            return None
            
        except Exception as e:
            print(f"Error fetching match analytics: {e}")
            return None
    
    # ==================== CLEANUP ====================
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")


if __name__ == "__main__":
    # Test MongoDB connection
    handler = MongoDBHandler()
    
    if handler.is_connected():
        print("\n✅ MongoDB connection successful!")
        
        # Test saving a prediction
        test_prediction = {
            'player': 'V Kohli',
            'team': 'Royal Challengers Bangalore',
            'opponent': 'Mumbai Indians',
            'venue': 'M Chinnaswamy Stadium',
            'model_name': 'xgboost',
            'predicted_runs': 45.5,
            'predicted_strike_rate': 138.2,
            'confidence': 0.85
        }
        
        pred_id = handler.save_prediction(test_prediction)
        print(f"✓ Test prediction saved with ID: {pred_id}")
        
        # Get stats
        stats = handler.get_prediction_stats()
        print(f"✓ Total predictions in DB: {stats.get('total_predictions', 0)}")
        
        handler.close()
    else:
        print("\n❌ MongoDB not available")
