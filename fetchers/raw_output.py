import fastf1 as f1
import os
import sys

# Create a Cache directory
CACHE_DIR = "./fastf1cache"
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

f1.Cache.enable_cache(CACHE_DIR)

year = 2024
round_number = 20

event = f1.get_event(year, round_number)

session = event.get_race()
session.load()

results_df = session.results
output_file = "test.csv"

results_df.to_csv(output_file, index=False)