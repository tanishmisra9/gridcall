"""
API endpoints for prediction management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from models.database import Prediction, Race, User
from auth import get_current_user

router = APIRouter()

class PredictionCreate(BaseModel):
    race_id: int
    pole_driver: str
    podium_p1: str
    podium_p2: str
    podium_p3: str
    chaser_driver: Optional[str] = None
    breakout_type: str  # 'driver' or 'team'
    breakout_name: str
    bust_type: str  # 'driver' or 'team'
    bust_name: str
    full_send_category: Optional[str] = None

class PredictionResponse(BaseModel):
    id: int
    user_id: int
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
    points_earned: float
    scored: bool
    submitted_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    prediction: PredictionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new prediction for a race"""
    
    # Check if race exists
    race = db.query(Race).filter(Race.id == prediction.race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    # Check if predictions are still open
    if datetime.utcnow() > race.predictions_close:
        raise HTTPException(status_code=400, detail="Predictions are closed for this race")
    
    # Check if user already has a prediction for this race
    existing = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.race_id == prediction.race_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have a prediction for this race. Use PUT to update.")
    
    # Create prediction
    db_prediction = Prediction(
        user_id=current_user.id,
        **prediction.model_dump()
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


@router.put("/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: int,
    prediction: PredictionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing prediction"""
    
    db_prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not db_prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if db_prediction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your prediction")
    
    # Check if predictions are still open
    race = db.query(Race).filter(Race.id == db_prediction.race_id).first()
    if datetime.utcnow() > race.predictions_close:
        raise HTTPException(status_code=400, detail="Predictions are closed for this race")
    
    # Update fields
    for key, value in prediction.model_dump().items():
        if key != 'race_id':  # Don't allow changing race
            setattr(db_prediction, key, value)
    
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


@router.get("/user/me/race/{race_id}", response_model=PredictionResponse)
async def get_my_prediction(
    race_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's prediction for a specific race"""
    prediction = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.race_id == race_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No prediction found")
    
    return prediction


@router.get("/race/{race_id}", response_model=List[PredictionResponse])
async def get_race_predictions(
    race_id: int,
    db: Session = Depends(get_db)
):
    """Get all predictions for a race (for leaderboard)"""
    predictions = db.query(Prediction).filter(
        Prediction.race_id == race_id
    ).all()
    
    return predictions


@router.get("/user/{user_id}", response_model=List[PredictionResponse])
async def get_user_predictions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all predictions for a user"""
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.submitted_at.desc()).all()
    
    return predictions
