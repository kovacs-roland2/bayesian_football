import pandas as pd
import numpy as np
import os

def calculate_stats(club_name, calculation_type, csv_file_path="data/premier_league_matches_20250530_130423.csv"):
    """
    Calculate various Premier League statistics for a given club.
    
    Parameters:
    club_name (str): Name of the club (e.g., "Arsenal", "Manchester City")
    calculation_type (str): Type of calculation to perform. Options:
        - "points_per_match": List of points collected in each match (0, 1, or 3)
        - "xg_per_match": List of expected goals per match
        - "xga_per_match": List of expected goals against per match
    csv_file_path (str): Path to the CSV file containing match data
    
    Returns:
    list: The calculated statistic
    """
    
    def _calculate_points(club_matches):
        # Filter out invalid scores for points calculation
        valid_matches = club_matches[club_matches['Score'].str.contains('–', na=False)]
        
        try:
            valid_matches[['home_goals', 'away_goals']] = valid_matches['Score'].str.split('–', expand=True).astype(int)
        except ValueError:
            return []
        
        # Calculate points
        conditions = [
            # Win conditions
            (valid_matches['is_home'] & (valid_matches['home_goals'] > valid_matches['away_goals'])) |
            (~valid_matches['is_home'] & (valid_matches['away_goals'] > valid_matches['home_goals'])),
            # Draw conditions  
            (valid_matches['home_goals'] == valid_matches['away_goals'])
        ]
        
        choices = [3, 1]  # Win = 3 points, Draw = 1 point, Loss = 0 points (default)
        valid_matches['points'] = np.select(conditions, choices, default=0)
        
        return valid_matches['points'].tolist()
    
    def _calculate_xg(club_matches):
        home_xg = pd.to_numeric(club_matches.iloc[:, 5], errors='coerce')
        away_xg = pd.to_numeric(club_matches.iloc[:, 7], errors='coerce')
        
        club_matches['club_xg'] = np.where(club_matches['is_home'], home_xg, away_xg)
        return club_matches['club_xg'].fillna(0).tolist()
    
    def _calculate_xga(club_matches):
        home_xg = pd.to_numeric(club_matches.iloc[:, 5], errors='coerce')
        away_xg = pd.to_numeric(club_matches.iloc[:, 7], errors='coerce')
        
        club_matches['club_xga'] = np.where(club_matches['is_home'], away_xg, home_xg)
        return club_matches['club_xga'].fillna(0).tolist()
    
    # Dictionary mapping calculation types to functions
    calculations = {
        "points_per_match": _calculate_points,
        "xg_per_match": _calculate_xg,
        "xga_per_match": _calculate_xga
    }
    
    if calculation_type not in calculations:
        raise ValueError(f"Unknown calculation type: {calculation_type}. Available: {list(calculations.keys())}")
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        raise IOError(f"Error reading CSV file: {e}")
    
    # Filter matches where the club played
    club_matches = df[
        (df['Home'].str.strip() == club_name) | 
        (df['Away'].str.strip() == club_name)
    ].copy()
    
    # Determine if club is home team
    club_matches['is_home'] = club_matches['Home'].str.strip() == club_name
    
    # Execute the appropriate calculation function
    return calculations[calculation_type](club_matches)

def get_available_teams(csv_file_path="data/premier_league_matches_20250530_130423.csv"):
    """
    Get a list of all teams in the dataset.
    
    Parameters:
    csv_file_path (str): Path to the CSV file containing match data
    
    Returns:
    list: Sorted list of unique team names
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    df = pd.read_csv(csv_file_path)
    teams = set(df['Home'].str.strip().tolist())
    return sorted(list(teams))