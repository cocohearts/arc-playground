import numpy as np
from scipy.ndimage import label
from skimage.draw import line
from skimage.transform import resize
from symmetric_patterns import symmetric_pattern

# Define grid size range
MIN_SIZE = 6
MAX_SIZE = 15

# Create a grid with symmetric patterns or connected components
# def create_patterned_grid(size=None):
#     if size is None:
#         size = np.random.randint(MIN_SIZE, MAX_SIZE)
#     grid = np.zeros((size, size), dtype=int)
    
#     # Add symmetric pattern or connected components
#     pattern_choice = np.random.choice(['symmetric', 'components'])
#     if pattern_choice == 'symmetric':
#         symmetric_pattern(grid)
#     else:
#         add_connected_components(grid)
#     return grid

def create_random_grid(size=None):
    if size is None:
        size = np.random.randint(MIN_SIZE, MAX_SIZE)

    grid = np.zeros((size, size), dtype=int)
    
    # Always add connected components
    grid = add_connected_components(grid)
    return grid

# Add connected components using flood fill
def add_connected_components(grid):
    size = grid.shape[0]
    num_components = np.random.randint(2, 5)
    colors = np.random.choice(range(0, 8), num_components)
    for color in colors:
        component_size = np.random.randint(2, size // 2)
        x, y = np.random.randint(0, size, 2)
        grid = flood_fill_random_shape(grid, (x, y), color, component_size)
    return grid

def flood_fill_random_shape(grid, start, fill_value, max_size):
    size = grid.shape[0]
    filled_grid = grid.copy()
    to_fill = [start]
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    filled = 0
    
    while to_fill and filled < max_size:
        x, y = to_fill.pop()
        if 0 <= x < size and 0 <= y < size and filled_grid[x, y] == 0:
            filled_grid[x, y] = fill_value
            filled += 1
            np.random.shuffle(directions)  # Randomize direction for irregular shapes
            for dx, dy in directions:
                to_fill.append((x + dx, y + dy))
    return filled_grid

# Color Transformations
def recolor_grid(grid, old_color, new_color):
    transformed_grid = grid.copy()
    transformed_grid[transformed_grid == old_color] = new_color
    return transformed_grid

def recolor_condition(grid, condition, new_color):
    transformed_grid = grid.copy()
    transformed_grid[condition(transformed_grid)] = new_color
    return transformed_grid

# Shape Transformations
def resize_shape(grid, shape_value, scale):
    # Scaling the size of the shape according to the provided scale factor
    scaling_mask = np.kron(grid == shape_value, np.ones(scale))
    print("scaling mask: ", scaling_mask)
    print("grid: ", grid)
    
    # Cropping the scaled mask to the bounding box of true values
    true_positions = np.argwhere(scaling_mask)
    if true_positions.size > 0:
        min_y, min_x = true_positions.min(axis=0)
        max_y, max_x = true_positions.max(axis=0)
        cropped_mask = scaling_mask[min_y:max_y+1, min_x:max_x+1]
    else:
        cropped_mask = np.zeros_like(grid)
    
    # Creating a new grid to place the cropped mask
    transformed_grid = np.zeros_like(cropped_mask)
    
    # Calculating the dimensions to fit the cropped mask onto the grid
    fit_height = min(cropped_mask.shape[0], transformed_grid.shape[0])
    fit_width = min(cropped_mask.shape[1], transformed_grid.shape[1])
    
    # Adjusting the dimensions of the new grid to match the original grid size
    transformed_grid = np.zeros_like(grid)
    
    # Placing the cropped mask into a random position on the new grid
    max_y_offset = transformed_grid.shape[0] - fit_height
    max_x_offset = transformed_grid.shape[1] - fit_width
    random_y_offset = np.random.randint(0, max_y_offset + 1)
    random_x_offset = np.random.randint(0, max_x_offset + 1)
    transformed_grid[random_y_offset:random_y_offset + fit_height, random_x_offset:random_x_offset + fit_width] = shape_value * cropped_mask[:fit_height, :fit_width]
    return transformed_grid

def rotate_shape(grid, shape_value):
    transformed_grid = np.zeros_like(grid)
    shape_mask = (grid == shape_value)
    rotated = np.rot90(shape_mask)
    transformed_grid[:rotated.shape[0], :rotated.shape[1]] = rotated
    transformed_grid[rotated] = shape_value
    return transformed_grid

def reflect_shape(grid, shape_value, axis=0):
    transformed_grid = np.zeros_like(grid)
    shape_mask = (grid == shape_value)
    reflected = np.flip(shape_mask, axis=axis)
    transformed_grid[:reflected.shape[0], :reflected.shape[1]] = reflected
    transformed_grid[reflected] = shape_value
    return transformed_grid

def translate_shape(grid, shape_value, offset):
    transformed_grid = np.zeros_like(grid)
    shape_mask = (grid == shape_value)
    translation = np.roll(shape_mask, offset, axis=(0, 1))
    transformed_grid[:translation.shape[0], :translation.shape[1]] = translation
    transformed_grid[translation] = shape_value
    return transformed_grid

# Pattern Matching
def identify_pattern(grid, pattern_value):
    return (grid == pattern_value)

# Grid Manipulation
def split_grid(grid, num_splits):
    return np.array_split(grid, num_splits, axis=0), np.array_split(grid, num_splits, axis=1)

def concatenate_grids(grid1, grid2, axis=0):
    return np.concatenate((grid1, grid2), axis=axis)

def expand_grid(grid, new_shape):
    expanded = np.zeros(new_shape)
    min_dim = min(grid.shape[0], new_shape[0]), min(grid.shape[1], new_shape[1])
    expanded[:min_dim[0], :min_dim[1]] = grid[:min_dim[0], :min_dim[1]]
    return expanded

# Line Operations
def draw_line(grid, start, end, value):
    transformed_grid = grid.copy()
    rr, cc = line(start[0], start[1], end[0], end[1])
    transformed_grid[rr, cc] = value
    return transformed_grid

# Object Counting
def count_objects(grid, obj):
    return np.sum(grid == obj)

def presence_of_object(grid, obj):
    return obj in grid

# Boolean Logic
def apply_logical_and(grid1, grid2):
    return np.logical_and(grid1, grid2)

def apply_logical_or(grid1, grid2):
    return np.logical_or(grid1, grid2)

def apply_logical_not(grid):
    return np.logical_not(grid)

# Filter Operations
def filter_grid(grid, condition):
    return grid[condition(grid)]

# Boundary Detection
def detect_boundaries(grid):
    gx, gy = np.gradient(grid.astype(float))
    return np.sqrt(gx**2 + gy**2)

# Region Labeling
def label_regions(grid):
    labeled, num_features = label(grid)
    return labeled, num_features

def apply_transformation_to_component(grid, component_value, transformation):
    # Create a mask for the component
    component_mask = (grid == component_value)
    
    # Extract the component grid
    component_grid = np.zeros_like(grid)
    component_grid[component_mask] = component_value
    
    # Apply transformation
    if transformation.__name__ == 'resize_shape':
        scale_x = int(np.random.uniform(2, 3))
        scale_y = int(np.random.uniform(2, 3))
        print((scale_x, scale_y))
        transformed_component_grid = transformation(component_grid, component_value, (scale_x, scale_y))
    elif transformation.__name__ == 'recolor_grid':
        new_color = int(np.random.uniform(0, 8))
        transformed_component_grid = transformation(component_grid, component_value, new_color)
    else:
        transformed_component_grid = transformation(component_grid, component_value)
    
    # Merge the transformed component back into the original grid
    grid[component_mask] = 0  # Clear the original component in the grid
    grid += transformed_component_grid  # Add the transformed component
    return grid

# Conditional Operations
def conditional_transformation(grid, condition, transformation):
    transformed_grid = grid.copy()
    condition_mask = condition(transformed_grid)
    transformed_grid[condition_mask] = transformation(transformed_grid[condition_mask])
    return transformed_grid

# Flood Fill (connected component labeling)
def flood_fill(grid, start, fill_value):
    filled_grid = grid.copy()
    target_value = grid[start[0], start[1]]
    def flood_fill_rec(x, y):
        if filled_grid[x, y] == target_value:
            filled_grid[x, y] = fill_value
            if x > 0: flood_fill_rec(x - 1, y)
            if x < filled_grid.shape[0] - 1: flood_fill_rec(x + 1, y)
            if y > 0: flood_fill_rec(x, y - 1)
            if y < filled_grid.shape[1] - 1: flood_fill_rec(x, y + 1)
    flood_fill_rec(start[0], start[1])
    return filled_grid

# Example usage
if __name__ == "__main__":
    grid = create_patterned_grid()
    print("Original Patterned Grid:\n", grid)
    
    grid = recolor_grid(grid, 1, 5)
    print("Recolored Grid:\n", grid)
    
    shape_value = 5
    grid = rotate_shape(grid, shape_value)
    print("Rotated Shape Grid:\n", grid)
    
    # Add more transformations and debug here

def get_unique_colors(grid):
    """
    Returns a set of unique colors present in the grid, excluding the color 0.
    """
    unique_colors = set(np.unique(grid))
    unique_colors.discard(0)  # Remove the color 0 if it exists
    return unique_colors
