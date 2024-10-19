import json
import pandas as pd

with open("raw/characters.json") as file:
    data = json.load(file)

data_list = []
character_id = 1

for character in data["characters"]:
    data_list.append(
        {
            "character_id": character_id,
            "name": character["characterName"],
            "house": character["houseName"] if "houseName" in character else "Other",
            "image": character["characterImageThumb"] if "characterImageThumb" in character else None,
        }
    )
    character_id += 1

df = pd.DataFrame(data_list)
df = df[["character_id", "name", "house", "image"]]
df.to_csv("processed/characters.csv", index=False)
print(df)
