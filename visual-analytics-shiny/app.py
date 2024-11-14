from pathlib import Path
from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

from util import map

app_dir = Path(__file__).parent
static_dir = app_dir / "static"
data_dir = app_dir / "data"

location_data = pd.read_csv(data_dir / "locations.csv", dtype=str)
character_data = pd.read_csv(data_dir / "characters.csv", dtype=str)
episode_data = pd.read_csv(data_dir / "episodes.csv", dtype=str)
time_data = pd.read_csv(data_dir / "time.csv")
time_data_alt = pd.read_csv(data_dir / "characters_time.csv")
time_location_data = pd.read_csv(data_dir / "time_location_post.csv")

app_ui = ui.page_fluid(
    ui.tags.h1(
        {"class": "got-font"},
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
        ui.tags.link(rel="stylesheet", type="text/css", href="map/styles.css"),
        ui.tags.link(rel="stylesheet", type="text/css", href="network/styles.css"),
        ui.tags.link(rel="stylesheet", type="text/css", href="heatmap/styles.css"),
        ui.tags.script(src="https://d3js.org/d3.v7.min.js"),
        ui.tags.script(src="map/script.js"),
        ui.tags.script(src="network/script.js"),
        ui.tags.script(src="heatmap/script.js"),
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
                                    "maxItems": 3,
                                },
                            ),
                            ui.input_selectize(
                                "map_episode_start",
                                "Select start episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                            ),
                            ui.input_selectize(
                                "map_episode_end",
                                "Select end episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                            ),
                            ui.input_checkbox(
                                "show_time_spent",
                                "Show time spent at locations",
                                value=True,
                            ),
                            ui.input_checkbox(
                                "show_travel_paths", "Show travel paths", value=True
                            ),
                            # Slider between 0 and 100 for opacity of picture
                            ui.input_slider(
                                "map_opacity",
                                "Opacity of the map:",
                                min=0,
                                max=100,
                                value=100,
                                step=5,
                                ticks=False,
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
                            ui.tags.img(src="map/zoom.png", height="18px"),
                            class_="fit-toggle-button map-settings-button",
                        ),
                        ui.input_action_button(
                            "zoom_in",
                            ui.tags.img(src="map/zoom_in.png", height="18px"),
                            class_="zoom-in-button map-settings-button",
                        ),
                        ui.input_action_button(
                            "zoom_out",
                            ui.tags.img(src="map/zoom_out.png", height="18px"),
                            class_="zoom-out-button map-settings-button",
                        ),
                        ui.div(
                            {"id": "map-container"},
                            ui.tags.img(id="map-img", src="map/map.png"),
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
                        {"class": "network-card"},
                        ui.tags.svg(id="network-canvas"),
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
                                },
                            ),
                            ui.input_selectize(
                                "linechart_episode_start",
                                "Select start episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                            ),
                            ui.input_selectize(
                                "linechart_episode_end",
                                "Select end episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                            ),
                        )
                    )
                ),
                ui.div(
                    {"class": "full-size-div"},
                    ui.card(
                        output_widget("screentime_linechart", width="100%")
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "Screentime Streamgraph",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.div(
                        ui.card(
                            ui.card_header(ui.h4("Settings")),
                            ui.input_selectize(
                                "screentime_streamgraph_character",
                                "Select characters:",
                                choices=[],  # Updated server-side
                                multiple=True,
                                options={
                                    "placeholder": "Type to search...",
                                },
                            ),
                            ui.input_selectize(
                                "streamgraph_episode_start",
                                "Select start episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                            ),
                            ui.input_selectize(
                                "streamgraph_episode_end",
                                "Select end episode:",
                                choices=[],  # Updated server-side
                                multiple=False,
                            ),
                        )
                    )
                ),
                ui.div(
                    {"class": "full-size-div"},
                    ui.card(
                        ui.output_plot("screentime_streamgraph", width="100%")
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
        "screentime_streamgraph_character",
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
    ui.update_selectize(
        "streamgraph_episode_start",
        choices=episodes,
        selected="S01E01",
        server=True,
        session=session,
    )
    ui.update_selectize(
        "streamgraph_episode_end",
        choices=episodes,
        selected="S08E06",
        server=True,
        session=session,
    )

    @render_widget
    def screentime_linechart():
        selected_characters = input.screentime_linechart_character()
        episode_start = input.linechart_episode_start()
        episode_end = input.linechart_episode_end()

        if not selected_characters:
            fig = px.line()
            fig.add_annotation(
                x=0.5, y=0.5,
                text='Please select at least one character.',
                showarrow=False,
                font=dict(size=12),
                xref='paper', yref='paper',
                xanchor='center', yanchor='middle'
            )
            fig.update_xaxes(range=[0, 1])
            fig.update_yaxes(range=[0, 1])
            return fig

        # Filter data for selected characters
        filtered_data = time_data_alt[time_data_alt['name'].isin(selected_characters)]
        
        # Get all episodes in correct order and create episode mapping
        episodes = episode_data[
            (episode_data['identifier'] >= episode_start) &
            (episode_data['identifier'] <= episode_end)
        ]['identifier'].tolist()
        episode_indices = {ep: idx for idx, ep in enumerate(episodes)}
        
        # Add episode index for proper ordering
        filtered_data['episode_idx'] = filtered_data['episode'].map(episode_indices)
        filtered_data = filtered_data[filtered_data['episode_idx'].notna()]
        
        # Pivot the data to have characters as rows and episodes as columns
        pivot_df = filtered_data.pivot_table(
            index='name',
            columns='episode',
            values='time',
            fill_value=0
        )
        
        # Ensure all episodes are represented and in correct order
        pivot_df = pivot_df.reindex(columns=episodes, fill_value=0)
        
        # Melt the pivot table back to long format for plotting
        plot_data = pivot_df.reset_index().melt(
            id_vars=['name'],
            value_vars=episodes,
            var_name='episode',
            value_name='time'
        )
        
        # Create the line plot
        fig = px.line(
            plot_data, 
            x='episode',
            y='time',
            color='name',
            title='Screen Time per Episode',
            labels={
                'time': 'Screen Time (seconds)',
                'episode': 'Episode',
                'name': 'Character'
            }
        )
        
        # Customize the layout
        fig.update_layout(
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02
            ),
            margin=dict(r=150),
            xaxis_tickangle=-45
        )
        
        fig.update_traces(
            mode='lines+markers',
            hovertemplate='%{y:.0f} seconds<extra></extra>'
        )
        
        return fig

    @render.plot(alt="Streamgraph showing the screentime of selected characters")
    def screentime_streamgraph():
        selected_characters = input.screentime_streamgraph_character()
        episode_start = input.streamgraph_episode_start()
        episode_end = input.streamgraph_episode_end()

        if not selected_characters:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Please select at least one character.', 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_xticks([])
            ax.set_yticks([])
            return fig

        # Filter data for selected characters
        filtered_data = time_data_alt[
            (time_data_alt['name'].isin(selected_characters)) &
            (time_data_alt['episode'] >= episode_start) &
            (time_data_alt['episode'] <= episode_end)
        ]

        # Get episodes in correct order
        episodes = episode_data[
            (episode_data['identifier'] >= episode_start) &
            (episode_data['identifier'] <= episode_end)
        ]['identifier'].tolist()
        episode_indices = {ep: idx for idx, ep in enumerate(episodes)}
        
        # Add episode index for proper ordering
        filtered_data['episode_idx'] = filtered_data['episode'].map(episode_indices)
        
        # Pivot the data to have characters as rows and episodes as columns
        pivot_df = filtered_data.pivot_table(
            index='name',
            columns='episode_idx',
            values='time',
            fill_value=0
        )
        
        # Ensure all episodes are represented
        pivot_df = pivot_df.reindex(columns=range(len(episodes)), fill_value=0)
        
        x = range(len(episodes))
        y = pivot_df.values
        
        # Use interpolated values to make streamgraph smooth
        x_new = np.linspace(min(x), max(x), 500)  # Increase number of points => Smoother
        y_smooth = make_interp_spline(x, y, axis=1)(x_new)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.stackplot(
            x_new,
            y_smooth,
            labels=pivot_df.index,
            baseline='wiggle',
            colors=plt.cm.tab20.colors[:len(pivot_df.index)]
        )
        
        ax.set_xticks(x)
        ax.set_xticklabels(episodes, rotation=45, ha='right')
        ax.set_xlim(0, len(episodes)-1)
        ax.set_xlabel('Episode')
        ax.set_ylabel('Screen Time (seconds)')
        ax.set_title('Screentime Streamgraph')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        plt.tight_layout()
        return fig

    @reactive.Effect
    @reactive.event(input.map_opacity)
    async def handle_map_opacity_change():
        await session.send_custom_message(
            "set_map_opacity",
            {"opacity": input.map_opacity() / 100},
        )

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
        await map.handle_map_change(session, input, location_data, time_location_data)

    @reactive.Effect
    @reactive.event(input.map_episode_start)
    async def handle_map_episode_start_change():
        await map.handle_map_change(session, input, location_data, time_location_data)

    @reactive.Effect
    @reactive.event(input.map_episode_end)
    async def handle_map_episode_end_change():
        await map.handle_map_change(session, input, location_data, time_location_data)

    @reactive.Effect
    @reactive.event(input.show_time_spent)
    async def handle_show_time_spend_change():
        await map.handle_map_change(session, input, location_data, time_location_data)

    @reactive.Effect
    @reactive.event(input.show_travel_paths)
    async def handle_show_travel_paths_change():
        await map.handle_map_change(session, input, location_data, time_location_data)

zoom_level = 100
fit_mode = "w"
app = App(app_ui, server, static_assets=static_dir)
