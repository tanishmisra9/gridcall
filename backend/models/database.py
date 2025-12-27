"""
Database models for Gridcall
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

# Association table for Grid membership (many-to-many)
grid_members = Table(
    'grid_members',
    Base.metadata,
    Column('grid_id', Integer, ForeignKey('grids.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user")
    grids = relationship("Grid", secondary=grid_members, back_populates="members")
    created_grids = relationship("Grid", back_populates="creator", foreign_keys="Grid.created_by")


class Race(Base):
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    round_number = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    race_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    results_processed = Column(Boolean, default=False)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="race")
    results = relationship("RaceResult", back_populates="race", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    
    # Prediction fields
    pole_driver = Column(String)
    podium_p1 = Column(String)
    podium_p2 = Column(String)
    podium_p3 = Column(String)
    chaser_driver = Column(String)
    breakout_type = Column(String)  # 'driver' or 'team'
    breakout_name = Column(String)
    bust_type = Column(String)      # 'driver' or 'team'
    bust_name = Column(String)
    full_send_category = Column(String, nullable=True)  # Category to double points
    
    # Scoring
    points_earned = Column(Float, default=0.0)
    scored = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    race = relationship("Race", back_populates="predictions")


class Grid(Base):
    __tablename__ = "grids"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship("User", secondary=grid_members, back_populates="grids")
    creator = relationship("User", back_populates="created_grids", foreign_keys=[created_by])


class RaceResult(Base):
    __tablename__ = "race_results"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    
    # Objective results
    pole_driver = Column(String)
    podium_p1 = Column(String)
    podium_p2 = Column(String)
    podium_p3 = Column(String)
    chaser_driver = Column(String)
    chaser_positions_gained = Column(Integer)  # ADDED THIS FIELD
    
    # Subjective results (from performance analyzer)
    breakout_drivers = Column(String)  # JSON list
    breakout_teams = Column(String)    # JSON list
    bust_drivers = Column(String)      # JSON list
    bust_teams = Column(String)        # JSON list
    
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race", back_populates="results")