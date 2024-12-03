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
from util.heatmap import create_heatmap
import plotly.graph_objects as go

app_dir = Path(__file__).parent
static_dir = app_dir / "static"
data_dir = app_dir / "data"

location_data = pd.read_csv(data_dir / "locations.csv", dtype=str)
character_data = pd.read_csv(data_dir / "characters.csv", dtype=str)
episode_data = pd.read_csv(data_dir / "episodes.csv", dtype=str)
time_data = pd.read_csv(data_dir / "time.csv", index_col=0)
time_data_alt = pd.read_csv(data_dir / "characters_time.csv")
time_location_data = pd.read_csv(data_dir / "time_location_post.csv")
network_nodes = pd.read_json(data_dir / "got_network_nodes.json")
network_links = pd.read_json(data_dir / "got_network_links.json")

characters = character_data["name"].tolist()
episodes = episode_data["identifier"].tolist()

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
                    ui.card(
                        {"class": "settings-card"},
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
                    ui.card(
                        {"class": "settings-card"},
                        ui.card_header(ui.h4("Settings")),
                        ui.input_selectize(
                            "network_character",
                            "Select characters:",
                            choices=[],
                            multiple=True,
                            options={
                                "placeholder": "Type to search...",
                            },
                        ),
                        ui.input_selectize(
                            "network_relationships",
                            "Select relationship types:",
                            choices=[
                                "parent",
                                "sibling",
                                "married",
                                "killed",
                                "serves",
                                "guardianOf",
                                "ally",
                            ],
                            multiple=True,
                            options={
                                "placeholder": "Type to search...",
                            },
                        ),
                        ui.input_checkbox(
                            "show_character_pictures",
                            "Show pictures",
                            value=False
                        ),
                    )
                ),
                ui.div(
                    {"class": "full-size-div"},
                    ui.card(
                        ui.tags.svg(id="network-canvas"),
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "Screentime Heatmap",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.card(
                        {"class": "settings-card"},
                        ui.card_header(ui.h4("Settings")),
                        ui.input_slider(
                            "heatmap_threshold",
                            "Screentime range (minutes):",
                            min=0,
                            max=685,
                            value=[60, 685],
                        ),
                        output_widget("screentime_distribution"),
                    )
                ),
                ui.div(
                    {"class": "full-size-div"},
                    ui.card(
                        output_widget("character_heatmap", width="100%", height="auto")
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "Screentime Streamgraph",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.card(
                        {"class": "settings-card"},
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
            "Screentime Linechart",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.card(
                        {"class": "settings-card"},
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
                ),
                ui.div(
                    {"class": "full-size-div"},
                    ui.card(
                        output_widget("screentime_linechart", width="100%")
                    ),
                ),
            ),
        ),
        ui.nav_spacer(),
        ui.nav_panel(
            "About",
            ui.div(
                {"id": "about-container"},
                ui.h1("Report"),
                ui.p(['This visual analytics app was developed by Sven Ligensa, Camille Alazard and Zhao Lige in the course ', ui.em("Data Visualization"), ' at the UPM in the academic year 2024-2025.',
                "The source code is made available on ",
                ui.a([
                    ui.img({"src": "about/gh_logo.png", "height": "16px", "style": "vertical-align: middle;"}),
                    " GitHub"
                    ], href="https://github.com/SvenLigensa/visual-analytics-got", target="_blank"),
                    ". We used ",
                    ui.a([
                        ui.img({"src": "about/shiny_logo.png", "height": "16px", "style": "vertical-align: middle;"}),
                        ' Shiny for Python'
                    ], href="https://shiny.posit.co/py/", target="_blank"),
                    " as the framework, while the visualizations utilize different libraries, as discussed below."
                ]),
                ui.h3("Credits"),
                ui.p(["The data used in this project was obtained from ",
                    ui.a("this repository", href="https://github.com/jeffreylancaster/game-of-thrones", target="_blank"),
                    " by Jeffrey Lancaster. We appreciate the effort he put into creating this dataset and thank him for releasing it as open-source. ",
                    "The map of Westeros and Essos was obtained from ",
                    ui.a(ui.img({"src": "about/hbo_logo.png", "height": "16px", "style": "vertical-align: middle;"}),
                         " here", href="https://www.hbo.com/house-of-the-dragon/map-of-westeros", target="_blank"),
                    "."
                ]),
            ),
        ),
    ),
)


