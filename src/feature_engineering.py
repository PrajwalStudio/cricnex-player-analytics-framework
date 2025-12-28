"""
CricNex - Feature Engineering Module
Creates advanced features for player performance prediction
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """
    Feature engineering for cricket player performance prediction
    Creates rolling statistics, venue features, and encoded variables
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize feature engineer with player-match statistics
        
        Args:
            df: DataFrame with player-match level data
        """
        self.df = df.copy()
        self.label_encoders = {}
        self.features_df = None
        
    def create_rolling_features(self, windows: List[int] = [5, 10]) -> pd.DataFrame:
        """
        Create rolling window features for player form
        
        Args:
            windows: List of window sizes for rolling statistics
            
        Returns:
            DataFrame with rolling features added
        """
        print("\n🎯 Creating rolling features...")
        
        df = self.df.copy()
        
        # Sort by player and date
        df = df.sort_values(['player', 'date']).reset_index(drop=True)
        
        # Create rolling features for each window
        for window in windows:
            print(f"  • Rolling {window}-match statistics...")
            
            # Runs average
            df[f'runs_last_{window}_avg'] = df.groupby('player')['runs_scored'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean().shift(1)
            )
            
            # Strike rate average
            df[f'strike_rate_last_{window}'] = df.groupby('player')['strike_rate'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean().shift(1)
            )
            
            # Balls faced average
            df[f'balls_faced_last_{window}'] = df.groupby('player')['balls_faced'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean().shift(1)
            )
        
        # Fill NaN values with 0 for first matches
        rolling_cols = [col for col in df.columns if 'last_' in col]
        df[rolling_cols] = df[rolling_cols].fillna(0)
        
        print(f"✓ Created {len(rolling_cols)} rolling features")
        return df
    
    def create_venue_features(self) -> pd.DataFrame:
        """
        Create venue-specific features
        Average performance at each venue
        
        Returns:
            DataFrame with venue features added
        """
        print("\n🏟️ Creating venue features...")
        
        df = self.df.copy()
        
        # Venue average runs
        venue_avg_runs = df.groupby('venue')['runs_scored'].transform('mean')
        df['venue_avg_runs'] = venue_avg_runs
        
        # Venue average strike rate
        venue_avg_sr = df.groupby('venue')['strike_rate'].transform('mean')
        df['venue_avg_strike_rate'] = venue_avg_sr
        
        # Player-venue average (historical performance at venue)
        player_venue_runs = df.groupby(['player', 'venue'])['runs_scored'].transform(
            lambda x: x.expanding().mean().shift(1)
        ).fillna(venue_avg_runs)
        df['player_venue_avg_runs'] = player_venue_runs
        
        print("✓ Created 3 venue features")
        return df
    
    def create_opponent_features(self) -> pd.DataFrame:
        """
        Create opponent-specific features
        Performance against each opponent
        
        Returns:
            DataFrame with opponent features added
        """
        print("\n⚔️ Creating opponent features...")
        
        df = self.df.copy()
        
        # Opponent average runs conceded
        opponent_avg_runs = df.groupby('opponent')['runs_scored'].transform('mean')
        df['opponent_avg_runs'] = opponent_avg_runs
        
        # Opponent average strike rate allowed
        opponent_avg_sr = df.groupby('opponent')['strike_rate'].transform('mean')
        df['opponent_avg_strike_rate'] = opponent_avg_sr
        
        # Player vs opponent average
        player_opponent_runs = df.groupby(['player', 'opponent'])['runs_scored'].transform(
            lambda x: x.expanding().mean().shift(1)
        ).fillna(opponent_avg_runs)
        df['player_opponent_avg_runs'] = player_opponent_runs
        
        print("✓ Created 3 opponent features")
        return df
    
    def create_home_away_feature(self) -> pd.DataFrame:
        """
        Create home match indicator
        Based on team's primary venue
        
        Returns:
            DataFrame with home/away feature
        """
        print("\n🏠 Creating home/away feature...")
        
        df = self.df.copy()
        
        # Determine home venues for each team (most common venue)
        team_home_venue = df.groupby('team')['venue'].agg(
            lambda x: x.value_counts().index[0] if len(x) > 0 else None
        ).to_dict()
        
        # Create is_home_match feature
        df['is_home_match'] = df.apply(
            lambda row: 1 if team_home_venue.get(row['team']) == row['venue'] else 0,
            axis=1
        )
        
        print("✓ Created home/away feature")
        return df
    
    def create_batting_position_feature(self) -> pd.DataFrame:
        """
        Estimate batting position/order
        Based on when player typically bats
        
        Returns:
            DataFrame with batting position feature
        """
        print("\n🎯 Creating batting position feature...")
        
        df = self.df.copy()
        
        # Estimate position (simplified - could be enhanced with actual data)
        # Use average balls faced as proxy - earlier batsmen face more balls
        player_avg_balls = df.groupby('player')['balls_faced'].mean().to_dict()
        df['batting_position'] = df['player'].map(player_avg_balls)
        
        # Normalize to 1-11 scale
        df['batting_position'] = pd.qcut(
            df['batting_position'], 
            q=11, 
            labels=range(1, 12), 
            duplicates='drop'
        ).astype(float)
        
        df['batting_position'] = df['batting_position'].fillna(6)  # Default middle order
        
        print("✓ Created batting position feature")
        return df
    
    def encode_categorical_features(self) -> pd.DataFrame:
        """
        Label encode categorical variables
        
        Returns:
            DataFrame with encoded categorical features
        """
        print("\n🏷️ Encoding categorical features...")
        
        df = self.df.copy()
        
        categorical_cols = ['player', 'team', 'opponent', 'venue']
        
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        print(f"✓ Encoded {len(categorical_cols)} categorical features")
        return df
    
    def create_match_context_features(self) -> pd.DataFrame:
        """
        Create contextual features about the match
        
        Returns:
            DataFrame with match context features
        """
        print("\n📅 Creating match context features...")
        
        df = self.df.copy()
        
        # Season feature (already exists, but ensure it's numeric)
        if 'season' in df.columns:
            df['season'] = pd.to_numeric(df['season'], errors='coerce').fillna(2024)
        
        # Match number in season for player (form progression)
        df['match_number_in_season'] = df.groupby(['player', 'season']).cumcount() + 1
        
        # Days since last match (rest/momentum)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['days_since_last_match'] = df.groupby('player')['date'].diff().dt.days.fillna(7)
        df['days_since_last_match'] = df['days_since_last_match'].clip(0, 30)  # Cap at 30 days
        
        print("✓ Created 2 match context features")
        return df
    
    def engineer_all_features(self) -> pd.DataFrame:
        """
        Create all features in sequence
        
        Returns:
            DataFrame with all engineered features
        """
        print("\n" + "="*70)
        print("FEATURE ENGINEERING")
        print("="*70)
        
        # Start with base data
        df = self.df.copy()
        
        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Apply all feature engineering steps
        df = self.create_rolling_features(windows=[5, 10])
        self.df = df
        
        df = self.create_venue_features()
        self.df = df
        
        df = self.create_opponent_features()
        self.df = df
        
        df = self.create_home_away_feature()
        self.df = df
        
        df = self.create_batting_position_feature()
        self.df = df
        
        df = self.create_match_context_features()
        self.df = df
        
        df = self.encode_categorical_features()
        
        # Store final features
        self.features_df = df
        
        # Print summary
        print("\n" + "="*70)
        print("FEATURE ENGINEERING COMPLETE")
        print("="*70)
        print(f"\n📊 Total features created: {len(df.columns)}")
        print(f"📝 Total records: {len(df):,}")
        
        # Display feature categories
        rolling_features = [col for col in df.columns if 'last_' in col]
        venue_features = [col for col in df.columns if 'venue' in col.lower()]
        opponent_features = [col for col in df.columns if 'opponent' in col.lower()]
        encoded_features = [col for col in df.columns if 'encoded' in col]
        
        print(f"\nFeature breakdown:")
        print(f"  • Rolling features: {len(rolling_features)}")
        print(f"  • Venue features: {len(venue_features)}")
        print(f"  • Opponent features: {len(opponent_features)}")
        print(f"  • Encoded features: {len(encoded_features)}")
        
        return df
    
    def get_feature_columns(self, target: str = 'runs_scored') -> List[str]:
        """
        Get list of feature columns (excluding target and metadata)
        
        Args:
            target: Target variable name
            
        Returns:
            List of feature column names
        """
        if self.features_df is None:
            raise ValueError("Features not yet created. Call engineer_all_features() first.")
        
        # Exclude columns
        exclude_cols = [
            target, 'match_id', 'player', 'team', 'opponent', 'venue', 
            'date', 'balls_faced', 'extra_runs', 'is_valid_ball', 'season'
        ]
        
        feature_cols = [col for col in self.features_df.columns if col not in exclude_cols]
        
        return feature_cols
    
    def save_features(self, output_path: str):
        """
        Save engineered features to CSV
        
        Args:
            output_path: Path to save features
        """
        if self.features_df is None:
            raise ValueError("Features not yet created. Call engineer_all_features() first.")
        
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.features_df.to_csv(output_path, index=False)
        print(f"\n✓ Features saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    print("Feature Engineering Module - Example Usage\n")
    
    # This would typically load from data_loader
    # For demo, create sample data
    sample_data = pd.DataFrame({
        'match_id': range(100),
        'player': ['Player A'] * 50 + ['Player B'] * 50,
        'team': ['Team 1'] * 100,
        'opponent': ['Team 2'] * 50 + ['Team 3'] * 50,
        'venue': ['Venue A'] * 100,
        'date': pd.date_range('2023-01-01', periods=100),
        'season': [2023] * 100,
        'runs_scored': np.random.randint(0, 100, 100),
        'strike_rate': np.random.uniform(80, 180, 100),
        'balls_faced': np.random.randint(5, 50, 100)
    })
    
    engineer = FeatureEngineer(sample_data)
    features = engineer.engineer_all_features()
    
    print("\n✓ Feature engineering demonstration complete!")
    print(f"Input columns: {len(sample_data.columns)}")
    print(f"Output columns: {len(features.columns)}")
