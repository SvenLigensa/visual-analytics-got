import json
import pandas as pd

with open("../raw/episodes.json") as file:
    data = json.load(file)

    # Initialize the list to store the data and the location_id counter
    data_list = []
    episode_id = 1

    # Iterate over each region and subLocation to build the data list
    for episode in data["episodes"]:
        data_list.append(
            {
                "episode_id": episode_id,
                "identifier": f"S{episode["seasonNum"]:02}E{episode["episodeNum"]:02}",
                "title": episode["episodeTitle"],
            }
        )
        episode_id += 1

    # Create the pandas DataFrame
    df = pd.DataFrame(data_list)

    # Ensure the columns are in the specified order
    df = df[["episode_id", "identifier", "title"]]

    # Export the DataFrame to a CSV file
    df.to_csv("episodes.csv", index=False)
    # Print DataFrame to verify the output
    print(df)