def server(input, output, session):
    # Update selectize inputs
    ui.update_selectize("map_character", choices=characters, server=True, session=session)
    ui.update_selectize("network_character", choices=characters, server=True, session=session)
    ui.update_selectize("screentime_linechart_character", choices=characters, server=True, session=session)
    ui.update_selectize("screentime_streamgraph_character", choices=characters, server=True, session=session)
    ui.update_selectize("screentime_heatmap_character", choices=characters, server=True, session=session)
    ui.update_selectize("heatmap_characters", choices=characters, selected=None)
    ui.update_selectize("map_episode_start", choices=episodes, selected="S01E01", server=True, session=session)
    ui.update_selectize("map_episode_end", choices=episodes, selected="S08E06", server=True, session=session)
    ui.update_selectize("linechart_episode_start", choices=episodes, selected="S01E01", server=True, session=session)
    ui.update_selectize("linechart_episode_end", choices=episodes, selected="S08E06", server=True, session=session)
    ui.update_selectize("streamgraph_episode_start", choices=episodes, selected="S01E01", server=True, session=session)
    ui.update_selectize("streamgraph_episode_end", choices=episodes, selected="S08E06", server=True, session=session)

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
    @reactive.event(input.map_character, input.map_episode_start, input.map_episode_end, input.show_time_spent, input.show_travel_paths)
    async def handle_show_travel_paths_change():
        await map.handle_map_change(session, input, location_data, time_location_data)

    # Initialize network visualization
    @reactive.Effect
    async def initialize_network():
        network_data = {
            "nodes": network_nodes.to_dict('records'),
            "links": network_links.to_dict('records')
        }
        await session.send_custom_message("show_network", network_data)

    @reactive.Effect
    @reactive.event(input.network_character, input.network_relationships, input.show_character_pictures)
    async def handle_network_filter():
        chars = list(input.network_character()) or network_nodes['id'].tolist()
        rels = list(input.network_relationships())
        show_pictures = input.show_character_pictures()
        
        # Get links connected to selected characters
        links = network_links[
            network_links['source'].isin(chars) |
            network_links['target'].isin(chars)
        ]
        
        # Filter by relationship type if specified
        if rels:
            links = links[links['category'].isin(rels)]
        
        # Get all nodes that are connected through the filtered links
        connected_chars = set(links['source'].tolist() + links['target'].tolist())
        # Add back selected characters only if they have connections
        connected_chars.update(char for char in chars if char in connected_chars)
        
        nodes = network_nodes[network_nodes['id'].isin(connected_chars)]
        
        await session.send_custom_message(
            "show_network",
            {
                "nodes": nodes.to_dict('records'),
                "links": links.to_dict('records'),
                "show_pictures": show_pictures,
            }
        )

    @reactive.Effect
    @reactive.event(input.network_node_click)
    async def handle_network_node_click():
        clicked_character = input.network_node_click()
        current_selection = input.network_character() or ()
        
        # Toggle selection: remove if present, add if not
        if clicked_character in current_selection:
            # Remove character from selection
            new_selection = tuple(char for char in current_selection if char != clicked_character)
        else:
            # Add character to selection
            new_selection = current_selection + (clicked_character,)
            
        ui.update_selectize(
            "network_character",
            selected=new_selection,
            choices=characters,
            server=True,
            session=session
        )

    @output
    @render_widget
    def character_heatmap():
        return create_heatmap(time_data, input.heatmap_threshold())

    @render_widget
    def screentime_distribution():
        # Calculate total screentime for each character (in minutes)
        total_screentime = time_data.sum(axis=1) / 60
        max_screentime = total_screentime.max()

        # Create histogram
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=total_screentime,
            nbinsx=100,
            name='All Characters'
        ))

        # Add vertical lines for the current threshold
        min_threshold, max_threshold = input.heatmap_threshold()

        fig.add_vrect(x0=min_threshold, x1=max_threshold, 
            annotation_text="selected", annotation_position="top",
            fillcolor="green", opacity=0.2, line_width=0)


        fig.update_layout(
            yaxis_title="log(#characters)",
            yaxis=dict(type="log"),
            xaxis=dict(range=[0, max_screentime]),
            showlegend=False,
            height=150,
            margin=dict(l=1, r=1, t=1, b=1),
            bargap=0.05,
        )

        return fig

zoom_level = 100
fit_mode = "w"
app = App(app_ui, server, static_assets=static_dir)
