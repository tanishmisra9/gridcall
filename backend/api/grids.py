"""
API endpoints for Grid (friend group) management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import secrets

from database.connection import get_db
from models.database import Grid, User

router = APIRouter()

class GridCreate(BaseModel):
    name: str

class GridResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    created_by: int
    member_count: int
    
    class Config:
        from_attributes = True

@router.post("/", response_model=GridResponse)
async def create_grid(
    grid: GridCreate,
    user_id: int,  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """Create a new grid"""
    
    # Generate unique invite code
    invite_code = secrets.token_urlsafe(8)
    
    db_grid = Grid(
        name=grid.name,
        invite_code=invite_code,
        created_by=user_id
    )
    db.add(db_grid)
    
    # Add creator as member
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db_grid.members.append(user)
    
    db.commit()
    db.refresh(db_grid)
    
    return GridResponse(
        id=db_grid.id,
        name=db_grid.name,
        invite_code=db_grid.invite_code,
        created_by=db_grid.created_by,
        member_count=len(db_grid.members)
    )

@router.post("/{invite_code}/join")
async def join_grid(
    invite_code: str,
    user_id: int,  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """Join a grid using invite code"""
    
    grid = db.query(Grid).filter(Grid.invite_code == invite_code).first()
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user in grid.members:
        raise HTTPException(status_code=400, detail="Already a member of this grid")
    
    grid.members.append(user)
    db.commit()
    
    return {"message": "Successfully joined grid", "grid_name": grid.name}

@router.get("/user/{user_id}")
async def get_user_grids(user_id: int, db: Session = Depends(get_db)):
    """Get all grids a user is part of"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    grids = []
    for grid in user.grids:
        grids.append(GridResponse(
            id=grid.id,
            name=grid.name,
            invite_code=grid.invite_code,
            created_by=grid.created_by,
            member_count=len(grid.members)
        ))
    
    return grids
