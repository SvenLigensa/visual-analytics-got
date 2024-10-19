import json
import pandas as pd

with open("raw/locations.json") as file:
    data = json.load(file)

data_list = []

for region in data["regions"]:
    data_list.append(
        {
            "location": region["location"],
            "sub_location": region["location"],
            "x_coord": None,
            "y_coord": None,
        }
    )

    for subLocation in region["subLocation"]:
        if subLocation.strip() != "":
            data_list.append(
                {
                    "location": region["location"],
                    "sub_location": subLocation,
                    "x_coord": None,
                    "y_coord": None,
                }
            )

df = pd.DataFrame(data_list)
df = df[["location", "sub_location", "x_coord", "y_coord"]]
df.to_csv("processed/locations.csv", index=False)
print(df)
