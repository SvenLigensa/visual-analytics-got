from scipy.cluster.hierarchy import linkage, leaves_list

def cluster_data(data):
    """
    Reorder the rows of a dataframe based on hierarchical clustering.
    
    Args:
        data: pandas DataFrame where rows are items and columns are features
    
    Returns:
        DataFrame with rows reordered according to hierarchical clustering
    """
    # Normalize columns to sum to 1
    normalized_data = data.copy()
    # normalized_data = normalized_data.div(normalized_data.sum(axis=0), axis=1)
    # Normalize rows to sum to 1
    normalized_data = normalized_data.div(normalized_data.sum(axis=1), axis=0)
    
    # Perform hierarchical clustering
    features = normalized_data.values
    linkage_matrix = linkage(features, method='ward')
    
    # Get the leaf ordering from the linkage matrix
    leaf_order = leaves_list(linkage_matrix)

    # Reorder the original data according to the clustering
    return data.iloc[leaf_order]
