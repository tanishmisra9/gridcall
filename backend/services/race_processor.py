"""
Service to run performance analysis and process race results
Integrates with existing performance_analyzer.py
"""

import sys
import os
from sqlalchemy.orm import Session
import json

# Add project root to Python path to import from src/
# This file is at: backend/services/race_processor.py
# Project root is: ../../ from here
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import from your existing src/ directory
from src.data_fetcher import F1DataFetcher, TeammateBattleFetcher
from models.database import Race, RaceResult, Prediction

def process_race_results(race_id: int, db: Session):
    """
    Process race results and calculate performance scores.
    This integrates your existing performance_analyzer.py logic.
    """
    
    # Get race from database
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise ValueError(f"Race {race_id} not found")
    
    print(f"Processing results for {race.location} (Round {race.round_number})")
    
    # Initialize fetchers (from your existing code)
    data_fetcher = F1DataFetcher(race.year, race.round_number)
    teammate_fetcher = TeammateBattleFetcher(race.year, race.round_number)
    
    # Fetch data
    quali_results = data_fetcher.get_qualifying_results()
    race_results = data_fetcher.get_race_results()
    teammate_quali = teammate_fetcher.get_teammate_quali_comparison()
    teammate_race = teammate_fetcher.get_teammate_race_comparison()
    wcc_standings = data_fetcher.get_wcc_standings_after_race()
    
    # Calculate performance scores (from your existing code)
    from src.performance_analyzer import calculate_weekend_performance, identify_breakout_bust
    
    performance_scores = calculate_weekend_performance(
        race_results, quali_results, wcc_standings, teammate_race, teammate_quali
    )
    
    if performance_scores.empty:
        raise ValueError("Could not calculate performance scores")
    
    # Identify breakout and bust
    breakout_drivers, bust_drivers = identify_breakout_bust(performance_scores)
    
    # Extract objective results
    pole_driver = quali_results.iloc[0]['Abbreviation'] if not quali_results.empty else None
    podium_p1 = race_results[race_results['Position'] == 1]['Abbreviation'].iloc[0] if len(race_results[race_results['Position'] == 1]) > 0 else None
    podium_p2 = race_results[race_results['Position'] == 2]['Abbreviation'].iloc[0] if len(race_results[race_results['Position'] == 2]) > 0 else None
    podium_p3 = race_results[race_results['Position'] == 3]['Abbreviation'].iloc[0] if len(race_results[race_results['Position'] == 3]) > 0 else None
    
    # Get chaser (most positions gained)
    positions_gained = data_fetcher.get_positions_gained_ranking()
    chaser_driver = positions_gained.iloc[0]['Abbreviation'] if not positions_gained.empty else None
    
    # Calculate team performance for breakout/bust teams
    # Group performance scores by team
    team_performance = performance_scores.groupby('Team').agg({
        'TotalScore': 'mean'
    }).sort_values('TotalScore', ascending=False).reset_index()
    
    breakout_teams = team_performance.head(3)['Team'].tolist()
    bust_teams = team_performance.tail(3)['Team'].tolist()
    
    # Create or update RaceResult
    result = db.query(RaceResult).filter(RaceResult.race_id == race_id).first()
    if not result:
        result = RaceResult(race_id=race_id)
        db.add(result)
    
    result.pole_driver = pole_driver
    result.podium_p1 = podium_p1
    result.podium_p2 = podium_p2
    result.podium_p3 = podium_p3
    result.chaser_driver = chaser_driver
    result.breakout_drivers = json.dumps([d['Driver'] for d in breakout_drivers])
    result.bust_drivers = json.dumps([d['Driver'] for d in bust_drivers])
    result.breakout_teams = json.dumps(breakout_teams)
    result.bust_teams = json.dumps(bust_teams)
    result.performance_data = json.dumps(performance_scores.to_dict('records'))
    
    # Mark race as completed and results processed
    race.completed = True
    race.results_processed = True
    
    db.commit()
    
    print(f"Results processed successfully")
    
    return result


def score_predictions(race_id: int, db: Session):
    """
    Score all predictions for a completed race
    """
    
    # Get race results
    result = db.query(RaceResult).filter(RaceResult.race_id == race_id).first()
    if not result:
        raise ValueError(f"Results not found for race {race_id}")
    
    # Get all predictions for this race
    predictions = db.query(Prediction).filter(Prediction.race_id == race_id).all()
    
    breakout_drivers = json.loads(result.breakout_drivers)
    bust_drivers = json.loads(result.bust_drivers)
    breakout_teams = json.loads(result.breakout_teams)
    bust_teams = json.loads(result.bust_teams)
    
    for prediction in predictions:
        points = 0.0
        
        # Pole position (1 pt)
        if prediction.pole_driver == result.pole_driver:
            points += 1
            if prediction.full_send_category == 'pole':
                points += 1
        
        # Podium scoring
        podium_points = 0
        
        # P1
        if prediction.podium_p1 == result.podium_p1:
            podium_points += 2  # Correct driver + position
        elif prediction.podium_p1 in [result.podium_p2, result.podium_p3]:
            podium_points += 1  # Correct driver, wrong position
        
        # P2
        if prediction.podium_p2 == result.podium_p2:
            podium_points += 2
        elif prediction.podium_p2 in [result.podium_p1, result.podium_p3]:
            podium_points += 1
        
        # P3
        if prediction.podium_p3 == result.podium_p3:
            podium_points += 2
        elif prediction.podium_p3 in [result.podium_p1, result.podium_p2]:
            podium_points += 1
        
        if prediction.full_send_category == 'podium':
            podium_points *= 2
        
        points += podium_points
        
        # Chaser (1 pt)
        if prediction.chaser_driver == result.chaser_driver:
            chaser_points = 1
            if prediction.full_send_category == 'chaser':
                chaser_points *= 2
            points += chaser_points
        
        # Breakout
        breakout_points = 0
        if prediction.breakout_type == 'driver':
            if prediction.breakout_name in breakout_drivers:
                breakout_points = 1
        else:  # team
            if prediction.breakout_name in breakout_teams:
                breakout_points = 2
        
        if prediction.full_send_category == 'breakout':
            breakout_points *= 2
        points += breakout_points
        
        # Bust
        bust_points = 0
        if prediction.bust_type == 'driver':
            if prediction.bust_name in bust_drivers:
                bust_points = 1
        else:  # team
            if prediction.bust_name in bust_teams:
                bust_points = 2
        
        if prediction.full_send_category == 'bust':
            bust_points *= 2
        points += bust_points
        
        # Update prediction with score
        prediction.points_earned = points
        prediction.scored = True
    
    db.commit()
    
    print(f"Scored {len(predictions)} predictions")
