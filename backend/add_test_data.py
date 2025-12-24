"""
Add test data to the Gridcall database
Run this after initializing the database
"""

from database.connection import SessionLocal, init_db
from models.database import User, Race
from datetime import datetime, timedelta

# Ensure database exists
init_db()

db = SessionLocal()

# Create test user
user = User(
    username="testuser",
    email="test@gridcall.com",
    hashed_password="password123"  # TODO: Add proper password hashing later
)
db.add(user)
db.commit()
db.refresh(user)

# Create upcoming test race (7 days from now)
race = Race(
    year=2024,
    round_number=24,
    location="Abu Dhabi",
    race_date=datetime.utcnow() + timedelta(days=7),
    predictions_close=datetime.utcnow() + timedelta(days=6, hours=20),
    completed=False,
    results_processed=False
)
db.add(race)
db.commit()
db.refresh(race)

print("=" * 50)
print("Test Data Created Successfully!")
print("=" * 50)
print(f"\n✓ Test User:")
print(f"  ID: {user.id}")
print(f"  Username: {user.username}")
print(f"  Email: {user.email}")
print(f"\n✓ Test Race:")
print(f"  ID: {race.id}")
print(f"  Location: {race.location}")
print(f"  Round: {race.round_number}")
print(f"  Race Date: {race.race_date.strftime('%Y-%m-%d %H:%M UTC')}")
print(f"  Predictions Close: {race.predictions_close.strftime('%Y-%m-%d %H:%M UTC')}")
print(f"\nYou can now:")
print(f"  1. Start the server: python3 main.py")
print(f"  2. Visit: http://localhost:8000/docs")
print(f"  3. Test the /api/races/upcoming endpoint")
print("=" * 50)

db.close()
