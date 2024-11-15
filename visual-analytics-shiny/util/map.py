import pandas as pd

def filter_map_data(name_list, episode_start, episode_end, time_location_data):
    # Filter
    data = time_location_data[
        (time_location_data["name"].isin(name_list)) &
        (time_location_data["episode"].between(episode_start, episode_end))
    ]
    # Aggregate
    data = (
        data.assign(group=lambda x: (x["sub_location"] != x["sub_location"].shift()).cumsum())
        .groupby(["group", "name"])
        .agg({
            "episode": lambda x: list(x.unique()),
            "sub_location": "first",
            "time": "sum",
        })
        .reset_index()
        .drop(columns="group")
    )
    # Calculate travels
    travels = []
    for name in name_list:
        character_data = data[data["name"] == name]["sub_location"].tolist()
        for prev_loc, curr_loc in zip(character_data, character_data[1:]):
            if prev_loc != curr_loc:
                travel_key = (prev_loc, curr_loc, name)
                matching_travel = next((t for t in travels if t[:3] == travel_key), None)
                if matching_travel:
                    matching_travel[3] += 1
                else:
                    travels.append([*travel_key, 1])
    # Convert to dataframe
    travels = pd.DataFrame(travels, columns=["from", "to", "name", "num_travels"])
    # Calculate aggregated time
    data_agg = data.groupby(["sub_location", "name"])["time"].sum().reset_index()
    return (data, data_agg, travels)

async def handle_map_change(session, input, location_data, time_location_data):
    selected_characters = list(input.map_character())
    character_mapping = {char: idx for idx, char in enumerate(selected_characters)}
    
    await session.send_custom_message("show_legend", {"characters": selected_characters})
    await session.send_custom_message("remove_svg_elements", {})
    
    _, char_locations_agg, char_travels = filter_map_data(
        selected_characters, 
        input.map_episode_start(), 
        input.map_episode_end(), 
        time_location_data
    )

    if input.show_travel_paths():
        await draw_travel_paths(session, char_travels, location_data, character_mapping)
    if input.show_time_spent():
        await draw_time_bubbles(session, char_locations_agg, location_data, character_mapping)
    await draw_location_labels(session, char_locations_agg, location_data, character_mapping)

async def draw_travel_paths(session, character_travels, location_data, character_mapping):
    def get_coords(loc_name):
        loc = location_data[location_data["sub_location"] == loc_name]
        return None if loc.empty else (loc["x_coord"].values[0], loc["y_coord"].values[0])
    
    for _, row in character_travels.iterrows():
        from_coords = get_coords(row["from"])
        to_coords = get_coords(row["to"])
        
        if not (from_coords and to_coords):
            continue
            
        await session.send_custom_message("show_travel", {
            "character_num": character_mapping[row["name"]],
            "from_x": from_coords[0],
            "from_y": from_coords[1],
            "to_x": to_coords[0],
            "to_y": to_coords[1],
            "num_travels": row["num_travels"],
        })

async def draw_time_bubbles(session, character_locations_aggregated, location_data, character_mapping):
    character_locations_aggregated_sorted = character_locations_aggregated.sort_values(
        by=["sub_location", "time"], ascending=[True, False]
    )
    character_locations_aggregated_sorted = pd.merge(
        character_locations_aggregated_sorted,
        location_data,
        on="sub_location",
        how="left",
    )
    
    for _, row in character_locations_aggregated_sorted.iterrows():
        if pd.isna(row["x_coord"]) or pd.isna(row["y_coord"]):
            continue
        await session.send_custom_message(
            "show_location_bubble",
            {
                "character_num": character_mapping[row["name"]],
                "x_coord": row["x_coord"],
                "y_coord": row["y_coord"],
                "time": row["time"],
            },
        )

async def draw_location_labels(session, character_locations_aggregated, location_data, character_mapping):
    character_locations_aggregated_sorted = character_locations_aggregated.sort_values(
        by=["sub_location", "time"], ascending=[True, False]
    )
    character_locations_aggregated_sorted = pd.merge(
        character_locations_aggregated_sorted,
        location_data,
        on="sub_location",
        how="left",
    )
    
    unique_location_data = (character_locations_aggregated_sorted.groupby("sub_location")
        .agg({
            "x_coord": "first",
            "y_coord": "first",
            "name": list,
            "time": list,
        })
        .reset_index())

    for _, row in unique_location_data.iterrows():
        if pd.isna(row["x_coord"]) or pd.isna(row["y_coord"]):
            continue
        await session.send_custom_message(
            "show_location_label",
            {
                "sub_location": row["sub_location"],
                "x_coord": row["x_coord"],
                "y_coord": row["y_coord"],
                "character_nums": [character_mapping[name] for name in row["name"]],
                "character_times": row["time"],
            },
        )
