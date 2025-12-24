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
from auth import get_current_user

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new grid"""
    
    # Generate unique invite code
    invite_code = secrets.token_urlsafe(8)
    
    db_grid = Grid(
        name=grid.name,
        invite_code=invite_code,
        created_by=current_user.id
    )
    db.add(db_grid)
    
    # Add creator as member
    db_grid.members.append(current_user)
    
    db.commit()
    db.refresh(db_grid)
    
    return GridResponse(
        id=db_grid.id,
        name=db_grid.name,
        invite_code=db_grid.invite_code,
        created_by=db_grid.created_by,
        member_count=len(db_grid.members)
    )


@router.post("/{invite_code}/join", response_model=GridResponse)
async def join_grid(
    invite_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a grid using invite code"""
    
    grid = db.query(Grid).filter(Grid.invite_code == invite_code).first()
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    
    # Check if already a member
    if current_user in grid.members:
        raise HTTPException(status_code=400, detail="Already a member of this grid")
    
    grid.members.append(current_user)
    db.commit()
    db.refresh(grid)
    
    return GridResponse(
        id=grid.id,
        name=grid.name,
        invite_code=grid.invite_code,
        created_by=grid.created_by,
        member_count=len(grid.members)
    )


@router.get("/my", response_model=List[GridResponse])
async def get_my_grids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all grids the current user belongs to"""
    
    grids = current_user.grids
    
    return [
        GridResponse(
            id=grid.id,
            name=grid.name,
            invite_code=grid.invite_code,
            created_by=grid.created_by,
            member_count=len(grid.members)
        )
        for grid in grids
    ]


@router.get("/{grid_id}", response_model=GridResponse)
async def get_grid(
    grid_id: int,
    db: Session = Depends(get_db)
):
    """Get grid details by ID"""
    
    grid = db.query(Grid).filter(Grid.id == grid_id).first()
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    
    return GridResponse(
        id=grid.id,
        name=grid.name,
        invite_code=grid.invite_code,
        created_by=grid.created_by,
        member_count=len(grid.members)
    )
