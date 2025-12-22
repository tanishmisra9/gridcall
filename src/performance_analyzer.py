"""
Performance analyzer for F1 race weekends.
Generates comprehensive performance rankings for drivers and teams.
"""

import sys
import os
import pandas as pd
import logging
from datetime import datetime
from data_fetcher import F1DataFetcher, TeammateBattleFetcher

# Suppress FastF1 logging
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

if not DEBUG:
    logging.getLogger('fastf1').setLevel(logging.ERROR)
    logging.getLogger('fastf1.core').setLevel(logging.ERROR)
    logging.getLogger('fastf1.api').setLevel(logging.ERROR)
    logging.getLogger('fastf1.req').setLevel(logging.ERROR)
    logging.getLogger('fastf1.logger').setLevel(logging.ERROR)


def analyze_weekend_performance(year: int, round_number: int):
    """
    Analyze and rank driver and team performance across a race weekend.
    
    Args:
        year: Season year
        round_number: Round number
    """
    
    print(f"Gridcall performance analysis")
    print(f"Year: {year} | Round: {round_number}")
    
    # Initialize fetchers
    data_fetcher = F1DataFetcher(year, round_number)
    teammate_fetcher = TeammateBattleFetcher(year, round_number)
    
    location = data_fetcher.location
    print(f"Location: {location}\n")
    
    # Create output directory
    output_dir = "Analysis"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    # Generate filename
    location_clean = location.lower().replace(' ', '_').replace('-', '')
    output_file = os.path.join(output_dir, f'{year}_r{round_number}_{location_clean}_analysis.txt')
    
    # Fetch data
    print("Fetching race data...")
    quali_results = data_fetcher.get_qualifying_results()
    race_results = data_fetcher.get_race_results()
    teammate_quali = teammate_fetcher.get_teammate_quali_comparison()
    teammate_race = teammate_fetcher.get_teammate_race_comparison()
    
    print("Calculating championship standings...")
    wdc_standings = data_fetcher.get_wdc_standings_after_race()
    wcc_standings = data_fetcher.get_wcc_standings_after_race()
    
    # Generate output
    generate_text_report(output_file, year, round_number, location,
                       quali_results, race_results,
                       teammate_quali, teammate_race,
                       wdc_standings, wcc_standings)
    
    print(f"\nAnalysis complete! Output saved to: {output_file}\n")


