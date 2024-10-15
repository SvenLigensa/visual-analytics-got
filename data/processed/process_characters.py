import json
import pandas as pd

with open("../raw/characters.json") as file:
    data = json.load(file)

    # Initialize the list to store the data and the location_id counter
    data_list = []
    character_id = 1

    # Iterate over each region and subLocation to build the data list
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

    # Create the pandas DataFrame
    df = pd.DataFrame(data_list)

    # Ensure the columns are in the specified order
    df = df[["character_id", "name", "house", "image"]]

    # Export the DataFrame to a CSV file
    df.to_csv("characters.csv", index=False)
    # Print DataFrame to verify the output
    print(df)
