"""
CricNex - Data Loader Module
Handles loading and preprocessing of IPL cricket data
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import os


class DataLoader:
    """
    Data loader for IPL cricket datasets
    Handles loading deliveries and matches data with preprocessing
    """
    
    def __init__(self, deliveries_path: str, matches_path: str):
        """
        Initialize data loader with file paths
        
        Args:
            deliveries_path: Path to deliveries CSV file
            matches_path: Path to matches CSV file
        """
        self.deliveries_path = deliveries_path
        self.matches_path = matches_path
        self.deliveries_df = None
        self.matches_df = None
        self.merged_df = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load both datasets
        
        Returns:
            Tuple of (deliveries_df, matches_df)
        """
        print("📂 Loading datasets...")
        
        # Load deliveries
        if os.path.exists(self.deliveries_path):
            self.deliveries_df = pd.read_csv(self.deliveries_path)
            print(f"✓ Deliveries loaded: {len(self.deliveries_df):,} records")
        else:
            raise FileNotFoundError(f"Deliveries file not found: {self.deliveries_path}")
        
        # Load matches
        if os.path.exists(self.matches_path):
            self.matches_df = pd.read_csv(self.matches_path)
            print(f"✓ Matches loaded: {len(self.matches_df):,} records")
        else:
            raise FileNotFoundError(f"Matches file not found: {self.matches_path}")
        
        return self.deliveries_df, self.matches_df
    
    def preprocess_deliveries(self) -> pd.DataFrame:
        """
        Preprocess deliveries data
        - Handle missing values
        - Convert data types
        - Filter valid deliveries
        
        Returns:
            Preprocessed deliveries DataFrame
        """
        print("\n🔧 Preprocessing deliveries...")
        
        df = self.deliveries_df.copy()
        
        # Fill missing values
        df['player_dismissed'] = df['player_dismissed'].fillna('Not Out')
        df['dismissal_kind'] = df['dismissal_kind'].fillna('Not Out')
        df['fielder'] = df['fielder'].fillna('No Fielder')
        
        # Convert numeric columns
        numeric_cols = ['total_runs', 'batsman_runs', 'extra_runs', 'wides', 'noballs', 'byes', 'legbyes', 'penalty']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Remove extra deliveries (wides, no balls) for batting stats
        df['is_valid_ball'] = (df['wides'] == 0) & (df['noballs'] == 0)
        
        print(f"✓ Deliveries preprocessed: {len(df):,} records")
        return df
    
    def preprocess_matches(self) -> pd.DataFrame:
        """
        Preprocess matches data
        - Parse dates
        - Handle missing values
        - Extract relevant columns
        
        Returns:
            Preprocessed matches DataFrame
        """
        print("\n🔧 Preprocessing matches...")
        
        df = self.matches_df.copy()
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Fill missing values
        if 'city' in df.columns:
            df['city'] = df['city'].fillna('Unknown')
        if 'venue' in df.columns:
            df['venue'] = df['venue'].fillna('Unknown Venue')
        if 'player_of_match' in df.columns:
            df['player_of_match'] = df['player_of_match'].fillna('Not Awarded')
        
        # Extract season/year
        if 'season' in df.columns:
            df['season'] = pd.to_numeric(df['season'], errors='coerce')
        elif 'date' in df.columns:
            df['season'] = df['date'].dt.year
        
        print(f"✓ Matches preprocessed: {len(df):,} records")
        return df
    
    def merge_data(self) -> pd.DataFrame:
        """
        Merge deliveries with match information
        
        Returns:
            Merged DataFrame with both delivery and match details
        """
        print("\n🔗 Merging datasets...")
        
        # Preprocess first
        deliveries = self.preprocess_deliveries()
        matches = self.preprocess_matches()
        
        # Select relevant match columns
        match_cols = ['id', 'date', 'season', 'city', 'venue', 'team1', 'team2', 'toss_winner', 
                      'toss_decision', 'result', 'winner', 'player_of_match']
        match_cols = [col for col in match_cols if col in matches.columns]
        
        # Merge on match_id
        self.merged_df = deliveries.merge(
            matches[match_cols],
            left_on='match_id',
            right_on='id',
            how='left'
        )
        
        # Drop duplicate id column if exists
        if 'id' in self.merged_df.columns and 'match_id' in self.merged_df.columns:
            self.merged_df = self.merged_df.drop(columns=['id'])
        
        print(f"✓ Data merged: {len(self.merged_df):,} records")
        return self.merged_df
    
    def aggregate_match_stats(self) -> pd.DataFrame:
        """
        Aggregate delivery data to match-level batting statistics
        
        Returns:
            DataFrame with player-match level statistics
        """
        print("\n📊 Aggregating match statistics...")
        
        if self.merged_df is None:
            self.merge_data()
        
        df = self.merged_df.copy()
        
        # Calculate balls faced (only valid deliveries)
        df['balls_faced'] = df['is_valid_ball'].astype(int)
        
        # Aggregate by player and match
        player_match_stats = df.groupby(['match_id', 'batsman', 'batting_team', 'bowling_team', 
                                         'venue', 'date', 'season']).agg({
            'batsman_runs': 'sum',
            'balls_faced': 'sum',
            'extra_runs': 'sum'
        }).reset_index()
        
        # Rename columns
        player_match_stats.rename(columns={
            'batsman': 'player',
            'batting_team': 'team',
            'bowling_team': 'opponent',
            'batsman_runs': 'runs_scored'
        }, inplace=True)
        
        # Calculate strike rate
        player_match_stats['strike_rate'] = (
            player_match_stats['runs_scored'] / player_match_stats['balls_faced'] * 100
        ).fillna(0)
        
        # Filter out innings with 0 balls faced
        player_match_stats = player_match_stats[player_match_stats['balls_faced'] > 0]
        
        # Sort by date
        player_match_stats = player_match_stats.sort_values(['player', 'date']).reset_index(drop=True)
        
        print(f"✓ Aggregated to {len(player_match_stats):,} player-match records")
        return player_match_stats
    
    def get_player_list(self) -> list:
        """Get list of unique players"""
        if self.merged_df is None:
            self.merge_data()
        return sorted(self.merged_df['batsman'].unique().tolist())
    
    def get_team_list(self) -> list:
        """Get list of unique teams"""
        if self.matches_df is None:
            self.load_data()
        teams = set()
        if 'team1' in self.matches_df.columns:
            teams.update(self.matches_df['team1'].unique())
        if 'team2' in self.matches_df.columns:
            teams.update(self.matches_df['team2'].unique())
        return sorted(list(teams))
    
    def get_venue_list(self) -> list:
        """Get list of unique venues"""
        if self.matches_df is None:
            self.load_data()
        return sorted(self.matches_df['venue'].dropna().unique().tolist())
    
    def save_processed_data(self, output_path: str):
        """
        Save aggregated data to CSV
        
        Args:
            output_path: Path to save processed data
        """
        if self.merged_df is None:
            self.merge_data()
        
        # Get aggregated stats
        stats_df = self.aggregate_match_stats()
        
        # Save to CSV
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        stats_df.to_csv(output_path, index=False)
        print(f"\n✓ Processed data saved to: {output_path}")
        
        return stats_df


def load_ipl_data(deliveries_path: str, matches_path: str) -> pd.DataFrame:
    """
    Convenience function to load and process IPL data
    
    Args:
        deliveries_path: Path to deliveries CSV
        matches_path: Path to matches CSV
        
    Returns:
        Processed DataFrame with match-level statistics
    """
    loader = DataLoader(deliveries_path, matches_path)
    loader.load_data()
    return loader.aggregate_match_stats()


if __name__ == "__main__":
    # Example usage
    deliveries_path = "../ballbyball/deliveries_updated_mens_ipl_upto_2024.csv"
    matches_path = "../ballbyball/matches_updated_mens_ipl_upto_2024.csv"
    
    loader = DataLoader(deliveries_path, matches_path)
    loader.load_data()
    processed_data = loader.aggregate_match_stats()
    
    print("\n📊 Data Summary:")
    print(f"Total records: {len(processed_data):,}")
    print(f"Unique players: {processed_data['player'].nunique()}")
    print(f"Unique teams: {processed_data['team'].nunique()}")
    print(f"Unique venues: {processed_data['venue'].nunique()}")
    print(f"Date range: {processed_data['date'].min()} to {processed_data['date'].max()}")
