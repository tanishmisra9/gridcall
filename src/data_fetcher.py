"""
Data fetcher module for F1 race data using FastF1.
Provides methods to retrieve race results, qualifying data, and driver/team comparisons.
"""

import fastf1 as f1
import pandas as pd
import os
from typing import Optional, Dict, List, Tuple

# Setup cache
CACHE_DIR = "./fastf1cache"
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)
f1.Cache.enable_cache(CACHE_DIR)


class F1DataFetcher:
    """Main class for fetching and processing F1 data"""
    
    def __init__(self, year: int, round_number: int):
        """
        Initialize the data fetcher for a specific race weekend.
        
        Args:
            year: Season year
            round_number: Round number in the season
        """
        self.year = year
        self.round_number = round_number
        self.event = f1.get_event(year, round_number)
        self.location = self.event['Location']
        
    def get_race_results(self, sprint: bool = False) -> pd.DataFrame:
        """
        Get race results for main or sprint race.
        
        Args:
            sprint: If True, get sprint race results, else main race
            
        Returns:
            DataFrame with race results
        """
        try:
            if sprint:
                session = self.event.get_sprint()
            else:
                session = self.event.get_race()
            
            session.load()
            
            # Get results
            results = session.results.copy()
            
            # Use ClassifiedPosition if Position is all NaN
            if results['Position'].isna().all() and not results['ClassifiedPosition'].isna().all():
                results['Position'] = results['ClassifiedPosition']
            
            # If GridPosition is missing/NaN, try to get it from qualifying
            if results['GridPosition'].isna().any():
                try:
                    quali = self.get_qualifying_results(sprint_quali=sprint)
                    if not quali.empty:
                        # Map qualifying position to grid position for drivers
                        for idx, row in results.iterrows():
                            if pd.isna(row['GridPosition']):
                                quali_pos = quali[quali['Abbreviation'] == row['Abbreviation']]['Position']
                                if not quali_pos.empty and pd.notna(quali_pos.iloc[0]):
                                    results.at[idx, 'GridPosition'] = quali_pos.iloc[0]
                except:
                    pass
            
            # Fix pit lane starts (GridPosition = 0)
            # Count how many drivers started from pit lane
            pit_lane_starters = results[results['GridPosition'] == 0].copy()
            if len(pit_lane_starters) > 0:
                # Get the maximum grid position
                max_grid = results[results['GridPosition'] > 0]['GridPosition'].max()
                if pd.notna(max_grid):
                    # Assign pit lane starters positions after the last grid position
                    # Sort by driver number for consistency
                    pit_lane_starters = pit_lane_starters.sort_values('DriverNumber')
                    for i, (idx, row) in enumerate(pit_lane_starters.iterrows()):
                        results.at[idx, 'GridPosition'] = max_grid + i + 1
            
            columns_to_keep = [
                'DriverNumber', 'Abbreviation', 'TeamName', 'FullName',
                'Position', 'ClassifiedPosition', 'GridPosition',
                'Time', 'Status', 'Points'
            ]
            
            return results[columns_to_keep].copy()
            
        except Exception as e:
            print(f"Error fetching race results: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_qualifying_results(self, sprint_quali: bool = False) -> pd.DataFrame:
        """
        Get qualifying results for main or sprint qualifying.
        
        Args:
            sprint_quali: If True, get sprint qualifying/shootout, else main qualifying
            
        Returns:
            DataFrame with qualifying results
        """
        try:
            if sprint_quali:
                try:
                    session = self.event.get_sprint_qualifying()
                except:
                    session = self.event.get_sprint_shootout()
            else:
                session = self.event.get_qualifying()
            
            session.load()
            
            columns_to_keep = [
                'DriverNumber', 'Abbreviation', 'TeamName', 'FullName',
                'Position', 'ClassifiedPosition', 'GridPosition',
                'Q1', 'Q2', 'Q3'
            ]
            
            return session.results[columns_to_keep].copy()
            
        except Exception as e:
            print(f"Error fetching qualifying results: {e}")
            return pd.DataFrame()
    
    def get_driver_weekend_summary(self, driver_abbr: str) -> Dict:
        """
        Get complete weekend summary for a specific driver.
        
        Args:
            driver_abbr: Driver abbreviation (e.g., 'VER', 'HAM')
            
        Returns:
            Dictionary with weekend performance data
        """
        quali = self.get_qualifying_results()
        race = self.get_race_results()
        
        driver_quali = quali[quali['Abbreviation'] == driver_abbr]
        driver_race = race[race['Abbreviation'] == driver_abbr]
        
        summary = {
            'driver': driver_abbr,
            'team': driver_quali['TeamName'].iloc[0] if not driver_quali.empty else None,
            'quali_position': int(driver_quali['Position'].iloc[0]) if not driver_quali.empty and pd.notna(driver_quali['Position'].iloc[0]) else None,
            'grid_position': int(driver_race['GridPosition'].iloc[0]) if not driver_race.empty and pd.notna(driver_race['GridPosition'].iloc[0]) else None,
            'finish_position': int(driver_race['Position'].iloc[0]) if not driver_race.empty and pd.notna(driver_race['Position'].iloc[0]) else None,
            'positions_gained': None,
            'points': float(driver_race['Points'].iloc[0]) if not driver_race.empty and pd.notna(driver_race['Points'].iloc[0]) else 0,
            'status': driver_race['Status'].iloc[0] if not driver_race.empty else None
        }
        
        # Calculate positions gained
        if summary['grid_position'] is not None and summary['finish_position'] is not None:
            summary['positions_gained'] = summary['grid_position'] - summary['finish_position']
        
        return summary
    
    def get_positions_gained_ranking(self) -> pd.DataFrame:
        """
        Get ranking of drivers by positions gained in the race.
        
        Returns:
            DataFrame sorted by positions gained (descending)
        """
        race = self.get_race_results()
        
        if race.empty:
            return pd.DataFrame()
        
        # Calculate positions gained
        race['PositionsGained'] = race.apply(
            lambda row: row['GridPosition'] - row['Position'] 
            if pd.notna(row['GridPosition']) and pd.notna(row['Position']) 
            else None, 
            axis=1
        )
        
        # Filter only drivers with valid position data
        valid_data = race[pd.notna(race['Position']) & pd.notna(race['GridPosition'])].copy()
        
        if valid_data.empty:
            return pd.DataFrame()
        
        # Sort by positions gained
        ranked = valid_data.sort_values('PositionsGained', ascending=False)
        
        return ranked[['DriverNumber', 'Abbreviation', 'FullName', 'TeamName', 
                      'GridPosition', 'Position', 'PositionsGained']].reset_index(drop=True)
    
    def get_wdc_standings_after_race(self) -> pd.DataFrame:
        """
        Get WDC standings after this race.
        
        Returns:
            DataFrame with driver championship standings
        """
        try:
            # Get all races up to and including this round
            standings_data = []
            
            for round_num in range(1, self.round_number + 1):
                try:
                    event = f1.get_event(self.year, round_num)
                    race_session = event.get_race()
                    # Load minimal data - just need results
                    race_session.load(laps=False, telemetry=False, weather=False, messages=False)
                    
                    # Get results with driver info and points
                    results = race_session.results
                    race_results = results[['Abbreviation', 'FullName', 'TeamName', 'Points']].copy()
                    
                    # Only include rows with valid data
                    race_results = race_results[pd.notna(race_results['Abbreviation']) & 
                                               pd.notna(race_results['Points'])].copy()
                    
                    if not race_results.empty:
                        standings_data.append(race_results)
                except Exception as e:
                    print(f"Warning: Could not load round {round_num}: {e}")
                    continue
            
            if not standings_data:
                return pd.DataFrame()
            
            # Combine all race results
            all_results = pd.concat(standings_data, ignore_index=True)
            
            # Group by driver and sum points
            wdc_standings = all_results.groupby(['Abbreviation'], as_index=False).agg({
                'FullName': 'first',
                'TeamName': 'last',  # Use last team (in case of mid-season transfers)
                'Points': 'sum'
            })
            
            wdc_standings = wdc_standings.sort_values('Points', ascending=False).reset_index(drop=True)
            wdc_standings.insert(0, 'Position', range(1, len(wdc_standings) + 1))
            
            return wdc_standings
            
        except Exception as e:
            print(f"Error calculating WDC standings: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_wcc_standings_after_race(self) -> pd.DataFrame:
        """
        Get WCC standings after this race.
        
        Returns:
            DataFrame with constructor championship standings
        """
        try:
            standings_data = []
            
            for round_num in range(1, self.round_number + 1):
                try:
                    event = f1.get_event(self.year, round_num)
                    race_session = event.get_race()
                    # Load minimal data - just need results
                    race_session.load(laps=False, telemetry=False, weather=False, messages=False)
                    
                    race_results = race_session.results[['TeamName', 'Points']].copy()
                    
                    # Only include rows with valid data
                    race_results = race_results[pd.notna(race_results['TeamName']) & 
                                               pd.notna(race_results['Points'])].copy()
                    
                    if not race_results.empty:
                        standings_data.append(race_results)
                except Exception as e:
                    print(f"Warning: Could not load round {round_num}: {e}")
                    continue
            
            if not standings_data:
                return pd.DataFrame()
            
            # Combine all race results
            all_results = pd.concat(standings_data, ignore_index=True)
            
            # Group by team and sum points
            wcc_standings = all_results.groupby('TeamName', as_index=False)['Points'].sum()
            wcc_standings = wcc_standings.sort_values('Points', ascending=False).reset_index(drop=True)
            wcc_standings.insert(0, 'Position', range(1, len(wcc_standings) + 1))
            
            return wcc_standings
            
        except Exception as e:
            print(f"Error calculating WCC standings: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()


class TeammateBattleFetcher:
    """Class for teammate and team comparison analysis"""
    
    def __init__(self, year: int, round_number: int):
        """
        Initialize the teammate battle fetcher.
        
        Args:
            year: Season year
            round_number: Round number in the season
        """
        self.year = year
        self.round_number = round_number
        self.fetcher = F1DataFetcher(year, round_number)
    
    def get_teammate_quali_comparison(self) -> pd.DataFrame:
        """
        Compare teammates in qualifying.
        
        Returns:
            DataFrame with teammate qualifying comparisons
        """
        quali = self.fetcher.get_qualifying_results()
        
        if quali.empty:
            return pd.DataFrame()
        
        # Group by team
        teams = quali.groupby('TeamName')
        
        comparisons = []
        
        for team_name, team_data in teams:
            if len(team_data) == 2:
                drivers = team_data.sort_values('Position')
                driver1 = drivers.iloc[0]
                driver2 = drivers.iloc[1]
                
                # Calculate quali delta if both have Q3 times, else Q2, else Q1
                delta = None
                for q_session in ['Q3', 'Q2', 'Q1']:
                    if pd.notna(driver1[q_session]) and pd.notna(driver2[q_session]):
                        delta = abs((driver2[q_session] - driver1[q_session]).total_seconds())
                        break
                
                comparisons.append({
                    'Team': team_name,
                    'QuickestDriver': driver1['Abbreviation'],
                    'QuickestPosition': int(driver1['Position']),
                    'SlowerDriver': driver2['Abbreviation'],
                    'SlowerPosition': int(driver2['Position']),
                    'QualifyingDelta_seconds': delta
                })
        
        return pd.DataFrame(comparisons)
    
    def get_teammate_race_comparison(self) -> pd.DataFrame:
        """
        Compare teammates in the race.
        
        Returns:
            DataFrame with teammate race comparisons
        """
        race = self.fetcher.get_race_results()
        
        if race.empty:
            return pd.DataFrame()
        
        # Calculate positions gained
        race['PositionsGained'] = race.apply(
            lambda row: row['GridPosition'] - row['Position'] 
            if pd.notna(row['GridPosition']) and pd.notna(row['Position']) 
            else None, 
            axis=1
        )
        
        # Group by team
        teams = race.groupby('TeamName')
        
        comparisons = []
        
        for team_name, team_data in teams:
            if len(team_data) == 2:
                driver1 = team_data.iloc[0]
                driver2 = team_data.iloc[1]
                
                # Determine who finished ahead based on finishing position
                # Lower position number = better finish
                d1_pos = driver1['Position'] if pd.notna(driver1['Position']) else float('inf')
                d2_pos = driver2['Position'] if pd.notna(driver2['Position']) else float('inf')
                
                if d1_pos < d2_pos:
                    ahead_driver = driver1
                    behind_driver = driver2
                elif d2_pos < d1_pos:
                    ahead_driver = driver2
                    behind_driver = driver1
                else:
                    # Both DNF or same position (shouldn't happen), use driver1 as ahead
                    ahead_driver = driver1
                    behind_driver = driver2
                
                comparisons.append({
                    'Team': team_name,
                    'AheadDriver': ahead_driver['Abbreviation'],
                    'AheadPosition': int(ahead_driver['Position']) if pd.notna(ahead_driver['Position']) else None,
                    'AheadPositionsGained': ahead_driver['PositionsGained'] if pd.notna(ahead_driver['PositionsGained']) else None,
                    'BehindDriver': behind_driver['Abbreviation'],
                    'BehindPosition': int(behind_driver['Position']) if pd.notna(behind_driver['Position']) else None,
                    'BehindPositionsGained': behind_driver['PositionsGained'] if pd.notna(behind_driver['PositionsGained']) else None
                })
        
        return pd.DataFrame(comparisons)
    
    def get_team_weekend_summary(self, team_name: str) -> Dict:
        """
        Get complete weekend summary for a specific team.
        
        Args:
            team_name: Team name (e.g., 'Red Bull Racing')
            
        Returns:
            Dictionary with team weekend performance
        """
        quali = self.fetcher.get_qualifying_results()
        race = self.fetcher.get_race_results()
        
        team_quali = quali[quali['TeamName'] == team_name]
        team_race = race[race['TeamName'] == team_name]
        
        if team_quali.empty or team_race.empty:
            return {}
        
        drivers = team_quali['Abbreviation'].tolist()
        
        summary = {
            'team': team_name,
            'drivers': drivers,
            'best_quali_position': int(team_quali['Position'].min()),
            'worst_quali_position': int(team_quali['Position'].max()),
            'best_race_finish': int(team_race['Position'].min()) if team_race['Position'].notna().any() else None,
            'worst_race_finish': int(team_race['Position'].max()) if team_race['Position'].notna().any() else None,
            'total_points': float(team_race['Points'].sum()),
            'both_finished': all(team_race['Status'] == 'Finished')
        }
        
        return summary