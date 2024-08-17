import numpy as np
from skimage.draw import line

def symmetric_pattern(grid):
    size = grid.shape[0]
    half = size // 2
    colors = np.random.choice(range(1, 10), half * half)
    pattern = colors.reshape((half, half))
    grid[:half, :half] = pattern
    grid[:half, half:] = np.flip(pattern, axis=1)
    grid[half:, :half] = np.flip(pattern, axis=0)
    grid[half:, half:] = np.flip(pattern, axis=(0, 1))
    return grid