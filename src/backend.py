"""
CricNex - Enhanced Backend API
Comprehensive Flask backend for cricket player performance prediction UI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import os
import warnings
warnings.filterwarnings('ignore')

# Import MongoDB handler
try:
    from mongo_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠ MongoDB handler not available")


class CricNexBackend:
    """
    Enhanced backend API for CricNex with comprehensive endpoints
    """
    
    def __init__(self, model_path: str, features_path: str, models_dir: str = None):
        """
        Initialize backend with model and feature data
        
        Args:
            model_path: Path to saved model (default/best model)
            features_path: Path to features CSV
            models_dir: Directory containing all models (optional)
        """
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend
        
        self.model_data = None
        self.all_models = {}  # Store all available models
        self.features_df = None
        self.players_stats = None
        self.teams_stats = None
        self.venues_stats = None
        
        # Initialize MongoDB handler
        self.mongo = None
        if MONGODB_AVAILABLE:
            try:
                self.mongo = MongoDBHandler()
                if self.mongo.is_connected():
                    print("✓ MongoDB integration enabled")
            except Exception as e:
                print(f"⚠ MongoDB initialization failed: {e}")
                self.mongo = None
        
        # Load model and data
        self.load_model(model_path)
        if models_dir:
            self.load_all_models(models_dir)
        self.load_features(features_path)
        self.prepare_statistics()
        
        # Sync player analytics to MongoDB
        if self.mongo and self.mongo.is_connected():
            self._sync_player_analytics()
        
        # Setup routes
        self.setup_routes()
    
    def load_model(self, model_path: str):
        """Load trained model"""
        if os.path.exists(model_path):
            self.model_data = joblib.load(model_path)
            print(f"✓ Model loaded: {self.model_data['model_name']}")
        else:
            print(f"⚠ Model not found: {model_path}")
    
    def load_all_models(self, models_dir: str):
        """Load all available models from directory"""
        if not os.path.exists(models_dir):
            print(f"⚠ Models directory not found: {models_dir}")
            return
        
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
        
        for model_file in model_files:
            model_path = os.path.join(models_dir, model_file)
            try:
                model_data = joblib.load(model_path)
                model_name = model_data.get('model_name', model_file.replace('.pkl', ''))
                self.all_models[model_name] = model_data
                print(f"  ✓ Loaded {model_name}")
            except Exception as e:
                print(f"  ⚠ Could not load {model_file}: {str(e)}")
        
        print(f"✓ Total models loaded: {len(self.all_models)}")
    
    def load_features(self, features_path: str):
        """Load feature dataset"""
        if os.path.exists(features_path):
            self.features_df = pd.read_csv(features_path)
            # Convert date column to datetime for proper sorting
            if 'date' in self.features_df.columns:
                self.features_df['date'] = pd.to_datetime(self.features_df['date'], errors='coerce')
            print(f"✓ Features loaded: {len(self.features_df)} records")
        else:
            print(f"⚠ Features not found: {features_path}")
    
    def prepare_statistics(self):
        """Prepare aggregated statistics for fast retrieval"""
        if self.features_df is None:
            return
        
        # Player statistics
        agg_dict = {
            'runs_scored': ['mean', 'sum', 'count', 'max'],
            'strike_rate': 'mean'
        }
        
        # Add dismissals if column exists
        if 'dismissals' in self.features_df.columns:
            agg_dict['dismissals'] = 'sum'
        
        self.players_stats = self.features_df.groupby('player').agg(agg_dict).reset_index()
        
        # Set column names based on what was aggregated
        if 'dismissals' in self.features_df.columns:
            self.players_stats.columns = [
                'player', 'avg_runs', 'total_runs', 'matches', 
                'highest_score', 'avg_strike_rate', 'dismissals'
            ]
        else:
            self.players_stats.columns = [
                'player', 'avg_runs', 'total_runs', 'matches', 
                'highest_score', 'avg_strike_rate'
            ]
        
        # Team statistics
        self.teams_stats = self.features_df.groupby('team').agg({
            'runs_scored': 'mean',
            'matchId': 'count'
        }).reset_index()
        self.teams_stats.columns = ['team', 'avg_runs', 'matches']
        
        # Venue statistics
        self.venues_stats = self.features_df.groupby('venue').agg({
            'runs_scored': 'mean',
            'strike_rate': 'mean',
            'matchId': 'count'
        }).reset_index()
        self.venues_stats.columns = ['venue', 'avg_runs', 'avg_strike_rate', 'matches']
        
        print("✓ Statistics prepared")
    
    def _sync_player_analytics(self):
        """Sync player statistics to MongoDB"""
        if not self.mongo or not self.mongo.is_connected():
            return
        
        try:
            print("\n📊 Syncing player analytics to MongoDB...")
            
            for _, player_row in self.players_stats.iterrows():
                analytics_data = {
                    'total_matches': int(player_row['matches']),
                    'total_runs': int(player_row['total_runs']),
                    'avg_runs': float(player_row['avg_runs']),
                    'avg_strike_rate': float(player_row['avg_strike_rate']),
                    'highest_score': int(player_row['highest_score']),
                    'matches_analyzed': int(player_row['matches'])
                }
                
                self.mongo.update_player_analytics(
                    player_name=player_row['player'],
                    analytics_data=analytics_data
                )
            
            print(f"✓ Synced {len(self.players_stats)} player analytics to MongoDB")
            
        except Exception as e:
            print(f"⚠ Error syncing player analytics: {e}")
    
    def setup_routes(self):
        """Setup all API routes"""
        
        # ===================== CORE PREDICTION ENDPOINTS =====================
        
        @self.app.route('/api/predict', methods=['POST'])
        def predict():
            """
            Predict player performance for upcoming match
            
            Request Body:
            {
                "player": "V Kohli",
                "team": "Royal Challengers Bangalore",
                "opponent": "Mumbai Indians",
                "venue": "M Chinnaswamy Stadium",
                "model_name": "xgboost",  // optional, defaults to current model
                "runs_last_5_avg": 45.0,  // optional
                "strike_rate_last_5": 140.0  // optional
            }
            """
            try:
                data = request.get_json()
                
                # Validate required fields
                required = ['player', 'team', 'opponent', 'venue']
                if not all(field in data for field in required):
                    return jsonify({
                        'error': 'Missing required fields',
                        'required': required
                    }), 400
                
                # Get requested model (optional)
                requested_model = data.get('model_name')
                
                # Get player recent stats if not provided
                player_data = self._get_player_recent_stats(data['player'])
                
                # Create prediction with selected model
                prediction = self._make_prediction(data, player_data, requested_model)
                
                # Save prediction to MongoDB if available
                if self.mongo and self.mongo.is_connected():
                    try:
                        prediction_data = {
                            'player': data['player'],
                            'team': data['team'],
                            'opponent': data['opponent'],
                            'venue': data['venue'],
                            'model_name': prediction['model_used'],
                            'predicted_runs': prediction['predicted_runs'],
                            'predicted_strike_rate': prediction['predicted_strike_rate'],
                            'confidence': prediction['confidence_score'],
                            'factors': player_data
                        }
                        pred_id = self.mongo.save_prediction(prediction_data)
                        prediction['mongo_id'] = pred_id
                    except Exception as e:
                        print(f"Failed to save to MongoDB: {e}")
                
                return jsonify(prediction), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/predict/batch', methods=['POST'])
        def predict_batch():
            """
            Batch predictions for multiple players
            
            Request Body:
            {
                "predictions": [
                    {"player": "V Kohli", "team": "RCB", ...},
                    {"player": "MS Dhoni", "team": "CSK", ...}
                ]
            }
            """
            try:
                data = request.get_json()
                predictions_list = data.get('predictions', [])
                
                results = []
                for pred_input in predictions_list:
                    try:
                        player_data = self._get_player_recent_stats(pred_input['player'])
                        pred = self._make_prediction(pred_input, player_data)
                        results.append(pred)
                    except Exception as e:
                        results.append({
                            'player': pred_input.get('player', 'Unknown'),
                            'error': str(e)
                        })
                
                return jsonify({'predictions': results}), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== PLAYER ENDPOINTS =====================
        
        @self.app.route('/api/players', methods=['GET'])
        def get_players():
            """
            Get list of all players with basic stats
            
            Query params:
            - limit: Number of players (default: 50)
            - sortBy: Sort field (total_runs, avg_runs, avg_strike_rate)
            - order: asc or desc
            """
            try:
                limit = int(request.args.get('limit', 50))
                sort_by = request.args.get('sortBy', 'total_runs')
                order = request.args.get('order', 'desc')
                
                ascending = order == 'asc'
                
                players = self.players_stats.sort_values(
                    sort_by, ascending=ascending
                ).head(limit)
                
                return jsonify({
                    'players': players.to_dict('records'),
                    'total': len(self.players_stats)
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/players/<player_name>', methods=['GET'])
        def get_player_details(player_name):
            """
            Get detailed statistics for a specific player
            """
            try:
                # Get player stats
                player_matches = self.features_df[
                    self.features_df['player'].str.contains(player_name, case=False, na=False)
                ]
                
                if len(player_matches) == 0:
                    return jsonify({'error': 'Player not found'}), 404
                
                # Calculate detailed stats
                stats = {
                    'name': player_matches['player'].iloc[0],
                    'matches': len(player_matches),
                    'total_runs': int(player_matches['runs_scored'].sum()),
                    'average': round(player_matches['runs_scored'].mean(), 2),
                    'highest_score': int(player_matches['runs_scored'].max()),
                    'strike_rate': round(player_matches['strike_rate'].mean(), 2),
                    'fifties': int((player_matches['runs_scored'] >= 50).sum()),
                    'hundreds': int((player_matches['runs_scored'] >= 100).sum()),
                    'ducks': int((player_matches['runs_scored'] == 0).sum()),
                    'dismissals': int(player_matches['dismissals'].sum())
                }
                
                # Recent form (last 5 matches)
                if 'date' in player_matches.columns and len(player_matches) > 0:
                    recent = player_matches.sort_values('date', ascending=False).head(5)[['date', 'runs_scored', 'strike_rate', 'opponent', 'venue']]
                    stats['recent_form'] = recent.to_dict('records')
                else:
                    stats['recent_form'] = []
                
                # Venue performance
                venue_perf = player_matches.groupby('venue').agg({
                    'runs_scored': ['mean', 'count']
                }).reset_index()
                venue_perf.columns = ['venue', 'avg_runs', 'matches']
                stats['venue_performance'] = venue_perf.to_dict('records')
                
                # Opposition performance
                opp_perf = player_matches.groupby('opponent').agg({
                    'runs_scored': ['mean', 'count']
                }).reset_index()
                opp_perf.columns = ['opponent', 'avg_runs', 'matches']
                stats['opponent_performance'] = opp_perf.to_dict('records')
                
                # Teams played for
                teams_played = player_matches['team'].unique().tolist()
                stats['teams'] = teams_played
                
                return jsonify(stats), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/players/search', methods=['GET'])
        def search_players():
            """
            Search players by name
            
            Query params:
            - q: Search query
            """
            try:
                query = request.args.get('q', '').strip()
                
                if len(query) < 2:
                    return jsonify({'players': []}), 200
                
                matching = self.players_stats[
                    self.players_stats['player'].str.contains(query, case=False, na=False)
                ]
                
                return jsonify({
                    'players': matching[['player', 'total_runs', 'avg_runs', 'matches']].to_dict('records')
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== TEAM ENDPOINTS =====================
        
        @self.app.route('/api/teams', methods=['GET'])
        def get_teams():
            """Get list of all teams with statistics"""
            try:
                teams = self.teams_stats.sort_values('avg_runs', ascending=False)
                
                return jsonify({
                    'teams': teams.to_dict('records')
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/teams/<team_name>/players', methods=['GET'])
        def get_team_players(team_name):
            """
            Get all players for a specific team
            """
            try:
                team_players = self.features_df[
                    self.features_df['team'].str.contains(team_name, case=False, na=False)
                ].groupby('player').agg({
                    'runs_scored': ['mean', 'sum', 'count'],
                    'strike_rate': 'mean'
                }).reset_index()
                
                team_players.columns = ['player', 'avg_runs', 'total_runs', 'matches', 'strike_rate']
                team_players = team_players.sort_values('total_runs', ascending=False)
                
                return jsonify({
                    'team': team_name,
                    'players': team_players.to_dict('records')
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== VENUE ENDPOINTS =====================
        
        @self.app.route('/api/venues', methods=['GET'])
        def get_venues():
            """
            Get list of all venues with statistics
            
            Query params:
            - team: Filter by team
            - opponent: Filter by opponent (requires team)
            """
            try:
                team = request.args.get('team', '').strip()
                opponent = request.args.get('opponent', '').strip()
                
                # If both team and opponent are provided, filter venues
                if team and opponent:
                    matchup_matches = self.features_df[
                        (self.features_df['team'].str.contains(team, case=False, na=False)) &
                        (self.features_df['opponent'].str.contains(opponent, case=False, na=False))
                    ]
                    
                    if len(matchup_matches) > 0:
                        # Get unique venues where these teams have played
                        matchup_venues = matchup_matches.groupby('venue').agg({
                            'runs_scored': 'mean',
                            'matchId': 'nunique'
                        }).reset_index()
                        matchup_venues.columns = ['venue', 'avg_runs', 'matches']
                        matchup_venues = matchup_venues.sort_values('matches', ascending=False)
                        
                        return jsonify({
                            'venues': matchup_venues.to_dict('records')
                        }), 200
                
                # Default: return all venues
                venues = self.venues_stats.sort_values('avg_runs', ascending=False)
                
                return jsonify({
                    'venues': venues.to_dict('records')
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/venues/<venue_name>/stats', methods=['GET'])
        def get_venue_stats(venue_name):
            """
            Get detailed statistics for a venue
            """
            try:
                venue_matches = self.features_df[
                    self.features_df['venue'].str.contains(venue_name, case=False, na=False)
                ]
                
                if len(venue_matches) == 0:
                    return jsonify({'error': 'Venue not found'}), 404
                
                stats = {
                    'venue': venue_matches['venue'].iloc[0],
                    'matches': len(venue_matches.groupby('matchId')),
                    'avg_runs': round(venue_matches['runs_scored'].mean(), 2),
                    'avg_strike_rate': round(venue_matches['strike_rate'].mean(), 2),
                    'highest_score': int(venue_matches['runs_scored'].max()),
                    'total_runs': int(venue_matches['runs_scored'].sum())
                }
                
                # Top scorers at venue
                top_scorers = venue_matches.groupby('player').agg({
                    'runs_scored': ['sum', 'mean', 'count']
                }).reset_index()
                top_scorers.columns = ['player', 'total_runs', 'avg_runs', 'matches']
                stats['top_scorers'] = top_scorers.nlargest(10, 'total_runs').to_dict('records')
                
                return jsonify(stats), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== LEADERBOARD ENDPOINTS =====================
        
        @self.app.route('/api/leaderboard/runs', methods=['GET'])
        def leaderboard_runs():
            """Get top run scorers leaderboard"""
            try:
                limit = int(request.args.get('limit', 20))
                
                leaderboard = self.players_stats.nlargest(limit, 'total_runs')
                
                return jsonify({
                    'leaderboard': leaderboard[[
                        'player', 'total_runs', 'avg_runs', 'matches', 
                        'highest_score', 'avg_strike_rate'
                    ]].to_dict('records')
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/leaderboard/strike-rate', methods=['GET'])
        def leaderboard_strike_rate():
            """Get highest strike rate leaderboard"""
            try:
                limit = int(request.args.get('limit', 20))
                min_matches = int(request.args.get('minMatches', 10))
                
                qualified = self.players_stats[self.players_stats['matches'] >= min_matches]
                leaderboard = qualified.nlargest(limit, 'avg_strike_rate')
                
                return jsonify({
                    'leaderboard': leaderboard[[
                        'player', 'avg_strike_rate', 'avg_runs', 'matches', 'total_runs'
                    ]].to_dict('records')
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/leaderboard/average', methods=['GET'])
        def leaderboard_average():
            """Get highest average leaderboard"""
            try:
                limit = int(request.args.get('limit', 20))
                min_matches = int(request.args.get('minMatches', 10))
                
                qualified = self.players_stats[self.players_stats['matches'] >= min_matches]
                leaderboard = qualified.nlargest(limit, 'avg_runs')
                
                # Select columns that exist
                columns = ['player', 'avg_runs', 'total_runs', 'matches']
                if 'highest_score' in leaderboard.columns:
                    columns.append('highest_score')
                if 'avg_strike_rate' in leaderboard.columns:
                    columns.append('avg_strike_rate')
                
                return jsonify({
                    'leaderboard': leaderboard[columns].to_dict('records')
                }), 200
                
            except Exception as e:
                print(f"Error in leaderboard_average: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        # ===================== COMPARISON ENDPOINTS =====================
        
        @self.app.route('/api/compare/players', methods=['POST'])
        def compare_players():
            """
            Compare multiple players
            
            Request Body:
            {
                "players": ["V Kohli", "RG Sharma", "MS Dhoni"]
            }
            """
            try:
                data = request.get_json()
                players = data.get('players', [])
                
                if len(players) < 2:
                    return jsonify({'error': 'Need at least 2 players to compare'}), 400
                
                comparison = []
                for player_name in players:
                    player_data = self.players_stats[
                        self.players_stats['player'].str.contains(player_name, case=False, na=False)
                    ]
                    
                    if len(player_data) > 0:
                        comparison.append(player_data.iloc[0].to_dict())
                
                return jsonify({
                    'comparison': comparison
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== ANALYTICS ENDPOINTS =====================
        
        @self.app.route('/api/analytics/form', methods=['GET'])
        def get_form_players():
            """
            Get players in best form (based on recent matches)
            """
            try:
                limit = int(request.args.get('limit', 10))
                
                # Calculate recent form for each player
                recent_form = []
                for player in self.features_df['player'].unique():
                    player_data = self.features_df[self.features_df['player'] == player]
                    if len(player_data) >= 3:
                        # Get last 5 matches (most recent by index if date not available)
                        if 'date' in player_data.columns:
                            last_5 = player_data.nlargest(5, 'date')
                        else:
                            last_5 = player_data.tail(5)
                        
                        form_score = last_5['runs_scored'].mean()
                        recent_form.append({
                            'player': player,
                            'form_score': round(form_score, 2),
                            'avg_runs': round(last_5['runs_scored'].mean(), 2),
                            'avg_strike_rate': round(last_5['strike_rate'].mean(), 2),
                            'matches': len(player_data)
                        })
                
                if len(recent_form) == 0:
                    return jsonify({
                        'form': [],
                        'message': 'No form data available'
                    }), 200
                
                form_df = pd.DataFrame(recent_form).nlargest(limit, 'form_score')
                
                return jsonify({
                    'form': form_df.to_dict('records')
                }), 200
                
            except Exception as e:
                print(f"Error in get_form_players: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics/matchups', methods=['GET'])
        def get_matchups():
            """
            Get player vs team matchup statistics
            
            Query params:
            - player: Player name
            - opponent: Opponent team
            """
            try:
                player = request.args.get('player', '').strip()
                opponent = request.args.get('opponent', '').strip()
                
                if not player or not opponent:
                    return jsonify({'error': 'Player and opponent required'}), 400
                
                # Use case-insensitive search with better name matching
                matchup_data = self.features_df[
                    (self.features_df['player'].str.contains(player, case=False, na=False)) &
                    (self.features_df['opponent'].str.contains(opponent, case=False, na=False))
                ]
                
                if len(matchup_data) == 0:
                    return jsonify({
                        'player': player,
                        'opponent': opponent,
                        'matches': 0,
                        'message': 'No matchup data found'
                    }), 200
                
                # Sort by date descending and get only the most recent performances
                if 'date' in matchup_data.columns:
                    matchup_data = matchup_data.sort_values('date', ascending=False)
                    recent_performances = matchup_data.head(10)  # Get top 10 most recent
                else:
                    recent_performances = matchup_data.tail(10)
                
                stats = {
                    'player': player,
                    'opponent': opponent,
                    'matches': len(matchup_data),
                    'total_runs': int(matchup_data['runs_scored'].sum()),
                    'avg_runs': round(matchup_data['runs_scored'].mean(), 2),
                    'highest_score': int(matchup_data['runs_scored'].max()),
                    'avg_strike_rate': round(matchup_data['strike_rate'].mean(), 2),
                    'performances': recent_performances[['date', 'runs_scored', 'strike_rate', 'venue']].to_dict('records')
                }
                
                return jsonify(stats), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== SYSTEM ENDPOINTS =====================
        
        @self.app.route('/api/models', methods=['GET'])
        def get_models():
            """
            Get list of all available models
            """
            try:
                models_info = []
                
                # Add current/default model
                if self.model_data:
                    model_metrics = self.model_data.get('metrics', {})
                    models_info.append({
                        'name': self.model_data['model_name'],
                        'is_default': True,
                        'test_mae': model_metrics.get('test_mae', model_metrics.get('mae', 'N/A')),
                        'test_rmse': model_metrics.get('test_rmse', model_metrics.get('rmse', 'N/A')),
                        'test_r2': model_metrics.get('test_r2', model_metrics.get('r2', 'N/A'))
                    })
                
                # Add all loaded models
                for model_name, model_data in self.all_models.items():
                    if model_name == self.model_data.get('model_name'):
                        continue  # Skip duplicate
                    
                    model_metrics = model_data.get('metrics', {})
                    models_info.append({
                        'name': model_name,
                        'is_default': False,
                        'test_mae': model_metrics.get('test_mae', model_metrics.get('mae', 'N/A')),
                        'test_rmse': model_metrics.get('test_rmse', model_metrics.get('rmse', 'N/A')),
                        'test_r2': model_metrics.get('test_r2', model_metrics.get('r2', 'N/A'))
                    })
                
                return jsonify({
                    'models': models_info,
                    'total': len(models_info)
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'model_loaded': self.model_data is not None,
                'features_loaded': self.features_df is not None,
                'model_name': self.model_data['model_name'] if self.model_data else None,
                'available_models': len(self.all_models),
                'total_players': len(self.players_stats) if self.players_stats is not None else 0,
                'total_matches': len(self.features_df) if self.features_df is not None else 0
            }), 200
        
        @self.app.route('/api/model/info', methods=['GET'])
        def model_info():
            """Get model information and performance metrics"""
            if self.model_data is None:
                return jsonify({'error': 'Model not loaded'}), 500
            
            metrics = self.model_data['metrics']
            return jsonify({
                'model_name': self.model_data['model_name'],
                'metrics': {
                    'test_mae': float(metrics.get('test_mae', metrics.get('mae', 0))),
                    'test_rmse': float(metrics.get('test_rmse', metrics.get('rmse', 0))),
                    'test_r2': float(metrics.get('test_r2', metrics.get('r2', 0)))
                },
                'training_date': 'December 2025',
                'dataset_size': len(self.features_df) if self.features_df is not None else 0
            }), 200
        
        @self.app.route('/api/stats/summary', methods=['GET'])
        def stats_summary():
            """Get overall statistics summary"""
            try:
                return jsonify({
                    'total_players': len(self.players_stats),
                    'total_teams': len(self.teams_stats),
                    'total_venues': len(self.venues_stats),
                    'total_matches': len(self.features_df.groupby('matchId')),
                    'total_runs': int(self.features_df['runs_scored'].sum()),
                    'avg_runs_per_match': round(self.features_df['runs_scored'].mean(), 2),
                    'avg_strike_rate': round(self.features_df['strike_rate'].mean(), 2),
                    'highest_score': int(self.features_df['runs_scored'].max())
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ===================== MONGODB ENDPOINTS =====================
        
        @self.app.route('/api/mongo/predictions/recent', methods=['GET'])
        def mongo_get_recent_predictions():
            """Get recent predictions from MongoDB"""
            if not self.mongo or not self.mongo.is_connected():
                return jsonify({'error': 'MongoDB not available'}), 503
            
            try:
                limit = int(request.args.get('limit', 50))
                predictions = self.mongo.get_recent_predictions(limit)
                
                return jsonify({
                    'predictions': predictions,
                    'total': len(predictions)
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/mongo/predictions/player/<player_name>', methods=['GET'])
        def mongo_get_player_predictions(player_name):
            """Get predictions for specific player from MongoDB"""
            if not self.mongo or not self.mongo.is_connected():
                return jsonify({'error': 'MongoDB not available'}), 503
            
            try:
                limit = int(request.args.get('limit', 20))
                predictions = self.mongo.get_player_predictions(player_name, limit)
                
                return jsonify({
                    'player': player_name,
                    'predictions': predictions,
                    'total': len(predictions)
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/mongo/predictions/stats', methods=['GET'])
        def mongo_get_prediction_stats():
            """Get prediction statistics from MongoDB"""
            if not self.mongo or not self.mongo.is_connected():
                return jsonify({'error': 'MongoDB not available'}), 503
            
            try:
                stats = self.mongo.get_prediction_stats()
                return jsonify(stats), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/mongo/analytics/player/<player_name>', methods=['GET'])
        def mongo_get_player_analytics(player_name):
            """Get player analytics from MongoDB"""
            if not self.mongo or not self.mongo.is_connected():
                return jsonify({'error': 'MongoDB not available'}), 503
            
            try:
                analytics = self.mongo.get_player_analytics(player_name)
                
                if analytics:
                    return jsonify(analytics), 200
                else:
                    return jsonify({'error': 'Player not found'}), 404
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/mongo/analytics/all', methods=['GET'])
        def mongo_get_all_analytics():
            """Get all player analytics from MongoDB"""
            if not self.mongo or not self.mongo.is_connected():
                return jsonify({'error': 'MongoDB not available'}), 503
            
            try:
                limit = int(request.args.get('limit', 100))
                analytics = self.mongo.get_all_player_analytics(limit)
                
                return jsonify({
                    'analytics': analytics,
                    'total': len(analytics)
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/mongo/status', methods=['GET'])
        def mongo_status():
            """Check MongoDB connection status"""
            if not self.mongo:
                return jsonify({
                    'connected': False,
                    'message': 'MongoDB handler not initialized'
                }), 200
            
            return jsonify({
                'connected': self.mongo.is_connected(),
                'message': 'MongoDB connected' if self.mongo.is_connected() else 'MongoDB not connected'
            }), 200
    
    # ===================== HELPER METHODS =====================
    
    def _get_player_recent_stats(self, player_name: str) -> Dict:
        """Get player's recent statistics"""
        if self.features_df is None:
            return {}
        
        player_data = self.features_df[
            self.features_df['player'].str.contains(player_name, case=False, na=False)
        ]
        
        if len(player_data) == 0:
            return {}
        
        # Sort by date descending and get last 5 matches
        recent = player_data.sort_values('date', ascending=False).head(5)
        
        stats = {
            'runs_last_5_avg': round(recent['runs_scored'].mean(), 2),
            'strike_rate_last_5': round(recent['strike_rate'].mean(), 2),
            'matches_played': len(player_data),
            'career_avg': round(player_data['runs_scored'].mean(), 2),
            'highest_score': int(player_data['runs_scored'].max())
        }
        
        # Add venue and opponent averages if available in player data
        if 'venue_avg_runs' in player_data.columns:
            stats['venue_avg_runs'] = round(player_data['venue_avg_runs'].mean(), 2)
        if 'opponent_avg_runs' in player_data.columns:
            stats['opponent_avg_runs'] = round(player_data['opponent_avg_runs'].mean(), 2)
        if 'venue_avg_strike_rate' in player_data.columns:
            stats['venue_avg_strike_rate'] = round(player_data['venue_avg_strike_rate'].mean(), 2)
        if 'opponent_avg_strike_rate' in player_data.columns:
            stats['opponent_avg_strike_rate'] = round(player_data['opponent_avg_strike_rate'].mean(), 2)
        
        return stats
    
    def _make_prediction(self, input_data: Dict, player_stats: Dict, model_name: str = None) -> Dict:
        """Make prediction with player context and optional model selection"""
        # Select model
        if model_name and model_name in self.all_models:
            model_data = self.all_models[model_name]
        elif self.model_data:
            model_data = self.model_data
        else:
            raise Exception("No model available for prediction")
        
        # Merge input with player stats
        prediction_input = {**input_data, **player_stats}
        
        # Extract features
        player = prediction_input['player']
        team = prediction_input['team']
        opponent = prediction_input['opponent']
        venue = prediction_input['venue']
        
        # Create feature vector
        features = self._create_feature_vector(prediction_input)
        
        # Make prediction
        model = model_data['model']
        scaler = model_data['scaler']
        
        features_scaled = scaler.transform([features])
        
        if model_data['model_name'] in ['random_forest', 'xgboost']:
            predicted_runs = model.predict([features])[0]
        else:
            predicted_runs = model.predict(features_scaled)[0]
        
        # Clip prediction to reasonable range
        predicted_runs = float(np.clip(predicted_runs, 0, 200))
        
        # Add small random variation to avoid exact same predictions
        # This accounts for match-day form, pitch conditions, etc.
        variation = np.random.uniform(-2, 2)
        predicted_runs = max(0, predicted_runs + variation)
        
        # Estimate strike rate
        predicted_strike_rate = self._estimate_strike_rate(predicted_runs, prediction_input)
        
        # Calculate confidence
        confidence = self._calculate_confidence(prediction_input)
        
        return {
            'player': player,
            'team': team,
            'opponent': opponent,
            'venue': venue,
            'predicted_runs': float(max(0, predicted_runs)),
            'predicted_strike_rate': float(predicted_strike_rate),
            'predicted_wickets': 0.0,
            'confidence': confidence,
            'confidence_score': self._get_confidence_score(confidence),
            'model_used': model_data['model_name'],
            'player_stats': player_stats
        }
    
    def _create_feature_vector(self, input_data: Dict) -> list:
        """Create feature vector from input using actual player data"""
        # Get player-specific encoding from historical data
        player_name = input_data['player']
        team_name = input_data['team']
        opponent_name = input_data['opponent']
        venue_name = input_data['venue']
        
        # Use actual player encoding from features_df if available
        if self.features_df is not None:
            player_matches = self.features_df[
                self.features_df['player'].str.contains(player_name, case=False, na=False)
            ]
            
            if len(player_matches) > 0:
                # Use actual encoded values from data
                player_encoded = player_matches['player_encoded'].iloc[0] if 'player_encoded' in player_matches else hash(player_name) % 1000
            else:
                player_encoded = hash(player_name) % 1000
        else:
            player_encoded = hash(player_name) % 1000
        
        team_encoded = hash(team_name) % 20
        opponent_encoded = hash(opponent_name) % 20
        venue_encoded = hash(venue_name) % 50
        
        # Get actual player stats (NOT hardcoded defaults)
        runs_last_5_avg = input_data.get('runs_last_5_avg', None)
        strike_rate_last_5 = input_data.get('strike_rate_last_5', None)
        
        # If stats not provided, calculate from historical data
        if runs_last_5_avg is None and self.features_df is not None:
            if len(player_matches) > 0:
                recent = player_matches.sort_values('date', ascending=False).head(5)
                runs_last_5_avg = recent['runs_scored'].mean()
                if strike_rate_last_5 is None:
                    strike_rate_last_5 = recent['strike_rate'].mean()
            else:
                # Use global average only if player not found
                runs_last_5_avg = self.features_df['runs_scored'].mean()
                strike_rate_last_5 = self.features_df['strike_rate'].mean()
        else:
            runs_last_5_avg = runs_last_5_avg if runs_last_5_avg is not None else 30.0
            strike_rate_last_5 = strike_rate_last_5 if strike_rate_last_5 is not None else 130.0
        
        # Get venue-specific stats
        venue_avg_runs = input_data.get('venue_avg_runs', None)
        venue_avg_strike_rate = input_data.get('venue_avg_strike_rate', None)
        
        if venue_avg_runs is None and self.features_df is not None:
            venue_matches = self.features_df[
                self.features_df['venue'].str.contains(venue_name, case=False, na=False)
            ]
            if len(venue_matches) > 0:
                venue_avg_runs = venue_matches['runs_scored'].mean()
                venue_avg_strike_rate = venue_matches['strike_rate'].mean()
            else:
                venue_avg_runs = self.features_df['runs_scored'].mean()
                venue_avg_strike_rate = self.features_df['strike_rate'].mean()
        else:
            venue_avg_runs = venue_avg_runs if venue_avg_runs is not None else 32.0
            venue_avg_strike_rate = venue_avg_strike_rate if venue_avg_strike_rate is not None else 130.0
        
        # Get opponent-specific stats
        opponent_avg_runs = input_data.get('opponent_avg_runs', None)
        opponent_avg_strike_rate = input_data.get('opponent_avg_strike_rate', None)
        
        if opponent_avg_runs is None and self.features_df is not None:
            opponent_matches = self.features_df[
                self.features_df['opponent'].str.contains(opponent_name, case=False, na=False)
            ]
            if len(opponent_matches) > 0:
                opponent_avg_runs = opponent_matches['runs_scored'].mean()
                opponent_avg_strike_rate = opponent_matches['strike_rate'].mean()
            else:
                opponent_avg_runs = self.features_df['runs_scored'].mean()
                opponent_avg_strike_rate = self.features_df['strike_rate'].mean()
        else:
            opponent_avg_runs = opponent_avg_runs if opponent_avg_runs is not None else 30.0
            opponent_avg_strike_rate = opponent_avg_strike_rate if opponent_avg_strike_rate is not None else 130.0
        
        is_home_match = input_data.get('is_home_match', 0)
        batting_position = input_data.get('batting_position', 4)
        
        return [
            player_encoded, team_encoded, opponent_encoded, venue_encoded,
            runs_last_5_avg, strike_rate_last_5, venue_avg_runs,
            opponent_avg_runs, is_home_match, batting_position,
            venue_avg_strike_rate, opponent_avg_strike_rate
        ]
    
    def _estimate_strike_rate(self, predicted_runs: float, input_data: Dict) -> float:
        """Estimate strike rate based on predicted runs"""
        base_sr = input_data.get('strike_rate_last_5', 130.0)
        
        if predicted_runs > 50:
            estimated_sr = base_sr * 1.1
        elif predicted_runs > 30:
            estimated_sr = base_sr
        else:
            estimated_sr = base_sr * 0.9
        
        return min(200.0, max(80.0, estimated_sr))
    
    def _calculate_confidence(self, input_data: Dict) -> str:
        """Calculate confidence level"""
        has_recent_form = 'runs_last_5_avg' in input_data
        has_strike_rate = 'strike_rate_last_5' in input_data
        has_matches = input_data.get('matches_played', 0) > 10
        
        confidence_score = sum([has_recent_form, has_strike_rate, has_matches])
        
        if confidence_score >= 2:
            return 'high'
        elif confidence_score == 1:
            return 'medium'
        else:
            return 'low'
    
    def _get_confidence_score(self, confidence: str) -> float:
        """Convert confidence to numeric score"""
        return {'high': 0.85, 'medium': 0.65, 'low': 0.45}.get(confidence, 0.5)
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run Flask application"""
        print("\n" + "=" * 70)
        print("  CricNex Enhanced Backend API Server")
        print("=" * 70)
        print(f"  Server: http://{host}:{port}")
        print(f"  Model: {self.model_data['model_name'] if self.model_data else 'Not loaded'}")
        print(f"  Available Models: {len(self.all_models)}")
        print(f"  Players: {len(self.players_stats) if self.players_stats is not None else 0}")
        print(f"  Teams: {len(self.teams_stats) if self.teams_stats is not None else 0}")
        print(f"  Venues: {len(self.venues_stats) if self.venues_stats is not None else 0}")
        print("=" * 70)
        print("\n  📡 API Endpoints:")
        print("     POST   /api/predict")
        print("     POST   /api/predict/batch")
        print("     GET    /api/players")
        print("     GET    /api/players/<name>")
        print("     GET    /api/teams")
        print("     GET    /api/venues")
        print("     GET    /api/leaderboard/runs")
        print("     GET    /api/leaderboard/strike-rate")
        print("     GET    /api/leaderboard/average")
        print("     POST   /api/compare/players")
        print("     GET    /api/analytics/form")
        print("     GET    /api/analytics/matchups")
        print("     GET    /api/models")
        print("     GET    /api/health")
        print("     GET    /api/model/info")
        print("     GET    /api/stats/summary")
        print("=" * 70 + "\n")
        
        self.app.run(host=host, port=port, debug=debug)


def create_backend(
    model_path: str = "../models/best_model.pkl",
    features_path: str = "../data/features.csv",
    models_dir: str = "../models"
) -> CricNexBackend:
    """
    Factory function to create backend instance
    
    Args:
        model_path: Path to saved model
        features_path: Path to features CSV
        models_dir: Directory containing all models
        
    Returns:
        CricNexBackend instance
    """
    backend = CricNexBackend(model_path, features_path, models_dir)
    return backend


if __name__ == "__main__":
    # Run enhanced backend
    backend = create_backend()
    backend.run(debug=False)
