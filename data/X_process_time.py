import pandas as pd

# Load the existing CSV file (replace 'existing_file.csv' with the actual file path)
df = pd.read_csv('processed/characters_time.csv') 

# Pivot the data so that the 'name' becomes the index, and 'episode' becomes columns
# Assuming your existing file has columns: 'name', 'episode', and 'time'
df_pivot = df.pivot(index='name', columns='episode', values='time')

# Sort the columns based on episode string order (e.g., S01E01, S01E02, ...)
df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)

df_pivot.fillna(0, inplace=True)

# Save the resulting DataFrame to a CSV file called 'time.csv'
df_pivot.to_csv('processed/time.csv')
