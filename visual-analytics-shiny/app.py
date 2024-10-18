from pathlib import Path
from shiny import App, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd

from util import map

app_ui = ui.page_fluid(
    ui.tags.div(
        {"class": "got-font", "style": "font-size: 32px; text-align: center;"},
        "Game of Thrones Analyzer",
    ),
    ui.tags.style(
        """
        body {
            height: 100vh;
        }
        """
    ),
    ui.tags.head(
        ui.tags.link(rel="stylesheet", type="text/css", href="styles.css"),
        ui.tags.link(rel="stylesheet", type="text/css", href="map-styles.css"),
        ui.tags.script(src="script.js"),
    ),
    ui.navset_pill(
        ui.nav_panel(
            "Map",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.div(
                        ui.card(
                            ui.card_header(ui.h4("Settings")),
                            ui.input_selectize(
                                "map_character",
                                "Select characters:",
                                choices=[],  # Updated server-side
                                multiple=True,
                                options={
                                    "placeholder": "Type to search...",
                                    "maxOptions": 5,
                                },
                            ),
                            ui.input_selectize(
                                "map_episode_start",
                                "Select start episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                                options={
                                    "maxOptions": 5,
                                },
                            ),
                            ui.input_selectize(
                                "map_episode_end",
                                "Select end episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                                options={
                                    "maxOptions": 5,
                                },
                            ),
                            ui.input_checkbox(
                                "show_time_spent",
                                "Show time spent at locations",
                                value=True,
                            ),
                            ui.input_checkbox(
                                "show_travel_paths", "Show travel paths", value=True
                            ),
                        )
                    )
                ),
                # Main content area
                ui.div(
                    {"class": "content-container"},
                    ui.card(
                        {"class": "map-card"},
                        ui.input_action_button(
                            "toggle_fit",
                            ui.tags.img(src="zoom.png", height="30px"),
                            class_="fit-toggle-button map-settings-button",
                        ),
                        ui.input_action_button(
                            "zoom_in",
                            ui.tags.img(src="zoom_in.png", height="30px"),
                            class_="zoom-in-button map-settings-button",
                        ),
                        ui.input_action_button(
                            "zoom_out",
                            ui.tags.img(src="zoom_out.png", height="30px"),
                            class_="zoom-out-button map-settings-button",
                        ),
                        ui.div(
                            {"id": "map-container"},
                            ui.tags.img(id="map-img", src="map.png"),
                            ui.tags.svg(id="map-canvas"),
                        ),
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "Character Network",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.div(
                        ui.card(
                            ui.card_header(ui.h4("Settings")),
                            ui.input_selectize(
                                "network_character",
                                "Select characters:",
                                choices=[],  # Updated server-side
                                multiple=True,
                                options={
                                    "placeholder": "Type to search...",
                                    "maxOptions": 5,
                                },
                            ),
                            ui.input_selectize(
                                "network_relationships",
                                "Select relationship types:",
                                choices=[
                                    "Parent",
                                    "Sibling",
                                    "Married / Engaged",
                                    "Killed",
                                    "Serves",
                                    "Guardian of",
                                    "Ally",
                                ],
                                multiple=True,
                                options={
                                    "placeholder": "Type to search...",
                                },
                            ),
                        )
                    )
                ),
                ui.div(
                    {"class": "content-container"},
                    ui.card(
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "Screentime Linechart",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.div(
                        ui.card(
                            ui.card_header(ui.h4("Settings")),
                            ui.input_selectize(
                                "screentime_linechart_character",
                                "Select characters:",
                                choices=[],  # Updated server-side
                                multiple=True,
                                options={
                                    "placeholder": "Type to search...",
                                    "maxOptions": 5,
                                },
                            ),
                            ui.input_selectize(
                                "linechart_episode_start",
                                "Select start episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                                options={
                                    "maxOptions": 5,
                                },
                            ),
                            ui.input_selectize(
                                "linechart_episode_end",
                                "Select end episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                                options={
                                    "maxOptions": 5,
                                },
                            ),
                        )
                    )
                ),
                ui.div(
                    {"class": "full-size-card"},
                    ui.card(
                        output_widget("screentime_linechart", width="100%")
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "Screentime Heatmap",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.div(
                        ui.card(
                            ui.card_header(ui.h4("Settings")),
                            "Coming soon...",
                        )
                    )
                ),
                ui.div(
                    {"class": "content-container"},
                    ui.card(

                    ),
                ),
            ),
        ),
    ),
)


