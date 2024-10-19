import pandas as pd

df = pd.read_csv('processed/time_location.csv') 

# Select only the relevant columns
df_selected = df[['name', 'episode', 'time']]

df_grouped = df_selected.groupby(['name', 'episode'], as_index=False).sum()

df_grouped.to_csv('processed/characters_time.csv', index=False)
