import pandas as pd

def filter_map_data(name_list, episode_start, episode_end, time_location_data):
    # Filter names
    data = time_location_data[time_location_data["name"].isin(name_list)]
    # Filter episode range
    data = data[(data["episode"] >= episode_start) & (data["episode"] <= episode_end)]
    # Group adjacent rows with the same sub_location
    data = (
        data.assign(
            # create groups by checking if value is different from previous value
            group=lambda x: (x["sub_location"] != x["sub_location"].shift()).cumsum()
        )
        .groupby(["group", "name"])
        .agg(
            {
                "episode": lambda x: list(x.unique()),
                "sub_location": "first",
                "time": "sum",
            }
        )
        .reset_index()
    )
    data = data.drop(columns="group")
    # Calculate number of travels between locations
    travels = pd.DataFrame(columns=["from", "to", "num_travels", "name"])

    for name in name_list:
        character_data = time_location_data[time_location_data["name"] == name]
        character_data_filtered = character_data[(character_data["episode"] >= episode_start) & (character_data["episode"] <= episode_end)]
        prev_location = None
        for _, row in character_data_filtered.iterrows():
            if prev_location is not None:
                if prev_location != row["sub_location"]:
                    # Check if the travel already exists
                    travel = travels[
                        (travels["from"] == prev_location)
                        & (travels["to"] == row["sub_location"])
                        & (travels["name"] == name)
                    ]
                    if len(travel) == 0:
                        # Add a new row
                        travels.loc[len(travels)] = [prev_location, row["sub_location"], 1, name]
                    else:
                        # Increment the number of travels
                        travel_index = travel.index[0]
                        travels.at[travel_index, "num_travels"] += 1
            prev_location = row["sub_location"]
    # Calculate the aggregated time spent in each location
    data_agg = (
        data.groupby(["sub_location", "name"])
        .agg(
            {
                "time": "sum",
            }
        )
        .reset_index()
    )
    return (data, data_agg, travels)
