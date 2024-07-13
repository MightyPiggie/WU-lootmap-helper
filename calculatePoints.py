import numpy as np
def generate_circle_coordinates_within(X, Y, r):
    """
    Generates coordinates for all points within a circle with center (X, Y) and radius r.

    Parameters:
    X (float): X-coordinate of the center.
    Y (float): Y-coordinate of the center.
    r (float): Radius of the circle.

    Returns:
    numpy.ndarray: Array of shape (num_points, 2) containing the coordinates.
    """
    # Create a grid of points
    x_range = np.arange(X - r, X + r + 1)
    y_range = np.arange(Y - r, Y + r + 1)
    
    x_grid, y_grid = np.meshgrid(x_range, y_range)
    
    # Flatten the grids to create coordinate pairs
    x_grid_flat = x_grid.flatten()
    y_grid_flat = y_grid.flatten()
    
    # Calculate distance from the center and check if within the circle
    mask = (x_grid_flat - X)**2 + (y_grid_flat - Y)**2 <= r**2
    
    # Get all points within the circle
    x_within = x_grid_flat[mask]
    y_within = y_grid_flat[mask]
    
    # Combine x and y coordinates into a single array
    coordinates_within = np.vstack((x_within, y_within)).T
    
    return coordinates_within

def filter_coordinates_by_angle(coordinates, X, Y, angle_min, angle_max):
    """
    Filters coordinates by a specific angular range relative to the center (X, Y).

    Parameters:
    coordinates (numpy.ndarray): Array of shape (num_points, 2) containing the coordinates.
    X (float): X-coordinate of the center.
    Y (float): Y-coordinate of the center.
    angle_min (float): Minimum angle in degrees.
    angle_max (float): Maximum angle in degrees.

    Returns:
    numpy.ndarray: Filtered array of coordinates within the specified angular range.
    """
    # Convert angles to radians
    # print("angle_min", angle_min, "angle_max", angle_max)
    angle_min_rad = np.deg2rad(angle_min)
    angle_max_rad = np.deg2rad(angle_max)
    # print("angle_min_rad", angle_min_rad, "angle_max_rad", angle_max_rad)
    
    # Calculate the angles of each point relative to the center
    angles = np.arctan2(Y - coordinates[:, 1], coordinates[:, 0] - X)
    
    # Normalize angles to range [0, 2*pi)
    angles = np.mod(angles, 2 * np.pi)
    
    # Create mask for the angular range
    if angle_min_rad < angle_max_rad:
        mask_angle = (angles >= angle_min_rad) & (angles <= angle_max_rad)
    else:
        # Handle the case where the angular range crosses the 0 radians line
        mask_angle = (angles >= angle_min_rad) | (angles <= angle_max_rad)
    
    # Apply mask
    coordinates_within_angle = coordinates[mask_angle]
    
    return coordinates_within_angle
# Reduce the given coordinates to the ones that are within the new circle and within the specified angular range

def reduce_coordinates_by_angle(coordinates, X, Y, r, angle_min, angle_max):
    """
    Reduces the given coordinates to the ones that are within the new circle and within the specified angular range.

    Parameters:
    coordinates (numpy.ndarray): Array of shape (num_points, 2) containing the coordinates.
    X (float): X-coordinate of the center.
    Y (float): Y-coordinate of the center.
    r (float): Radius of the circle.
    angle_min (float): Minimum angle in degrees.
    angle_max (float): Maximum angle in degrees.

    Returns:
    numpy.ndarray: Reduced array of coordinates within the new circle and angular range.
    """
    # Generate all coordinates within the new circle
    coordinates_within = generate_circle_coordinates_within(X, Y, r)
    
    # Filter coordinates by the specified angular range
    coordinates_within_angle = filter_coordinates_by_angle(coordinates_within, X, Y, angle_min, angle_max)
    
    # Reduce the given coordinates to the ones within the new circle and angular range
    nrows, ncols = coordinates_within_angle.shape
    dtype={'names':['f{}'.format(i) for i in range(ncols)],
           'formats':ncols * [coordinates_within_angle.dtype]}
    coordinates_within_angle_reduced = np.intersect1d(coordinates_within_angle.view(dtype), coordinates.view(dtype))
    coordinates_within_angle_reduced = coordinates_within_angle_reduced.view(coordinates_within_angle.dtype).reshape(-1, ncols)
    
    return coordinates_within_angle_reduced

def filter_coordinates_by_min_distance(coordinates, X, Y, min_distance):
    """
    Reduces the given coordinates to the ones that are at least the minimum distance away from the center.

    Parameters:
    coordinates (numpy.ndarray): Array of shape (num_points, 2) containing the coordinates.
    X (float): X-coordinate of the center.
    Y (float): Y-coordinate of the center.
    min_distance (float): Minimum distance from the center.

    Returns:
    numpy.ndarray: Reduced array of coordinates at least the minimum distance away from the center.
    """
    # Calculate the distances of each point from the center
    distances = np.sqrt((coordinates[:, 0] - X)**2 + (coordinates[:, 1] - Y)**2)
    
    # Create mask for points that are at least the minimum distance away
    mask_distance = distances >= min_distance
    
    # Apply mask
    coordinates_min_distance = coordinates[mask_distance]
    
    return coordinates_min_distance

def filter_coordinates_outside_range(coordinates):
    """
    Filters coordinates that are outside the specified range.

    Parameters:
    coordinates (numpy.ndarray): Array of shape (num_points, 2) containing the coordinates.

    Returns:
    numpy.ndarray: Filtered array of coordinates that are outside the specified range.
    """
    # Define the range of coordinates to keep
    x_min, x_max = 0, 4096
    y_min, y_max = 0, 4096
    
    # Create mask for points that are within the specified range
    mask_range = (coordinates[:, 0] >= x_min) & (coordinates[:, 0] <= x_max) & (coordinates[:, 1] >= y_min) & (coordinates[:, 1] <= y_max)
    
    # Apply mask
    coordinates_within_range = coordinates[mask_range]
    return coordinates_within_range
