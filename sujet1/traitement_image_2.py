import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
import PIL.Image as pim

#---------------------------------------------
# Loading and converting the Excel file to a numpy array
#---------------------------------------------

# If Excel file:
file_path = r'C:\Users\Guillaume\IG\stage1A\sujet1\data_image.xlsx'
data = pd.read_excel(file_path, header=None).to_numpy()

# If image:
# data = np.array(pim.open())

# Cropping the image if necessary
x_crop_right = 9
x_crop_left = 0 
y_crop_top = 9  
y_crop_bottom = 9 
data_cropped = data[y_crop_top:-y_crop_bottom, x_crop_left:-x_crop_right] 

#---------------------------------------------
# Function to plot original and cropped images
#---------------------------------------------

def plot_images(data: np.ndarray, data_cropped: np.ndarray) -> None:
    """Plot the original image and the cropped image."""
    plt.imshow(data, cmap='gray') 
    plt.colorbar()
    plt.title("Original Image")  
    plt.show()

    plt.imshow(data_cropped, cmap='gray') 
    plt.colorbar()
    plt.title("Cropped Image")  
    plt.show()

#---------------------------------------------
# Function to binarize image and find active pixels
#---------------------------------------------

def binarize_and_find_pixels(image: np.ndarray, threshold: int) -> tuple[np.ndarray, np.ndarray]:  
    """Binarize the image based on threshold and find active pixels."""
    binary_image = image > threshold
    return binary_image, np.argwhere(binary_image)

#---------------------------------------------
# Function to show active zones in green
#---------------------------------------------

def show_active_zones(image: np.ndarray, threshold: int) -> None:
    """Show active zones in green on the image."""
    active_pixels = binarize_and_find_pixels(image, threshold)[1]
    plt.imshow(image, cmap='gray')
    for active_pixel in active_pixels:
        plt.plot(active_pixel[1], active_pixel[0], 'go', markersize=1)
    plt.title(f"Active zones highlighted with a {threshold} threshold")
    plt.show()

#---------------------------------------------
# Function to show contours of active zones
#---------------------------------------------

def show_contours(image: np.ndarray, threshold: int) -> None:
    """Show contours of active zones on the image."""
    binary_image = binarize_and_find_pixels(image, threshold)[0]
    contours = measure.find_contours(binary_image, 0.5)
    plt.imshow(image, cmap='gray')
    for contour in contours:
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2, color='green')
    plt.title(f"Contours of active zones for a {threshold} threshold")
    plt.show()

#---------------------------------------------
# Function to plot a grid on the image
#---------------------------------------------

def plot_grid(image: np.ndarray, grid_size: tuple[int, int]) -> None: 
    """Plot a grid on the image based on the specified size."""
    rows, cols = grid_size
    height, width = image.shape

    plt.imshow(image, cmap='gray')

    for i in range(1, cols):
        x = i * (width / cols)
        plt.axvline(x=x, color='r', linestyle='solid', linewidth=0.5)
        plt.text(x - (width / cols) / 2, height + 10, str(i), color='red', fontsize=8, ha='center', va='center')

    for j in range(1, rows):
        y = j * (height / rows)
        plt.axhline(y=y, color='r', linestyle='solid', linewidth=0.5)
        plt.text(-10, y - (height / rows) / 2, str(j), color='red', fontsize=8, ha='center', va='center')

    plt.title(f"Grid of ({rows}x{cols})")
    plt.show()

#---------------------------------------------
# Function to find coordinates of most active zones among the 1024 zones
#---------------------------------------------

def find_most_active_zones(image: np.ndarray, threshold: int, grid_size: tuple[int, int]) -> list[tuple[tuple[int, int], int]]:
    """Find and return coordinates of most active zones among the 1024 zones."""
    active_pixels = binarize_and_find_pixels(image, threshold)[1]

    height, width = image.shape
    rows, cols = grid_size
    
    cell_height = height / rows
    cell_width = width / cols
    
    active_zones = {}

    for pixel in active_pixels:
        row_index = int(pixel[0] // cell_height) + 1
        col_index = int(pixel[1] // cell_width) + 1
        grid_cell = (row_index, col_index)
        
        if grid_cell in active_zones:
            active_zones[grid_cell] += 1
        else:
            active_zones[grid_cell] = 1
    
    sorted_active_zones = sorted(active_zones.items(), key=lambda item: item[1], reverse=True)
    
    return sorted_active_zones

#---------------------------------------------
# Function to count number of active pixels in one of the 1024 zones
#---------------------------------------------

def count_active_pixels_in_zone(image: np.ndarray, grid_size: tuple[int, int], row: int, col: int) -> int:
    """Count number of active pixels in a specified zone of the grid."""
    active_pixels = binarize_and_find_pixels(image, threshold)[1]

    image_height, image_width = image.shape
    grid_rows, grid_cols = grid_size
    
    cell_height = image_height / grid_rows
    cell_width = image_width / grid_cols
    
    row_start = (row - 1) * cell_height
    row_end = row * cell_height
    col_start = (col - 1) * cell_width
    col_end = col * cell_width
    
    count = 0
    for pixel in active_pixels:
        if row_start <= pixel[0] < row_end and col_start <= pixel[1] < col_end:
            count += 1
    
    return count

#---------------------------------------------
# Function to calculate percentage of active pixels in the image
#---------------------------------------------

def count_active_pixels_in_image(image: np.ndarray, threshold: int) -> None:
    """Calculate and print the percentage of active pixels in the image."""
    binary_image = binarize_and_find_pixels(image, threshold)[0]
    percent_active = np.sum(binary_image) / binary_image.size * 100
    print(f"Percentage of active pixels in the image: {percent_active:.2f}%") 

#---------------------------------------------
# Function calls
#---------------------------------------------

threshold = 2.2
grid_size = (32, 32) # For 1024 zones

show_active_zones(data_cropped, threshold)
show_contours(data_cropped, threshold)
sorted_active_zones = find_most_active_zones(data_cropped, threshold, grid_size)

print("Most active zones in descending order within the grid:")
for zone, count in sorted_active_zones:
    print(f"\tZone {zone} : {count} active pixels")

plot_grid(data_cropped, grid_size)

# To know how many pixels there is in the [row,col] cell
row, col = 3, 3
count = count_active_pixels_in_zone(data_cropped, grid_size, row, col)
print(f"\nNumber of active pixels in zone ({row}, {col}): {count}")