"""
API endpoints for race management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from humanize import naturaldelta

from database.connection import get_db
from models.database import Race

router = APIRouter()

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

class UpcomingRaceResponse(RaceResponse):
    time_until_close: str
    can_predict: bool

class RaceCreate(BaseModel):
    year: int
    round_number: int
    location: str
    race_date: datetime
    predictions_close: datetime


@router.get("/upcoming", response_model=List[UpcomingRaceResponse])
async def get_upcoming_races(db: Session = Depends(get_db)):
    """Get upcoming races that haven't been completed"""
    now = datetime.utcnow()
    
    races = db.query(Race).filter(
        Race.completed == False,
        Race.race_date >= now
    ).order_by(Race.race_date).all()
    
    result = []
    for race in races:
        time_diff = race.predictions_close - now
        can_predict = now < race.predictions_close
        
        try:
            time_until = naturaldelta(time_diff) if time_diff.total_seconds() > 0 else "Closed"
        except:
            time_until = str(time_diff) if time_diff.total_seconds() > 0 else "Closed"
        
        result.append(UpcomingRaceResponse(
            id=race.id,
            year=race.year,
            round_number=race.round_number,
            location=race.location,
            race_date=race.race_date,
            predictions_close=race.predictions_close,
            completed=race.completed,
            results_processed=race.results_processed,
            time_until_close=time_until,
            can_predict=can_predict
        ))
    
    return result


@router.get("/{race_id}", response_model=RaceResponse)
async def get_race(race_id: int, db: Session = Depends(get_db)):
    """Get race by ID"""
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.post("/", response_model=RaceResponse)
async def create_race(race: RaceCreate, db: Session = Depends(get_db)):
    """Create a new race (admin only in production)"""
    db_race = Race(**race.model_dump())
    db.add(db_race)
    db.commit()
    db.refresh(db_race)
    return db_race


@router.get("/", response_model=List[RaceResponse])
async def get_all_races(db: Session = Depends(get_db)):
    """Get all races"""
    races = db.query(Race).order_by(Race.race_date.desc()).all()
    return races
