import json
import pandas as pd

with open("../raw/locations.json") as file:
    data = json.load(file)

    # Initialize the list to store the data and the location_id counter
    data_list = []
    location_id = 1

    # Iterate over each region and subLocation to build the data list
    for region in data["regions"]:
        # Add the region itself
        data_list.append(
            {
                "location_id": location_id,
                "location": region["location"],
                "region": region["location"],
                "x_coord": None,
                "y_coord": None,
            }
        )
        location_id += 1

        # Add each subLocation under the region
        for subLocation in region["subLocation"]:
            if subLocation.strip() != "":
                data_list.append(
                    {
                        "location_id": location_id,
                        "location": subLocation,
                        "region": region["location"],
                        "x_coord": None,
                        "y_coord": None,
                    }
                )
                location_id += 1

    # Create the pandas DataFrame
    df = pd.DataFrame(data_list)

    # Ensure the columns are in the specified order
    df = df[["location_id", "location", "region", "x_coord", "y_coord"]]

    # Export the DataFrame to a CSV file
    df.to_csv("locations.csv", index=False)
    # Print DataFrame to verify the output
    print(df)
