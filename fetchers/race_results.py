import fastf1 as f1
import os
import sys

# Create a Cache directory
CACHE_DIR = "./fastf1cache"
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

f1.Cache.enable_cache(CACHE_DIR)

# Check if arguments are provided
if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("Usage:")
    print("  python3 race_results.py <year> <round> [s|m]   - Get specific race")
    print("  python3 race_results.py <year> [s|m]           - Get all races for the year")
    print("  python3 race_results.py <year>                  - Get all races (main + sprint)")
    print("\nFlags:")
    print("  s - Sprint race(s)")
    print("  m - Main race(s)")
    print("\nExamples:")
    print("  python3 race_results.py 2025 2 s    - Get sprint race for round 2")
    print("  python3 race_results.py 2025 2      - Get main race for round 2")
    print("  python3 race_results.py 2025 s      - Get all sprint races for 2025")
    print("  python3 race_results.py 2025 m      - Get all main races for 2025")
    print("  python3 race_results.py 2025        - Get all races for 2025")
    sys.exit(1)

# Get year and round from command line arguments
year = int(sys.argv[1])

# Get results and keep only specified columns
columns_to_keep = [
    'DriverNumber',
    'Abbreviation',
    'TeamName',
    'FullName',
    'Position',
    'ClassifiedPosition',
    'GridPosition',
    'Time',
    'Status',
    'Points'
]

def process_round(year, round_number, race_type='main', main_dir=".", sprint_dir="."):
    """Process a single round and save to a CSV file"""
    try:
        event = f1.get_event(year, round_number)
        location = event['Location'].lower().replace(' ', '').replace('-', '')
        
        # Determine which session to load and which directory to use
        if race_type == 'sprint':
            try:
                session = event.get_sprint()
                session_name = "Sprint Race"
                output_dir = sprint_dir
                output_file = os.path.join(output_dir, f'{year}{location}_sprint.csv')
            except:
                print(f"No sprint race found for Round {round_number}")
                return
        else:
            session = event.get_race()
            session_name = "Race"
            output_dir = main_dir
            output_file = os.path.join(output_dir, f'{year}{location}.csv')
        
        print(f"Loading {session_name} data for {year}, Round {round_number}...")
        session.load()
        
        results_df = session.results[columns_to_keep]
        
        # Save to CSV
        results_df.to_csv(output_file, index=False)
        
        print(f"Saved to {output_file}")
        
    except Exception as e:
        print(f"There was an error: {e}")

# Create data directory if it doesn't exist
data_dir = "data"
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# Create year directory inside data/
year_dir = os.path.join(data_dir, str(year))
if not os.path.exists(year_dir):
    os.mkdir(year_dir)

# Create Sprint directory inside data/year/
sprint_dir = os.path.join(year_dir, "Sprint")
if not os.path.exists(sprint_dir):
    os.mkdir(sprint_dir)

# Determine if processing all rounds or specific round
if len(sys.argv) == 2:
    # python3 race_results.py 2025 - Get all races (main + sprint)
    print(f"Fetching all rounds for {year}...\n")
    schedule = f1.get_event_schedule(year)
    
    for index, event in schedule.iterrows():
        round_number = event['RoundNumber']
        event_format = event['EventFormat']
        
        # Always process main race
        process_round(year, round_number, 'main', main_dir=year_dir, sprint_dir=sprint_dir)
        
        # If it's a sprint event, also process sprint race
        if 'sprint' in str(event_format).lower():
            process_round(year, round_number, 'sprint', main_dir=year_dir, sprint_dir=sprint_dir)
    
    print(f"\nCompleted processing all rounds for {year}")
    print(f"Main race files saved in '{year_dir}/' directory")
    print(f"Sprint race files saved in '{sprint_dir}/' directory")

elif len(sys.argv) == 3:
    # Could be: python3 race_results.py 2025 5 OR python3 race_results.py 2025 s
    try:
        # Try to parse as round number
        round_number = int(sys.argv[2])
        # It's a specific round, default to main race
        process_round(year, round_number, 'main', main_dir=year_dir, sprint_dir=sprint_dir)
        print(f"File saved in '{year_dir}/' directory")
    except ValueError:
        # It's a flag for all races of that type
        flag = sys.argv[2].lower()
        if flag == 's':
            # Get all sprint races
            print(f"Fetching all sprint races for {year}...\n")
            schedule = f1.get_event_schedule(year)
            
            for index, event in schedule.iterrows():
                round_number = event['RoundNumber']
                event_format = event['EventFormat']
                
                if 'sprint' in str(event_format).lower():
                    process_round(year, round_number, 'sprint', main_dir=year_dir, sprint_dir=sprint_dir)
            
            print(f"\nCompleted processing all sprint races for {year}")
            print(f"Sprint race files saved in '{sprint_dir}/' directory")
            
        elif flag == 'm':
            # Get all main races
            print(f"Fetching all main races for {year}...\n")
            schedule = f1.get_event_schedule(year)
            
            for index, event in schedule.iterrows():
                round_number = event['RoundNumber']
                process_round(year, round_number, 'main', main_dir=year_dir, sprint_dir=sprint_dir)
            
            print(f"\nCompleted processing all main races for {year}")
            print(f"Main race files saved in '{year_dir}/' directory")
        else:
            print(f"Unknown flag '{flag}'. Use 's' for sprint or 'm' for main.")
            sys.exit(1)

else:
    # python3 race_results.py 2025 5 s - specific round with flag
    round_number = int(sys.argv[2])
    flag = sys.argv[3].lower()
    
    if flag == 's':
        race_type = 'sprint'
    elif flag == 'm':
        race_type = 'main'
    else:
        print(f"Unknown flag '{flag}'. Use 's' for sprint or 'm' for main.")
        sys.exit(1)
    
    process_round(year, round_number, race_type, main_dir=year_dir, sprint_dir=sprint_dir)
    
    if race_type == 'sprint':
        print(f"File saved in '{sprint_dir}/' directory")
    else:
        print(f"File saved in '{year_dir}/' directory")