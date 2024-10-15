from pathlib import Path
from shiny import App, ui, reactive
import pandas as pd

app_ui = ui.page_fluid(
    ui.tags.div({"class": "got-font", "style": "font-size: 32px; text-align: center;"}, "Game of Thrones Analyzer"),
    # Header with external resources
    ui.tags.head(
        ui.tags.link(rel="stylesheet", type="text/css", href="styles.css"),
        ui.tags.link(rel="stylesheet", type="text/css", href="map-styles.css"),
        ui.tags.script(src="script_python.js"),
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
                            ui.input_checkbox("show_time_spent", "Show time spent at locations", value=True),
                            ui.input_checkbox("show_travel_paths", "Show travel paths", value=True),
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
                            ui.tags.img(src="fit_h.png", height="30px"),
                            class_="fit-toggle-button",
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
                                choices=["Parent", "Sibling", "Married / Engaged", "Killed", "Serves", "Guardian of", "Ally"],  # Updated server-side
                                multiple=True,
                                options={
                                    "placeholder": "Type to search...",
                                },
                            ),
                        )
                    )
                )
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
                )
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
                )
            ),
        ),
    ),
)

def server(input, output, session):
    # Read city data
    location_data = pd.read_csv(app_dir / "locations.csv", dtype=str)
    character_data = pd.read_csv(app_dir / "characters.csv", dtype=str)
    episode_data = pd.read_csv(app_dir / "episodes.csv", dtype=str)

    # Update selectize inputs
    characters = character_data["name"].tolist()
    episodes = episode_data["identifier"].tolist()

    ui.update_selectize("map_character", choices=characters, server=True, session=session)
    ui.update_selectize("network_character", choices=characters, server=True, session=session)
    ui.update_selectize("screentime_linechart_character", choices=characters, server=True, session=session)
    ui.update_selectize("screentime_heatmap_character", choices=characters, server=True, session=session)

    ui.update_selectize("map_episode_start", choices=episodes, selected="S01E01", server=True, session=session)
    ui.update_selectize("map_episode_end", choices=episodes, selected="S08E06", server=True, session=session)
    ui.update_selectize("linechart_episode_start", choices=episodes, selected="S01E01", server=True, session=session)
    ui.update_selectize("linechart_episode_end", choices=episodes, selected="S08E06", server=True, session=session)

    # Use a reactive value for fit_mode
    fit_mode = reactive.Value("Width")

    @reactive.Effect
    @reactive.event(input.toggle_fit)
    async def toggle_fit():
        if fit_mode.get() == "Width":
            fit_mode.set("Height")
            # Await the custom message to the frontend
            await session.send_custom_message("toggle_fit", {
                "fit_mode": "Height",
                "button_img": "fit_w.png"
            })
        else:
            fit_mode.set("Width")
            # Await the custom message to the frontend
            await session.send_custom_message("toggle_fit", {
                "fit_mode": "Width",
                "button_img": "fit_h.png"
            })

    @reactive.Effect
    @reactive.event(input.show)
    async def show_cities():
        selected_cities = location_data[location_data["location"].isin(input.location())]
        for _, city in selected_cities.iterrows():
            # Skip cities with missing coordinates
            if (city["x_coord"] == "") or (city["y_coord"] == ""):
                continue
            # Await the custom message to the frontend
            await session.send_custom_message("show_city", {
                "location": city["location"],
                "x_coord": float(city["x_coord"]),
                "y_coord": float(city["y_coord"]),
            })

    @reactive.Effect
    @reactive.event(input.hide)
    async def remove_annotations():
        await session.send_custom_message("remove_annotations", {})


app_dir = Path(__file__).parent
app = App(app_ui, server, static_assets=app_dir / "www")
