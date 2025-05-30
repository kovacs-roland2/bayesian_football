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
    csv_file_path (str): Path to the CSV file containing match data
    
    Returns:
    list: The calculated statistic
    """
    
    if calculation_type != "points_per_match":
        raise ValueError(f"Unknown calculation type: {calculation_type}")
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        raise IOError(f"Error reading CSV file: {e}")
    
    club_name = club_name.strip()
    
    # Filter matches where the club played and score is valid
    club_matches = df[
        (df['Home'].str.strip() == club_name) | 
        (df['Away'].str.strip() == club_name)
    ].copy()
    
    # Filter out invalid scores
    club_matches = club_matches[club_matches['Score'].str.contains('–', na=False)]
    
    # Parse scores
    try:
        club_matches[['home_goals', 'away_goals']] = club_matches['Score'].str.split('–', expand=True).astype(int)
    except ValueError:
        return []
    
    # Determine if club is home team
    club_matches['is_home'] = club_matches['Home'].str.strip() == club_name
    
    # Calculate points
    conditions = [
        # Win conditions
        (club_matches['is_home'] & (club_matches['home_goals'] > club_matches['away_goals'])) |
        (~club_matches['is_home'] & (club_matches['away_goals'] > club_matches['home_goals'])),
        # Draw conditions  
        (club_matches['home_goals'] == club_matches['away_goals'])
    ]
    
    choices = [3, 1]  # Win = 3 points, Draw = 1 point, Loss = 0 points (default)
    
    club_matches['points'] = np.select(conditions, choices, default=0)
    
    return club_matches['points'].tolist()

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