def server(input, output, session):

    # Read data
    location_data = pd.read_csv(data_dir / "locations.csv", dtype=str)
    character_data = pd.read_csv(data_dir / "characters.csv", dtype=str)
    episode_data = pd.read_csv(data_dir / "episodes.csv", dtype=str)
    time_data = pd.read_csv(data_dir / "time.csv")

    # Update selectize inputs
    characters = character_data["name"].tolist()
    episodes = episode_data["identifier"].tolist()
    ui.update_selectize(
        "map_character", choices=characters, server=True, session=session
    )
    ui.update_selectize(
        "network_character", choices=characters, server=True, session=session
    )
    ui.update_selectize(
        "screentime_linechart_character",
        choices=characters,
        server=True,
        session=session,
    )
    ui.update_selectize(
        "screentime_heatmap_character", choices=characters, server=True, session=session
    )
    ui.update_selectize(
        "map_episode_start",
        choices=episodes,
        selected="S01E01",
        server=True,
        session=session,
    )
    ui.update_selectize(
        "map_episode_end",
        choices=episodes,
        selected="S08E06",
        server=True,
        session=session,
    )
    ui.update_selectize(
        "linechart_episode_start",
        choices=episodes,
        selected="S01E01",
        server=True,
        session=session,
    )
    ui.update_selectize(
        "linechart_episode_end",
        choices=episodes,
        selected="S08E06",
        server=True,
        session=session,
    )

    
    @render_widget
    def screentime_linechart():
        selected_characters = input.screentime_linechart_character()

        if not selected_characters:
            return px.line()

        filtered_data = time_data[time_data['name'].isin(selected_characters)]

        # Melt the DataFrame so that episodes become x-axis and times become y-axis
        # 'name' remains as the identifier for each line
        df_melted = filtered_data.melt(id_vars=['name'], var_name='episode', value_name='time')

        # Ensure that the episode order is maintained correctly (e.g., S01E01, S01E02)
        df_melted['episode'] = pd.Categorical(df_melted['episode'], categories=sorted(filtered_data.columns[1:]), ordered=True)

        # Plot the data using Plotly
        fig = px.line(df_melted, x='episode', y='time', color='name', title='Time Spent on Each Episode')

        return fig



    
    @reactive.Effect
    @reactive.event(input.toggle_fit)
    async def toggle_fit():
        global zoom_level, fit_mode
        # Reset the zoom to 100%
        zoom_level = 100
        await session.send_custom_message("set_zoom", {"zoom": zoom_level})
        fit_mode = "h" if fit_mode == "w" else "w"
        await session.send_custom_message("toggle_fit", {"fit_mode": fit_mode})

    @reactive.Effect
    @reactive.event(input.zoom_in)
    async def zoom_in():
        global zoom_level
        zoom_level = zoom_level * 1.5
        await session.send_custom_message("set_zoom", {"zoom": zoom_level})

    @reactive.Effect
    @reactive.event(input.zoom_out)
    async def zoom_out():
        global zoom_level
        zoom_level = zoom_level / 1.5
        await session.send_custom_message("set_zoom", {"zoom": zoom_level})

    @reactive.Effect
    @reactive.event(input.map_character)
    async def handle_map_character_change():
        global previous_selected_characters
        # Current selection from the input
        current_selected_characters = set(input.map_character())
        # Compute newly added and removed characters
        added_character = current_selected_characters - previous_selected_characters
        removed_character = previous_selected_characters - current_selected_characters
        previous_selected_characters = current_selected_characters

        if removed_character:
            removed_character = list(removed_character)[0]
            character = character_data[character_data["name"] == removed_character]
            await session.send_custom_message(
                "remove_svg_elements",
                {
                    "type": f"c-{character["character_id"].values[0]}",
                },
            )

        if added_character:
            added_character = list(added_character)[0]
            character = character_data[character_data["name"] == added_character].iloc[
                0
            ]
            name = character["name"]
            character_id = character["character_id"]
            episode_start = input.map_episode_start()
            episode_end = input.map_episode_end()
            time_spend = input.show_time_spent()
            travel_paths = input.show_travel_paths()

            (character_locations, character_locations_aggregated, character_travels) = (
                map.filter_map_data(name, episode_start, episode_end)
            )

            # Get x_coord and y_coord of every sub_location by performing a join of
            # the character_loccations_aggregated and the locations.csv data on the "sub_location" column
            character_locations_aggregated = pd.merge(
                character_locations_aggregated,
                location_data,
                on="sub_location",
                how="left",
            )
            character_locations_aggregated = character_locations_aggregated.drop(
                columns=["location_id"]
            )

            for _, row in character_locations_aggregated.iterrows():
                if pd.isna(row["x_coord"]) or pd.isna(row["y_coord"]):
                    continue
                await session.send_custom_message(
                    "show_location",
                    {
                        "character_id": character_id,
                        "sub_location": row["sub_location"],
                        "x_coord": row["x_coord"],
                        "y_coord": row["y_coord"],
                        "time": row["time"],
                        "show_time": time_spend,
                    },
                )
            if travel_paths:
                for _, row in character_travels.iterrows():
                    # Get the x and y coordinates of the "from" and "to" locations
                    from_location = location_data[
                        location_data["sub_location"] == row["from"]
                    ]
                    to_location = location_data[
                        location_data["sub_location"] == row["to"]
                    ]
                    # Check, if all coordinates are available
                    if (
                        from_location.empty
                        or to_location.empty
                        or any(
                            pd.isna(
                                [
                                    from_location["x_coord"].values[0],
                                    from_location["y_coord"].values[0],
                                    to_location["x_coord"].values[0],
                                    to_location["y_coord"].values[0],
                                ]
                            )
                        )
                    ):
                        continue
                    await session.send_custom_message(
                        "show_travel",
                        {
                            "character_id": character_id,
                            "from_x": from_location["x_coord"].values[0],
                            "from_y": from_location["y_coord"].values[0],
                            "to_x": to_location["x_coord"].values[0],
                            "to_y": to_location["y_coord"].values[0],
                            "num_travels": row["num_travels"],
                        },
                    )

    @reactive.Effect
    @reactive.event(input.map_episode_start)
    async def handle_map_episode_start_change():
        pass

    @reactive.Effect
    @reactive.event(input.map_episode_end)
    async def handle_map_episode_end_change():
        pass

    @reactive.Effect
    @reactive.event(input.show_time_spent)
    async def handle_show_time_spend_change():
        await session.send_custom_message(
            "remove_svg_elements",
            {
                "type": "circle",
            },
        )
        current_selected_characters = set(input.map_character())
        for character in current_selected_characters:
            character = character_data[character_data["name"] == character].iloc[0]
            name = character["name"]
            character_id = character["character_id"]
            episode_start = input.map_episode_start()
            episode_end = input.map_episode_end()
            time_spend = input.show_time_spent()
            travel_paths = input.show_travel_paths()

            (character_locations, character_locations_aggregated, character_travels) = (
                map.filter_map_data(name, episode_start, episode_end)
            )

            # Get x_coord and y_coord of every sub_location by performing a join of
            # the character_loccations_aggregated and the locations.csv data on the "sub_location" column
            character_locations_aggregated = pd.merge(
                character_locations_aggregated,
                location_data,
                on="sub_location",
                how="left",
            )
            character_locations_aggregated = character_locations_aggregated.drop(
                columns=["location_id"]
            )

            for _, row in character_locations_aggregated.iterrows():
                if pd.isna(row["x_coord"]) or pd.isna(row["y_coord"]):
                    continue
                await session.send_custom_message(
                    "show_location",
                    {
                        "character_id": character_id,
                        "sub_location": row["sub_location"],
                        "x_coord": row["x_coord"],
                        "y_coord": row["y_coord"],
                        "time": row["time"],
                        "show_time": time_spend,
                    },
                )

    @reactive.Effect
    @reactive.event(input.show_travel_paths)
    async def handle_show_travel_paths_change():
        if not input.show_travel_paths():
            await session.send_custom_message("remove_lines", {})
            await session.send_custom_message(
                "remove_svg_elements",
                {
                    "type": "line",
                },
            )
        else:
            current_selected_characters = set(input.map_character())
            for character in current_selected_characters:
                character = character_data[character_data["name"] == character].iloc[0]
                name = character["name"]
                character_id = character["character_id"]
                episode_start = input.map_episode_start()
                episode_end = input.map_episode_end()
                time_spend = input.show_time_spent()
                travel_paths = input.show_travel_paths()

                (
                    character_locations,
                    character_locations_aggregated,
                    character_travels,
                ) = map.filter_map_data(name, episode_start, episode_end)

                for _, row in character_travels.iterrows():
                    # Get the x and y coordinates of the "from" and "to" locations
                    from_location = location_data[
                        location_data["sub_location"] == row["from"]
                    ]
                    to_location = location_data[
                        location_data["sub_location"] == row["to"]
                    ]
                    if from_location.empty or to_location.empty:
                        continue
                    # Check, if the x and y coordinates are available (i.e. not NaN)
                    if any(
                        pd.isna(
                            [
                                from_location["x_coord"].values[0],
                                from_location["y_coord"].values[0],
                                to_location["x_coord"].values[0],
                                to_location["y_coord"].values[0],
                            ]
                        )
                    ):
                        continue
                    await session.send_custom_message(
                        "show_travel",
                        {
                            "character_id": character_id,
                            "from_x": from_location["x_coord"].values[0],
                            "from_y": from_location["y_coord"].values[0],
                            "to_x": to_location["x_coord"].values[0],
                            "to_y": to_location["y_coord"].values[0],
                            "num_travels": row["num_travels"],
                        },
                    )


zoom_level = 100
fit_mode = "w"
previous_selected_characters = set()

app_dir = Path(__file__).parent
static_dir = app_dir / "static"
data_dir = app_dir / "data"
app = App(app_ui, server, static_assets=static_dir)
