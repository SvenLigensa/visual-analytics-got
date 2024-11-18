import plotly.express as px
from scipy.cluster.hierarchy import linkage, leaves_list
import pandas as pd

def create_heatmap(time_data, threshold):
    """
    Create a heatmap visualization of character screentime.
    
    Args:
        time_data (pd.DataFrame): DataFrame containing screentime data
        threshold (list): [min, max] screentime in minutes to include character
        
    Returns:
        plotly.graph_objects.Figure: The configured heatmap figure
    """
    # Calculate total screentime for each character (in minutes)
    total_screentime = time_data.sum(axis=1) / 60

    min_threshold, max_threshold = threshold
    filtered_chars = total_screentime[
        (total_screentime >= min_threshold) & 
        (total_screentime <= max_threshold)
    ].index

    filtered_data = time_data.loc[filtered_chars] / 60  # Convert seconds to minutes

    # Cluster the filtered data
    filtered_data = cluster_data(filtered_data)

    # Create heatmap using plotly express
    fig = px.imshow(
        filtered_data,
        aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(x="Episode", y="Character", color="Screentime (minutes)"),
    )

    # Define season lengths
    season_lengths = [10, 10, 10, 10, 10, 10, 7, 6]  # Episodes per season
    season_positions = []
    current_pos = 0
    
    # Calculate center position for each season
    for length in season_lengths:
        season_positions.append(current_pos + (length - 1) / 2)
        current_pos += length

    # Create season labels
    season_labels = [f"Season {i+1}" for i in range(len(season_lengths))]

    # Calculate season boundaries for vertical lines
    season_boundaries = []
    current_pos = -0.5  # Start at -0.5 to place line between episodes
    for length in season_lengths:
        current_pos += length
        season_boundaries.append(current_pos)
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Character",
        height=len(filtered_chars) * 25 + 250,
        xaxis=dict(
            ticktext=season_labels,
            tickvals=season_positions,
            tickangle=0,
            tickmode='array',
        ),
        title=dict(
            text=f"{len(filtered_chars)} Characters with {min_threshold} - {max_threshold} minutes of total screentime",
            xanchor="center",
            x=0.5,
        ),
        coloraxis=dict(
            colorbar=dict(
                y=1,
                thickness=25,
                orientation='h',
                yanchor="bottom",
                xanchor="center",
                ticks="inside",
                bgcolor='rgba(255,255,255,0.9)',
            )
        )
    )

    # Add hover template
    fig.update_traces(
        hovertemplate="Character: %{y}<br>Episode: %{x}<br>Screentime: %{z:.1f} minutes<extra></extra>"
    )

    # Add vertical lines between seasons
    for boundary in season_boundaries[:-1]:  # Skip the last boundary as it's the end
        fig.add_vline(
            x=boundary, 
            line_width=1, 
            line_dash="solid", 
            line_color="rgba(0, 0, 0, 0.3)"
        )

    return fig


def cluster_data(data):
    """
    Reorder the rows of a dataframe based on hierarchical clustering.
    
    Args:
        data: pandas DataFrame where rows are items and columns are features
    
    Returns:
        DataFrame with rows reordered according to hierarchical clustering
    """
    # Check if there are the data input is empty or has only one row
    if data.empty or data.shape[0] == 1:
        return data

    # Remove rows that contain all zeros
    non_zero_mask = (data.sum(axis=1) > 0)
    if non_zero_mask.sum() == 0:  # If all rows are zeros
        return data
    
    data_to_cluster = data[non_zero_mask]
    zero_data = data[~non_zero_mask]

    normalized_data = data_to_cluster.copy()
    # Normalize columns to sum to 1 (only where column sum is non-zero)
    col_sums = normalized_data.sum(axis=0)
    normalized_data = normalized_data.loc[:, col_sums > 0]  # Remove all-zero columns
    normalized_data = normalized_data.div(normalized_data.sum(axis=0), axis=1)
    # Normalize rows to sum to 1
    normalized_data = normalized_data.div(normalized_data.sum(axis=1), axis=0)
    
    # Perform hierarchical clustering
    features = normalized_data.values
    linkage_matrix = linkage(features, method='ward', optimal_ordering=True)
    
    # Get the leaf ordering from the linkage matrix
    leaf_order = leaves_list(linkage_matrix)

    # Reorder the non-zero data according to the clustering
    clustered_data = data_to_cluster.iloc[leaf_order]
    
    # Append the zero rows at the end
    if not zero_data.empty:
        return pd.concat([clustered_data, zero_data])
    return clustered_data
