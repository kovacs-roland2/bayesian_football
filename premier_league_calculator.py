import pandas as pd
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
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        raise Exception(f"Error reading CSV file: {e}")
    
    # Normalize club name for comparison (handle variations)
    club_name = club_name.strip()
    
    # Initialize counter
    points_per_match = []  # New list to store points from each match
    
    # Process each match in chronological order
    for _, row in df.iterrows():
        home_team = row['Home'].strip()
        away_team = row['Away'].strip()
        score = row['Score'].strip()
        
        # Skip if score is not in expected format
        if '–' not in score:
            continue
            
        try:
            # Parse the score
            home_goals, away_goals = map(int, score.split('–'))
        except ValueError:
            continue
        
        # Check if the club is playing in this match
        is_home = (home_team == club_name)
        is_away = (away_team == club_name)
        
        if not (is_home or is_away):
            continue
        
        match_points = 0  # Points earned in this specific match
        
        if is_home:
            # Club is playing at home     
            if home_goals > away_goals:
                # Win
                match_points = 3
            elif home_goals == away_goals:
                # Draw
                match_points = 1
            else:
                # Loss
                match_points = 0
        
        elif is_away:
            # Club is playing away           
            if away_goals > home_goals:
                # Win
                match_points = 3
            elif away_goals == home_goals:
                # Draw
                match_points = 1
            else:
                # Loss
                match_points = 0
        
        # Add the points from this match to the list
        points_per_match.append(match_points)
    
    if calculation_type == "points_per_match":
        return points_per_match
    else:
        raise ValueError(f"Unknown calculation type: {calculation_type}")

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