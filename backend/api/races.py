"""
API endpoints for race management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database.connection import get_db
from models.database import Race, RaceResult

router = APIRouter()

# Pydantic models for request/response
class RaceCreate(BaseModel):
    year: int
    round_number: int
    location: str
    race_date: datetime
    predictions_close: datetime

class RaceResponse(BaseModel):
    id: int
    year: int
    round_number: int
    location: str
    race_date: datetime
    predictions_close: datetime
    completed: bool
    results_processed: bool
    
    class Config:
        from_attributes = True

class UpcomingRaceResponse(BaseModel):
    id: int
    year: int
    round_number: int
    location: str
    race_date: datetime
    predictions_close: datetime
    time_until_close: str  # Human readable
    can_predict: bool

@router.get("/upcoming", response_model=List[UpcomingRaceResponse])
async def get_upcoming_races(db: Session = Depends(get_db)):
    """Get upcoming races that haven't been completed"""
    now = datetime.utcnow()
    
    races = db.query(Race).filter(
        Race.completed == False,
        Race.race_date >= now
    ).order_by(Race.race_date).all()
    
    response = []
    for race in races:
        time_diff = race.predictions_close - now
        hours = int(time_diff.total_seconds() / 3600)
        
        if hours > 24:
            days = hours // 24
            time_str = f"{days} day{'s' if days != 1 else ''}"
        else:
            time_str = f"{hours} hour{'s' if hours != 1 else ''}"
        
        response.append(UpcomingRaceResponse(
            id=race.id,
            year=race.year,
            round_number=race.round_number,
            location=race.location,
            race_date=race.race_date,
            predictions_close=race.predictions_close,
            time_until_close=time_str,
            can_predict=(now < race.predictions_close)
        ))
    
    return response

@router.get("/{race_id}", response_model=RaceResponse)
async def get_race(race_id: int, db: Session = Depends(get_db)):
    """Get specific race details"""
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race

@router.post("/", response_model=RaceResponse)
async def create_race(race: RaceCreate, db: Session = Depends(get_db)):
    """Create a new race (admin only in production)"""
    db_race = Race(**race.dict())
    db.add(db_race)
    db.commit()
    db.refresh(db_race)
    return db_race

@router.get("/{race_id}/results")
async def get_race_results(race_id: int, db: Session = Depends(get_db)):
    """Get race results and performance analysis"""
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    if not race.results_processed:
        raise HTTPException(status_code=400, detail="Results not yet processed")
    
    results = db.query(RaceResult).filter(RaceResult.race_id == race_id).first()
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return {
        "race": RaceResponse.from_orm(race),
        "results": {
            "pole_driver": results.pole_driver,
            "podium": {
                "p1": results.podium_p1,
                "p2": results.podium_p2,
                "p3": results.podium_p3
            },
            "chaser": results.chaser_driver,
            "breakout_drivers": results.breakout_drivers,
            "bust_drivers": results.bust_drivers,
            "breakout_teams": results.breakout_teams,
            "bust_teams": results.bust_teams
        }
    }
