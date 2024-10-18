#process_characters_episodes_time

import pandas as pd

# Load the CSV file
df = pd.read_csv('data/processed/time_location.csv') 

# Select only the relevant columns
df_selected = df[['name', 'episode', 'time']]

# Group by 'name' and 'episode', and aggregate the time 
# You can choose an aggregation method (e.g., sum, mean, first, etc.)
df_grouped = df_selected.groupby(['name', 'episode'], as_index=False).sum()


df_grouped.to_csv('data\processed\characters_time.csv', index=False)