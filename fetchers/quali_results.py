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
    print("  python3 quali_results.py <year> <round> [s|m]   - Get specific qualifying")
    print("  python3 quali_results.py <year>                  - Get all qualifyings for the year")
    print("\nFlags:")
    print("  s - Sprint qualifying")
    print("  m - Main qualifying (default)")
    sys.exit(1)

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
    'Q1',
    'Q2',
    'Q3'
]

def process_qualifying(year, round_number, quali_type='main', main_quali_dir=".", sprint_quali_dir="."):
    """Process a qualifying session and save to a CSV file"""
    try:
        event = f1.get_event(year, round_number)
        location = event['Location'].lower().replace(' ', '').replace('-', '')
        
        # Determine which session to load and which directory to use
        if quali_type == 'sprint':
            # Try sprint qualifying first, then sprint shootout (newer format)
            try:
                session = event.get_sprint_qualifying()
                session_name = "Sprint Qualifying"
            except:
                try:
                    session = event.get_sprint_shootout()
                    session_name = "Sprint Shootout"
                except:
                    print(f"No sprint qualifying found for Round {round_number}")
                    return
            output_dir = sprint_quali_dir
            output_file = os.path.join(output_dir, f'{year}{location}_sprint_quali.csv')
        else:
            session = event.get_qualifying()
            session_name = "Qualifying"
            output_dir = main_quali_dir
            output_file = os.path.join(output_dir, f'{year}{location}_quali.csv')
        
        print(f"Loading {session_name} data for {year}, Round {round_number}...")
        session.load()
        
        # Keep only specified columns
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

# Create Qualifying directory inside data/year/
quali_dir = os.path.join(year_dir, "Qualifying")
if not os.path.exists(quali_dir):
    os.mkdir(quali_dir)

# Create Sprint Qualifying directory inside data/year/Qualifying/
sprint_quali_dir = os.path.join(quali_dir, "Sprint Qualifying")
if not os.path.exists(sprint_quali_dir):
    os.mkdir(sprint_quali_dir)

# If only year is provided, process all rounds
if len(sys.argv) == 2:
    print(f"Fetching all qualifying sessions for {year}...\n")
    schedule = f1.get_event_schedule(year)
    
    for index, event_row in schedule.iterrows():
        round_number = event_row['RoundNumber']
        event_format = event_row['EventFormat']
        
        # Always process main qualifying
        process_qualifying(year, round_number, 'main', main_quali_dir=quali_dir, sprint_quali_dir=sprint_quali_dir)
        
        # If it's a sprint event, also process sprint qualifying
        if 'sprint' in str(event_format).lower():
            process_qualifying(year, round_number, 'sprint', main_quali_dir=quali_dir, sprint_quali_dir=sprint_quali_dir)
    
    print(f"\nCompleted processing all qualifying sessions for {year}")
    print(f"Main qualifying files saved in '{quali_dir}/' directory")
    print(f"Sprint qualifying files saved in '{sprint_quali_dir}/' directory")

# If year and round are provided, process that specific qualifying
else:
    round_number = int(sys.argv[2])
    
    # Check for qualifying type flag
    quali_type = 'main'  # default
    if len(sys.argv) == 4:
        flag = sys.argv[3].lower()
        if flag == 's':
            quali_type = 'sprint'
        elif flag == 'm':
            quali_type = 'main'
        else:
            print(f"Unknown flag '{flag}'. Use 's' for sprint or 'm' for main.")
            sys.exit(1)
    
    process_qualifying(year, round_number, quali_type, main_quali_dir=quali_dir, sprint_quali_dir=sprint_quali_dir)
    
    if quali_type == 'sprint':
        print(f"File saved in '{sprint_quali_dir}/' directory")
    else:
        print(f"File saved in '{quali_dir}/' directory")