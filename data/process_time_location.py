import json
import pandas as pd

with open("raw/episodes.json") as file:
    data = json.load(file)

data_list = []

for episode in data["episodes"]:
    episode_title = episode["episodeTitle"]

    for scene in episode["scenes"]:
        location = scene["location"]
        sub_location = scene["subLocation"] if "subLocation" in scene else scene["location"]

        start_time_parts = [int(t) for t in scene["sceneStart"].split(":")]
        end_time_parts = [int(t) for t in scene["sceneEnd"].split(":")]
        start_seconds = start_time_parts[0] * 3600 + start_time_parts[1] * 60 + start_time_parts[2]
        end_seconds = end_time_parts[0] * 3600 + end_time_parts[1] * 60 + end_time_parts[2]
        duration = end_seconds - start_seconds

        for character in scene["characters"]:
            data_list.append({
                "name": character["name"],
                "episode": episode_title,
                "location": location,
                "sub_location": sub_location,
                "time": duration
            })

df = pd.DataFrame(data_list)

# Use episode identifiers instead of titles
episodes = pd.read_csv("processed/episodes.csv")
episode_titles = episodes["title"].tolist()
episode_identifiers = episodes["identifier"].tolist()
for i, title in enumerate(episode_titles):
    df["episode"] = df["episode"].str.replace(title, episode_identifiers[i])

df = df[["name", "episode", "location", "sub_location", "time"]]
df.to_csv("processed/time_location.csv", index=False)
print(df)
