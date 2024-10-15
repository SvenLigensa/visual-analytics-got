import json
import pandas as pd

# Load the JSON data
with open("../raw/episodes.json") as file:
    data = json.load(file)

# Initialize the list to store the data
data_list = []

# Iterate over each episode
for episode in data["episodes"]:
    episode_title = episode["episodeTitle"]
    
    # Iterate over each scene in the episode
    for scene in episode["scenes"]:
        location = scene["location"]
        sub_location = scene["subLocation"] if "subLocation" in scene else scene["location"]
        
        # Calculate the scene duration in seconds
        start_time_parts = [int(t) for t in scene["sceneStart"].split(":")]
        end_time_parts = [int(t) for t in scene["sceneEnd"].split(":")]
        
        start_seconds = start_time_parts[0] * 3600 + start_time_parts[1] * 60 + start_time_parts[2]
        end_seconds = end_time_parts[0] * 3600 + end_time_parts[1] * 60 + end_time_parts[2]
        duration = end_seconds - start_seconds
        
        # Iterate over each character in the scene
        for character in scene["characters"]:
            # Append the data for each character
            data_list.append({
                "name": character["name"],
                "episode_title": episode_title,
                "location": location,
                "sub_location": sub_location,
                "time": duration
            })

# Create the pandas DataFrame
df = pd.DataFrame(data_list)

# Ensure the columns are in the specified order
df = df[["name", "episode_title", "location", "sub_location", "time"]]

# Export the DataFrame to a CSV file
df.to_csv("time_location.csv", index=False)

# Print the DataFrame to verify the output
print(df)