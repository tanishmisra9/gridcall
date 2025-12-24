"""
Database models for Gridcall
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Many-to-many relationship table for users and grids
grid_members = Table(
    'grid_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('grid_id', Integer, ForeignKey('grids.id'))
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


class Grid(Base):
    __tablename__ = "grids"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship("User", secondary=grid_members, back_populates="grids")


class Race(Base):
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    round_number = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    race_date = Column(DateTime, nullable=False)
    predictions_close = Column(DateTime, nullable=False)  # When predictions lock
    completed = Column(Boolean, default=False)
    results_processed = Column(Boolean, default=False)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="race")
    results = relationship("RaceResult", back_populates="race")


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    
    # Objective predictions
    pole_driver = Column(String)  # Driver abbreviation
    podium_p1 = Column(String)
    podium_p2 = Column(String)
    podium_p3 = Column(String)
    chaser_driver = Column(String)  # Editable until race start
    
    # Subjective predictions
    breakout_type = Column(String)  # 'driver' or 'team'
    breakout_name = Column(String)  # Abbreviation or team name
    bust_type = Column(String)  # 'driver' or 'team'
    bust_name = Column(String)
    
    # Full Send feature
    full_send_category = Column(String)  # Which category to double points
    
    # Scoring
    points_earned = Column(Float, default=0)
    scored = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    race = relationship("Race", back_populates="predictions")


class RaceResult(Base):
    __tablename__ = "race_results"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    
    # Actual results
    pole_driver = Column(String)
    podium_p1 = Column(String)
    podium_p2 = Column(String)
    podium_p3 = Column(String)
    fastest_lap_driver = Column(String)
    
    # Breakout/bust analysis results (from your performance analyzer)
    breakout_drivers = Column(String)  # JSON list
    breakout_teams = Column(String)  # JSON list
    bust_drivers = Column(String)  # JSON list
    bust_teams = Column(String)  # JSON list
    
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race", back_populates="results")
