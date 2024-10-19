import json
import pandas as pd

with open("raw/episodes.json") as file:
    data = json.load(file)

data_list = []
episode_id = 1

for episode in data["episodes"]:
    data_list.append(
        {
            "episode_id": episode_id,
            "identifier": f"S{episode["seasonNum"]:02}E{episode["episodeNum"]:02}",
            "title": episode["episodeTitle"],
        }
    )
    episode_id += 1

df = pd.DataFrame(data_list)
df = df[["episode_id", "identifier", "title"]]
df.to_csv("processed/episodes.csv", index=False)
print(df)
