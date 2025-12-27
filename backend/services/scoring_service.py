"""
Scoring service for Gridcall predictions.
Scores user predictions against actual race results using PerformanceAnalyzer.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session

# Add src to path for performance analyzer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from performance_analyzer import PerformanceAnalyzer
from .data_availability import DataAvailabilityChecker
from models.database import Race, Prediction, RaceResult


class ScoringService:
    """
    Service for scoring race predictions.
    Fetches actual results, scores each prediction, and updates database.
    """
    
    def __init__(self, db: Session):
        """
        Initialize scoring service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def score_race(self, race_id: int) -> Dict:
        """
        Score all predictions for a race.
        
        This is the main entry point for scoring a race.
        
        Args:
            race_id: Database ID of the race to score
            
        Returns:
            dict: Summary of scoring results
            
        Raises:
            ValueError: If race not found or not ready to score
        """
        # Get race from database
        race = self.db.query(Race).filter(Race.id == race_id).first()
        if not race:
            raise ValueError(f"Race {race_id} not found")
        
        # Check if race is ready to score
        checker = DataAvailabilityChecker(
            year=race.year,
            round_number=race.round_number,
            race_date=race.race_date
        )
        
        if not checker.is_ready_to_score():
            status = checker.get_availability_status()
            raise ValueError(f"Race not ready to score: {status['status_message']}")
        
        # Check if already scored
        if race.results_processed:
            raise ValueError(f"Race {race_id} already scored")
        
        # Get actual race results using PerformanceAnalyzer
        print(f"Analyzing race results for {race.year} Round {race.round_number}...")
        analyzer = PerformanceAnalyzer(race.year, race.round_number)
        analyzer.fetch_all_data()
        actual_results = analyzer.get_all_results()
        
        # Create RaceResult record
        race_result = RaceResult(
            race_id=race_id,
            pole_driver=actual_results['pole'],
            podium_p1=actual_results['podium']['p1'],
            podium_p2=actual_results['podium']['p2'],
            podium_p3=actual_results['podium']['p3'],
            chaser_driver=actual_results['chaser']['driver'],
            chaser_positions_gained=actual_results['chaser']['positions_gained'],
            breakout_drivers=json.dumps(actual_results['breakouts']['drivers']),
            breakout_teams=json.dumps(actual_results['breakouts']['teams']),
            bust_drivers=json.dumps(actual_results['busts']['drivers']),
            bust_teams=json.dumps(actual_results['busts']['teams'])
        )
        self.db.add(race_result)
        
        # Get all predictions for this race
        predictions = self.db.query(Prediction).filter(
            Prediction.race_id == race_id
        ).all()
        
        scoring_summary = {
            'race_id': race_id,
            'total_predictions': len(predictions),
            'predictions_scored': 0,
            'total_points_awarded': 0.0,
            'scoring_timestamp': datetime.utcnow().isoformat()
        }
        
        # Score each prediction
        for prediction in predictions:
            # Convert to dict for _score_prediction
            pred_dict = {
                'id': prediction.id,
                'pole_driver': prediction.pole_driver,
                'podium_p1': prediction.podium_p1,
                'podium_p2': prediction.podium_p2,
                'podium_p3': prediction.podium_p3,
                'chaser_driver': prediction.chaser_driver,
                'breakout_type': prediction.breakout_type,
                'breakout_name': prediction.breakout_name,
                'bust_type': prediction.bust_type,
                'bust_name': prediction.bust_name,
                'full_send_category': prediction.full_send_category
            }
            
            points = self._score_prediction(pred_dict, actual_results)
            
            # Update prediction
            prediction.points_earned = points
            prediction.scored = True
            
            scoring_summary['predictions_scored'] += 1
            scoring_summary['total_points_awarded'] += points
            
            print(f"  Scored prediction {prediction.id}: {points} points")
        
        # Mark race as processed
        race.results_processed = True
        
        # Commit all changes
        self.db.commit()
        
        print(f"Scoring complete! {scoring_summary['predictions_scored']} predictions scored.")
        
        return scoring_summary
    
    def _score_prediction(self, prediction: Dict, actual_results: Dict) -> float:
        """
        Score a single prediction against actual results.
        
        Args:
            prediction: User's prediction
            actual_results: Actual race results from PerformanceAnalyzer
            
        Returns:
            float: Total points earned
        """
        points = 0.0
        category_points = {
            'pole': 0.0,
            'podium': 0.0,
            'chaser': 0.0,
            'breakout': 0.0,
            'bust': 0.0
        }
        
        # 1. POLE POSITION (1 pt)
        if prediction['pole_driver'] == actual_results['pole']:
            category_points['pole'] = 1.0
        
        # 2. PODIUM
        # 1 pt for correctly selecting a driver (regardless of position)
        # 2 pts for correctly selecting both driver AND position
        podium_drivers = [
            actual_results['podium']['p1'],
            actual_results['podium']['p2'],
            actual_results['podium']['p3']
        ]
        
        for position in ['p1', 'p2', 'p3']:
            predicted_driver = prediction[f'podium_{position}']
            actual_driver = actual_results['podium'][position]
            
            if predicted_driver == actual_driver:
                # Correct driver in correct position: 2 pts
                category_points['podium'] += 2.0
            elif predicted_driver in podium_drivers:
                # Correct driver, wrong position: 1 pt
                category_points['podium'] += 1.0
        
        # 3. CHASER (1 pt)
        if prediction['chaser_driver'] == actual_results['chaser']['driver']:
            category_points['chaser'] = 1.0
        
        # 4. BREAKOUT
        # 1 pt for driver, 2 pts for team
        if prediction['breakout_type'] == 'driver':
            if prediction['breakout_name'] in actual_results['breakouts']['drivers']:
                category_points['breakout'] = 1.0
        else:  # team
            if prediction['breakout_name'] in actual_results['breakouts']['teams']:
                category_points['breakout'] = 2.0
        
        # 5. BUST
        # 1 pt for driver, 2 pts for team
        if prediction['bust_type'] == 'driver':
            if prediction['bust_name'] in actual_results['busts']['drivers']:
                category_points['bust'] = 1.0
        else:  # team
            if prediction['bust_name'] in actual_results['busts']['teams']:
                category_points['bust'] = 2.0
        
        # 6. FULL SEND (double points for the selected category)
        if prediction['full_send_category']:
            category = prediction['full_send_category']
            if category in category_points and category_points[category] > 0:
                # Double the points for this category
                category_points[category] *= 2
        
        # Calculate total
        points = sum(category_points.values())
        
        return points