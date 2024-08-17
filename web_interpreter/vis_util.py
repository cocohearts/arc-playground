from PIL import Image, ImageDraw


def plot_one_pil(input_matrix):
    # Define the colors corresponding to the indices
    colors = [
        "#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00",
        "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25"
    ]

    # Define the size of each cell
    cell_size = 20
    rows, cols = len(input_matrix), len(input_matrix[0])
    width, height = cols * cell_size, rows * cell_size

    # Create a new image with a white background
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Draw the cells
    for i in range(rows):
        for j in range(cols):
            color = colors[input_matrix[i][j]]
            draw.rectangle(
                [j * cell_size, i * cell_size, (j + 1) * cell_size, (i + 1) * cell_size],
                fill=color
            )

    # Draw grid lines
    for i in range(rows + 1):
        draw.line([0, i * cell_size, width, i * cell_size], fill="lightgrey")
    for j in range(cols + 1):
        draw.line([j * cell_size, 0, j * cell_size, height], fill="lightgrey")

    return img
