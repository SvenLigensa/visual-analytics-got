import json
import pandas as pd

with open("../raw/locations.json") as file:
    data = json.load(file)

data_list = []
location_id = 1

for region in data["regions"]:
    data_list.append(
        {
            "location_id": location_id,
            "sub_location": region["location"],
            "location": region["location"],
            "x_coord": None,
            "y_coord": None,
        }
    )
    location_id += 1

    for subLocation in region["subLocation"]:
        if subLocation.strip() != "":
            data_list.append(
                {
                    "location_id": location_id,
                    "sub_location": subLocation,
                    "location": region["location"],
                    "x_coord": None,
                    "y_coord": None,
                }
            )
            location_id += 1

df = pd.DataFrame(data_list)
df = df[["location_id", "sub_location", "location", "x_coord", "y_coord"]]
df.to_csv("locations.csv", index=False)
print(df)
