"""
Data availability checker for F1 race results.
Determines when races are ready to be scored based on FastF1 data availability
and Monday wait period for penalties/DSQs.
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Dict
import logging

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    import fastf1 as f1
    FASTF1_AVAILABLE = True
except ImportError:
    FASTF1_AVAILABLE = False
    logging.warning("FastF1 not available - data availability checks will fail")

# Suppress FastF1 logging
logging.getLogger('fastf1').setLevel(logging.ERROR)
logging.getLogger('fastf1.core').setLevel(logging.ERROR)
logging.getLogger('fastf1.api').setLevel(logging.ERROR)
logging.getLogger('fastf1.req').setLevel(logging.ERROR)


class DataAvailabilityChecker:
    """
    Checks if FastF1 has complete race data available for scoring.
    Enforces Monday 00:00 UTC wait period for penalties/DSQs to be finalized.
    """
    
    def __init__(self, year: int, round_number: int, race_date: datetime):
        """
        Initialize data availability checker.
        
        Args:
            year: Season year
            round_number: Round number
            race_date: UTC datetime when race occurred
        """
        self.year = year
        self.round_number = round_number
        self.race_date = race_date
        
        if not FASTF1_AVAILABLE:
            raise ImportError("FastF1 library is required for data availability checking")
        
        # Setup FastF1 cache
        cache_dir = "./fastf1cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        f1.Cache.enable_cache(cache_dir)
    
    def _calculate_monday_deadline(self) -> datetime:
        """
        Calculate the Monday 00:00 UTC after the race.
        
        Returns:
            datetime: Monday 00:00 UTC following the race
        """
        # Ensure race_date is timezone-aware (UTC)
        if self.race_date.tzinfo is None:
            race_date_utc = self.race_date.replace(tzinfo=timezone.utc)
        else:
            race_date_utc = self.race_date.astimezone(timezone.utc)
        
        # Find the next Monday after the race
        # Monday = 0 in weekday()
        days_until_monday = (7 - race_date_utc.weekday()) % 7
        
        # If race is on Monday, wait until the following Monday
        if days_until_monday == 0:
            days_until_monday = 7
        
        monday_date = race_date_utc + timedelta(days=days_until_monday)
        
        # Set to 00:00:00 UTC
        monday_deadline = monday_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return monday_deadline
    
    def _check_fastf1_data_available(self) -> bool:
        """
        Check if FastF1 has complete race data (results + lap data).
        
        Returns:
            bool: True if data is complete and accessible
        """
        try:
            # Load event
            event = f1.get_event(self.year, self.round_number)
            
            # Load race session
            race = event.get_race()
            
            # Load session data - need both results and laps for complete analysis
            race.load(laps=True, telemetry=False, weather=False, messages=False)
            
            # Verify results DataFrame is populated
            if race.results is None or race.results.empty:
                return False
            
            # Verify we have position data
            if race.results['Position'].isna().all():
                return False
            
            # Verify lap data exists (needed for positions gained calculation)
            if race.laps is None or race.laps.empty:
                return False
            
            # Data appears complete
            return True
            
        except Exception as e:
            # Any error means data is not available
            logging.debug(f"FastF1 data check failed: {e}")
            return False
    
    def is_past_monday_deadline(self) -> bool:
        """
        Check if current time is past the Monday 00:00 UTC deadline.
        
        Returns:
            bool: True if we're past Monday deadline
        """
        monday_deadline = self._calculate_monday_deadline()
        current_time = datetime.now(timezone.utc)
        
        return current_time >= monday_deadline
    
    def is_data_available(self) -> bool:
        """
        Check if FastF1 has complete race data available.
        This is separate from the Monday check.
        
        Returns:
            bool: True if data is available in FastF1
        """
        return self._check_fastf1_data_available()
    
    def is_ready_to_score(self) -> bool:
        """
        Check if race is ready to score (past Monday AND data available).
        
        Returns:
            bool: True if ready to score
        """
        # Must be past Monday deadline
        if not self.is_past_monday_deadline():
            return False
        
        # Must have data available
        if not self.is_data_available():
            return False
        
        return True
    
    def get_availability_status(self) -> Dict:
        """
        Get detailed availability status for debugging/admin interface.
        
        Returns:
            dict: Detailed status information
        """
        current_time = datetime.now(timezone.utc)
        monday_deadline = self._calculate_monday_deadline()
        past_monday = self.is_past_monday_deadline()
        data_available = self.is_data_available()
        ready = self.is_ready_to_score()
        
        # Calculate time until Monday (if not past)
        if not past_monday:
            time_until_monday = monday_deadline - current_time
            hours_until_monday = int(time_until_monday.total_seconds() / 3600)
            minutes_until_monday = int((time_until_monday.total_seconds() % 3600) / 60)
            time_until_monday_str = f"{hours_until_monday}h {minutes_until_monday}m"
        else:
            time_until_monday_str = "Past deadline"
        
        # Calculate time since race
        time_since_race = current_time - self.race_date.replace(tzinfo=timezone.utc)
        hours_since_race = int(time_since_race.total_seconds() / 3600)
        
        status = {
            'year': self.year,
            'round_number': self.round_number,
            'race_date': self.race_date.isoformat(),
            'current_time': current_time.isoformat(),
            'monday_deadline': monday_deadline.isoformat(),
            'hours_since_race': hours_since_race,
            'past_monday_deadline': past_monday,
            'time_until_monday': time_until_monday_str,
            'fastf1_data_available': data_available,
            'ready_to_score': ready,
            'status_message': self._get_status_message(past_monday, data_available, ready)
        }
        
        return status
    
    def _get_status_message(self, past_monday: bool, data_available: bool, ready: bool) -> str:
        """
        Generate human-readable status message.
        
        Args:
            past_monday: Whether we're past Monday deadline
            data_available: Whether FastF1 data is available
            ready: Whether ready to score
            
        Returns:
            str: Status message
        """
        if ready:
            return "Ready to score"
        
        if not past_monday:
            return "Waiting for Monday deadline"
        
        if not data_available:
            return "Past Monday deadline, waiting for FastF1 data"
        
        return "Unknown status"


# Convenience function for quick checks
def check_race_ready(year: int, round_number: int, race_date: datetime) -> bool:
    """
    Quick check if a race is ready to score.
    
    Args:
        year: Season year
        round_number: Round number
        race_date: UTC datetime when race occurred
        
    Returns:
        bool: True if ready to score
    """
    try:
        checker = DataAvailabilityChecker(year, round_number, race_date)
        return checker.is_ready_to_score()
    except Exception:
        return False