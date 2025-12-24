"""
API endpoints for prediction management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from database.connection import get_db
from models.database import Prediction, Race

router = APIRouter()

# Pydantic models
class PredictionCreate(BaseModel):
    race_id: int
    pole_driver: str
    podium_p1: str
    podium_p2: str
    podium_p3: str
    chaser_driver: Optional[str] = None
    breakout_type: str  # 'driver' or 'team'
    breakout_name: str
    bust_type: str
    bust_name: str
    full_send_category: Optional[str] = None

class PredictionUpdate(BaseModel):
    chaser_driver: str  # Only chaser can be updated after initial submission

class PredictionResponse(BaseModel):
    id: int
    race_id: int
    pole_driver: str
    podium_p1: str
    podium_p2: str
    podium_p3: str
    chaser_driver: Optional[str]
    breakout_type: str
    breakout_name: str
    bust_type: str
    bust_name: str
    full_send_category: Optional[str]
    submitted_at: datetime
    locked_at: Optional[datetime]
    points_earned: float
    scored: bool
    
    class Config:
        from_attributes = True

@router.post("/", response_model=PredictionResponse)
async def submit_prediction(
    prediction: PredictionCreate,
    user_id: int,  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """Submit predictions for a race"""
    
    # Check if race exists and predictions are still open
    race = db.query(Race).filter(Race.id == prediction.race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    if datetime.utcnow() > race.predictions_close:
        raise HTTPException(status_code=400, detail="Predictions are closed for this race")
    
    # Check if user already has predictions for this race
    existing = db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.race_id == prediction.race_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Predictions already submitted. Use update endpoint to modify chaser.")
    
    # Create prediction
    db_prediction = Prediction(
        user_id=user_id,
        **prediction.dict()
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction

@router.put("/{prediction_id}/chaser", response_model=PredictionResponse)
async def update_chaser(
    prediction_id: int,
    update: PredictionUpdate,
    user_id: int,  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """Update chaser prediction (allowed until race start)"""
    
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if prediction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if race has started
    race = db.query(Race).filter(Race.id == prediction.race_id).first()
    if datetime.utcnow() > race.race_date:
        raise HTTPException(status_code=400, detail="Race has started, cannot update chaser")
    
    prediction.chaser_driver = update.chaser_driver
    db.commit()
    db.refresh(prediction)
    
    return prediction

@router.get("/user/{user_id}/race/{race_id}", response_model=PredictionResponse)
async def get_user_prediction(
    user_id: int,
    race_id: int,
    db: Session = Depends(get_db)
):
    """Get user's predictions for a specific race"""
    
    prediction = db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.race_id == race_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return prediction

@router.get("/race/{race_id}")
async def get_race_predictions(
    race_id: int,
    db: Session = Depends(get_db)
):
    """Get all predictions for a race (after predictions close)"""
    
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    # Only show predictions after they close
    if datetime.utcnow() < race.predictions_close:
        raise HTTPException(status_code=400, detail="Predictions still open")
    
    predictions = db.query(Prediction).filter(Prediction.race_id == race_id).all()
    return predictions