def generate_text_report(filename, year, round_number, location,
                         quali, race,
                         teammate_quali, teammate_race,
                         wdc, wcc):
    """Generate a formatted text report"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write("="*80 + "\n")
        f.write(f"F1 WEEKEND PERFORMANCE ANALYSIS\n")
        f.write(f"Year: {year} | Round: {round_number} | Location: {location}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        # Qualifying Results
        f.write("QUALIFYING RESULTS\n")
        f.write("-"*80 + "\n")
        f.write(f"{'Pos':<5} {'Driver':<20} {'Team':<30} {'Q1':<12} {'Q2':<12} {'Q3':<12}\n")
        f.write("-"*80 + "\n")
        
        for idx, row in quali.iterrows():
            pos = int(row['Position']) if pd.notna(row['Position']) else '--'
            q1 = format_time(row['Q1']) if pd.notna(row['Q1']) else '--'
            q2 = format_time(row['Q2']) if pd.notna(row['Q2']) else '--'
            q3 = format_time(row['Q3']) if pd.notna(row['Q3']) else '--'
            
            f.write(f"{pos:<5} {row['Abbreviation']:<20} {row['TeamName']:<30} {q1:<12} {q2:<12} {q3:<12}\n")
        
        # Race Results
        f.write("\n\nRACE RESULTS\n")
        f.write("-"*80 + "\n")
        f.write(f"{'Pos':<5} {'Driver':<20} {'Team':<30} {'Grid':<6} {'Status':<15} {'Pts':<5}\n")
        f.write("-"*80 + "\n")
        
        for idx, row in race.iterrows():
            pos = int(row['Position']) if pd.notna(row['Position']) else '--'
            grid = int(row['GridPosition']) if pd.notna(row['GridPosition']) else '--'
            pts = int(row['Points']) if pd.notna(row['Points']) else 0
            status = row['Status'] if pd.notna(row['Status']) else 'Unknown'
            
            f.write(f"{pos:<5} {row['Abbreviation']:<20} {row['TeamName']:<30} {grid:<6} {status:<15} {pts:<5}\n")
        
        # Teammate Qualifying Battle
        f.write("\n\nTEAMMATE QUALIFYING BATTLE\n")
        f.write("-"*80 + "\n")
        f.write(f"{'Team':<30} {'Ahead':<10} {'Pos':<5} {'Behind':<10} {'Pos':<5} {'Delta (s)':<12}\n")
        f.write("-"*80 + "\n")
        
        for idx, row in teammate_quali.iterrows():
            delta = f"{row['QualifyingDelta_seconds']:.3f}" if pd.notna(row['QualifyingDelta_seconds']) else '--'
            f.write(f"{row['Team']:<30} {row['QuickestDriver']:<10} {int(row['QuickestPosition']):<5} {row['SlowerDriver']:<10} {int(row['SlowerPosition']):<5} {delta:<12}\n")
        
        # Teammate Race Battle
        f.write("\n\nTEAMMATE RACE BATTLE\n")
        f.write("-"*80 + "\n")
        
        if not teammate_race.empty:
            f.write(f"{'Team':<30} {'Ahead':<10} {'Pos':<5} {'+/-':<5} {'Behind':<10} {'Pos':<5} {'+/-':<5}\n")
            f.write("-"*80 + "\n")
            
            for idx, row in teammate_race.iterrows():
                ahead_pos = int(row['AheadPosition']) if pd.notna(row['AheadPosition']) else '--'
                behind_pos = int(row['BehindPosition']) if pd.notna(row['BehindPosition']) else '--'
                ahead_gained = int(row['AheadPositionsGained']) if pd.notna(row['AheadPositionsGained']) else '--'
                behind_gained = int(row['BehindPositionsGained']) if pd.notna(row['BehindPositionsGained']) else '--'
                
                ahead_sign = '+' if isinstance(ahead_gained, int) and ahead_gained > 0 else ''
                behind_sign = '+' if isinstance(behind_gained, int) and behind_gained > 0 else ''
                
                ahead_str = f"{ahead_sign}{ahead_gained}" if ahead_gained != '--' else '--'
                behind_str = f"{behind_sign}{behind_gained}" if behind_gained != '--' else '--'
                
                f.write(f"{row['Team']:<30} {row['AheadDriver']:<10} {ahead_pos:<5} {ahead_str:<5} {row['BehindDriver']:<10} {behind_pos:<5} {behind_str:<5}\n")
        else:
            f.write("No race data available.\n")
        
        # WDC Standings
        if not wdc.empty:
            f.write("\n\nWORLD DRIVERS' CHAMPIONSHIP STANDINGS (After Round " + str(round_number) + ")\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Pos':<5} {'Driver':<25} {'Team':<30} {'Points':<10}\n")
            f.write("-"*80 + "\n")
            
            for idx, row in wdc.head(10).iterrows():
                f.write(f"{int(row['Position']):<5} {row['Abbreviation']:<25} {row['TeamName']:<30} {int(row['Points']):<10}\n")
        
        # WCC Standings
        if not wcc.empty:
            f.write("\n\nWORLD CONSTRUCTORS' CHAMPIONSHIP STANDINGS (After Round " + str(round_number) + ")\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Pos':<5} {'Team':<50} {'Points':<10}\n")
            f.write("-"*80 + "\n")
            
            for idx, row in wcc.iterrows():
                f.write(f"{int(row['Position']):<5} {row['TeamName']:<50} {int(row['Points']):<10}\n")
        
        # Weekend Performance Analysis
        f.write("\n\nWEEKEND PERFORMANCE ANALYSIS\n")
        f.write("="*80 + "\n")
        
        # Calculate performance scores for each driver
        performance_scores = calculate_weekend_performance(
            race, quali, wcc, teammate_race, teammate_quali
        )
        
        if not performance_scores.empty:
            # Overall Performance Ranking
            f.write("\nOVERALL WEEKEND PERFORMANCE RANKING\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Rank':<6} {'Driver':<12} {'Team':<25} {'Score':<8} {'Breakdown':<30}\n")
            f.write("-"*80 + "\n")
            
            for idx, row in performance_scores.iterrows():
                breakdown = f"Q:{row['QualiScore']:.1f} R:{row['RaceScore']:.1f} P:{row['PositionsScore']:.1f} TM:{row['TeammateScore']:.1f}"
                f.write(f"{idx+1:<6} {row['Driver']:<12} {row['Team']:<25} {row['TotalScore']:.2f}  {breakdown:<30}\n")
            
            # Breakout and Bust Analysis
            breakout_drivers, bust_drivers = identify_breakout_bust(performance_scores)
            
            f.write("\n\nBREAKOUT DRIVERS (Top 5 Positive Surprises)\n")
            f.write("-"*80 + "\n")
            if breakout_drivers:
                for i, driver_info in enumerate(breakout_drivers[:5], 1):
                    f.write(f"{i}. {driver_info['Driver']} ({driver_info['Team']}) - Score: {driver_info['TotalScore']:.2f}\n")
            else:
                f.write("No clear breakout performances identified.\n")
            
            f.write("\n\nBUST DRIVERS (Top 5 Disappointing Performances)\n")
            f.write("-"*80 + "\n")
            if bust_drivers:
                for i, driver_info in enumerate(bust_drivers[:5], 1):
                    f.write(f"{i}. {driver_info['Driver']} ({driver_info['Team']}) - Score: {driver_info['TotalScore']:.2f}\n")
            else:
                f.write("No clear bust performances identified.\n")


def format_time(time_delta):
    """Format timedelta to readable string"""
    if pd.notna(time_delta):
        total_seconds = time_delta.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        if minutes > 0:
            return f"{minutes}:{seconds:06.3f}"
        else:
            return f"{seconds:.3f}s"
    return '--'


def calculate_weekend_performance(race_df, quali_df, wcc_df, teammate_race_df, teammate_quali_df):
    """
    Calculate comprehensive weekend performance scores for each driver.
    
    Scoring factors:
    - Qualifying performance relative to team competitiveness
    - Race finish relative to team competitiveness  
    - Positions gained in race
    - Performance vs teammate
    """
    if race_df.empty or quali_df.empty or wcc_df.empty:
        return pd.DataFrame()
    
    # Create team competitiveness lookup (lower position = more competitive)
    team_competitiveness = {}
    for idx, row in wcc_df.iterrows():
        team_competitiveness[row['TeamName']] = int(row['Position'])
    
    performance_data = []
    
    for idx, race_row in race_df.iterrows():
        driver = race_row['Abbreviation']
        team = race_row['TeamName']
        
        # Skip if no valid finish position
        if pd.isna(race_row['Position']):
            continue
        
        finish_pos = int(race_row['Position'])
        grid_pos = race_row['GridPosition']
        
        # Get team competitiveness (1 = best team, 10 = worst team)
        team_comp = team_competitiveness.get(team, 5)
        
        # Find driver in quali results
        quali_row = quali_df[quali_df['Abbreviation'] == driver]
        quali_pos = int(quali_row['Position'].iloc[0]) if not quali_row.empty and pd.notna(quali_row['Position'].iloc[0]) else None
        
        # Calculate scores
        scores = {
            'Driver': driver,
            'Team': team,
            'TeamCompetitiveness': team_comp,
            'QualiScore': 0.0,
            'RaceScore': 0.0,
            'PositionsScore': 0.0,
            'TeammateScore': 0.0,
            'TotalScore': 0.0
        }
        
        # 1. QUALIFYING SCORE: Non-linear to emphasize Q3 (P1-P10)
        if quali_pos is not None:
            # Non-linear base score - Q3 positions get premium
            if quali_pos <= 10:
                # P1-P10: Exponential decay from 45 to 20
                base_quali_score = 45 - (quali_pos - 1) * 2.5
            else:
                # P11-P20: Linear taper from 18 to 2
                base_quali_score = 20 - (quali_pos - 10) * 1.8
            
            # Small bonus/penalty based on team expectations
            expected_quali = team_comp * 2
            quali_delta = expected_quali - quali_pos
            # Team multiplier: 1.0x to 1.6x
            team_multiplier = 1.0 + (team_comp - 1) * 0.0667
            expectation_bonus = quali_delta * 1.0 * team_multiplier
            
            scores['QualiScore'] = base_quali_score + expectation_bonus
        
        # 2. RACE FINISH SCORE: Similar to quali - absolute position matters most
        # Base score for finishing position (linear)
        base_race_score = (21 - finish_pos) * 2.5
        
        # Small bonus/penalty based on team expectations
        expected_race = team_comp * 2
        race_delta = expected_race - finish_pos
        team_multiplier = 1.0 + (team_comp - 1) * 0.0667
        expectation_bonus = race_delta * 1.0 * team_multiplier
        
        scores['RaceScore'] = base_race_score + expectation_bonus
        
        # 3. POSITIONS GAINED: Significant bonus for overtaking
        if pd.notna(grid_pos):
            positions_gained = grid_pos - finish_pos
            # Reward gains, penalize losses
            if positions_gained > 0:
                scores['PositionsScore'] = positions_gained * 3.5
            else:
                scores['PositionsScore'] = positions_gained * 2.5
        
        # 4. TEAMMATE BATTLES
        # Quali comparison
        tm_quali = teammate_quali_df[
            (teammate_quali_df['QuickestDriver'] == driver) | 
            (teammate_quali_df['SlowerDriver'] == driver)
        ]
        if not tm_quali.empty:
            tm_row = tm_quali.iloc[0]
            if tm_row['QuickestDriver'] == driver:
                scores['TeammateScore'] += 3.0
            else:
                scores['TeammateScore'] -= 3.0
        
        # Race comparison
        tm_race = teammate_race_df[
            (teammate_race_df['AheadDriver'] == driver) | 
            (teammate_race_df['BehindDriver'] == driver)
        ]
        if not tm_race.empty:
            tm_row = tm_race.iloc[0]
            if tm_row['AheadDriver'] == driver:
                scores['TeammateScore'] += 5.0
                # Bonus for positions gained difference
                if pd.notna(tm_row['AheadPositionsGained']) and pd.notna(tm_row['BehindPositionsGained']):
                    gained_diff = tm_row['AheadPositionsGained'] - tm_row['BehindPositionsGained']
                    scores['TeammateScore'] += gained_diff * 1.0
            else:
                scores['TeammateScore'] -= 5.0
        
        # Calculate total score
        scores['TotalScore'] = (scores['QualiScore'] + scores['RaceScore'] + 
                               scores['PositionsScore'] + scores['TeammateScore'])
        
        performance_data.append(scores)
    
    # Create DataFrame and sort by total score
    performance_df = pd.DataFrame(performance_data)
    performance_df = performance_df.sort_values('TotalScore', ascending=False).reset_index(drop=True)
    
    return performance_df


def identify_breakout_bust(performance_df):
    """
    Identify breakout and bust drivers.
    Always returns top 5 and bottom 5 drivers by score.
    """
    if performance_df.empty or len(performance_df) < 10:
        return [], []
    
    # Sort by score (already sorted but just to be sure)
    sorted_df = performance_df.sort_values('TotalScore', ascending=False).reset_index(drop=True)
    
    # Top 5 = Breakout
    breakout_drivers = []
    for idx in range(min(5, len(sorted_df))):
        row = sorted_df.iloc[idx]
        breakout_drivers.append({
            'Driver': row['Driver'],
            'Team': row['Team'],
            'TotalScore': row['TotalScore']
        })
    
    # Bottom 5 = Bust
    bust_drivers = []
    for idx in range(max(0, len(sorted_df) - 5), len(sorted_df)):
        row = sorted_df.iloc[idx]
        bust_drivers.append({
            'Driver': row['Driver'],
            'Team': row['Team'],
            'TotalScore': row['TotalScore']
        })
    
    # Reverse bust list so worst is first
    bust_drivers.reverse()
    
    return breakout_drivers, bust_drivers


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 performance_analyzer.py <year> <round>")
        sys.exit(1)
    
    year = int(sys.argv[1])
    round_number = int(sys.argv[2])
    
    try:
        analyze_weekend_performance(year, round_number)
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)