import pandas as pd

def filter_map_data(name, episode_start, episode_end, time_location_data):
    # Filter name
    data = time_location_data[time_location_data["name"] == name]
    # Filter episode range
    data = data[(data["episode"] >= episode_start) & (data["episode"] <= episode_end)]
    data = data.drop(columns="name")
    # Group adjacent rows with the same sub_location
    data = (
        data.assign(
            # create groups by checking if value is different from previous value
            group=lambda x: (x["sub_location"] != x["sub_location"].shift()).cumsum()
        )
        .groupby("group")
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
    travels = pd.DataFrame(columns=["from", "to", "num_travels"])
    prev_location = None
    for index, row in data.iterrows():
        if prev_location is not None:
            if prev_location != row["sub_location"]:
                # Check if the travel already exists
                travel = travels[
                    (travels["from"] == prev_location)
                    & (travels["to"] == row["sub_location"])
                ]
                if len(travel) == 0:
                    # Add a new row
                    travels.loc[len(travels)] = [prev_location, row["sub_location"], 1]
                else:
                    # Increment the number of travels
                    travel_index = travel.index[0]
                    travels.at[travel_index, "num_travels"] += 1
        prev_location = row["sub_location"]
    # Calculate the aggregated time spent in each location
    data_agg = (
        data.groupby("sub_location")
        .agg(
            {
                "time": "sum",
            }
        )
        .reset_index()
    )
    return (data, data_agg, travels)
