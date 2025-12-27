"""
API endpoints for race management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from database.connection import get_db
from models.database import Race, RaceResult, Prediction
from services.scoring_service import ScoringService
from services.data_availability import DataAvailabilityChecker
from auth import get_current_user, User

router = APIRouter()


class RaceCreate(BaseModel):
    year: int
    round_number: int
    location: str
    race_date: datetime


class RaceResponse(BaseModel):
    id: int
    year: int
    round_number: int
    location: str
    race_date: datetime
    completed: bool
    results_processed: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[RaceResponse])
async def get_races(db: Session = Depends(get_db)):
    """Get all races"""
    races = db.query(Race).all()
    return races


@router.get("/{race_id}", response_model=RaceResponse)
async def get_race(race_id: int, db: Session = Depends(get_db)):
    """Get a specific race"""
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.post("/", response_model=RaceResponse)
async def create_race(race: RaceCreate, db: Session = Depends(get_db)):
    """Create a new race"""
    db_race = Race(**race.dict())
    db.add(db_race)
    db.commit()
    db.refresh(db_race)
    return db_race


# ==================== SCORING ENDPOINTS ====================

@router.get("/{race_id}/scoring-status")
async def get_scoring_status(race_id: int, db: Session = Depends(get_db)):
    """
    Check if a race is ready to be scored.
    Returns detailed status information.
    """
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        checker = DataAvailabilityChecker(
            year=race.year,
            round_number=race.round_number,
            race_date=race.race_date
        )
        status = checker.get_availability_status()
        
        return {
            "race_id": race_id,
            "location": race.location,
            "already_scored": race.results_processed,
            **status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{race_id}/trigger-scoring")
async def trigger_scoring(
    race_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger scoring for a race.
    Requires authentication.
    """
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        scoring_service = ScoringService(db)
        summary = scoring_service.score_race(race_id)
        
        return {
            "success": True,
            "message": f"Scored {summary['predictions_scored']} predictions",
            **summary
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{race_id}/results")
async def get_race_results(race_id: int, db: Session = Depends(get_db)):
    """
    Get actual race results and all predictions with points.
    """
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    # Get race result
    race_result = db.query(RaceResult).filter(
        RaceResult.race_id == race_id
    ).first()
    
    if not race_result:
        raise HTTPException(status_code=404, detail="Race not scored yet")
    
    # Get all predictions with user info
    predictions = db.query(Prediction).filter(
        Prediction.race_id == race_id,
        Prediction.scored == True
    ).all()
    
    return {
        "race_id": race_id,
        "location": race.location,
        "race_date": race.race_date,
        "actual_results": {
            "pole": race_result.pole_driver,
            "podium": {
                "p1": race_result.podium_p1,
                "p2": race_result.podium_p2,
                "p3": race_result.podium_p3
            },
            "chaser": {
                "driver": race_result.chaser_driver,
                "positions_gained": race_result.chaser_positions_gained
            },
            "breakouts": {
                "drivers": json.loads(race_result.breakout_drivers),
                "teams": json.loads(race_result.breakout_teams)
            },
            "busts": {
                "drivers": json.loads(race_result.bust_drivers),
                "teams": json.loads(race_result.bust_teams)
            }
        },
        "predictions": [
            {
                "user_id": p.user_id,
                "points_earned": p.points_earned,
                "predictions": {
                    "pole": p.pole_driver,
                    "podium": [p.podium_p1, p.podium_p2, p.podium_p3],
                    "chaser": p.chaser_driver,
                    "breakout": f"{p.breakout_type}: {p.breakout_name}",
                    "bust": f"{p.bust_type}: {p.bust_name}",
                    "full_send": p.full_send_category
                }
            }
            for p in predictions
        ]
    }