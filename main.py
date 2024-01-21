import json
import os
import random
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from matplotlib import pyplot as plt, patches

WIDTH = 640
HEIGHT = 640
SAVE_DIR = r"X:\skolicka\diplomka\data\generate_datasets"


def generate_polygon():
    """Generate random polygon in the image."""
    num_points = np.random.randint(3, 7)
    x_points = np.random.randint(0, WIDTH, num_points)
    y_points = np.random.randint(0, HEIGHT, num_points)
    polygon = list(zip(x_points, y_points))
    return polygon


def generate_polygon_background():
    """Generate the background filled with polygons."""
    image = Image.new('RGB', (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    num_polygons = np.random.randint(5, 15)

    for _ in range(num_polygons):
        polygon = generate_polygon()
        # Ensure the color is not black
        while True:
            color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
            if color != (0, 0, 0):
                break
        draw.polygon(polygon, fill=color)

    return image


def generate_rotated_random_number(font_size_range=(50, 150)):
    """Generate a rotated random number with a random font size and return its image, bounding box, and number."""
    number = str(random.randint(0, 9))
    font_size = random.randint(*font_size_range)
    font = ImageFont.truetype("arial.ttf", font_size)

    # Calculate text size
    bbox = font.getbbox(number)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_height = 2 * text_height
    # Create an image for the text
    text_image = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), number, font=font, fill="black")

    # Rotate the text
    angle = random.randint(0, 360)

    rotated_text_image = text_image.rotate(angle, resample=Image.BICUBIC, expand=True)

    # Calculate bounding box
    bbox = rotated_text_image.getbbox()
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x_center = bbox[0] + width / 2
    y_center = bbox[1] + height / 2

    return rotated_text_image, (x_center, y_center, width, height, angle), number




def overlay_rotated_numbers_on_background(background, num_numbers=3):
    """Overlay rotated random numbers on the background and return the image and annotations."""
    bg_copy = background.copy()
    annotations = []

    for _ in range(num_numbers):
        text_image, (x_center, y_center, width, height, angle), number = generate_rotated_random_number()

        # Position the text randomly with margins
        x = random.randint(20, WIDTH - width - 20)
        y = random.randint(20, HEIGHT - height - 20)

        # Check for collision with existing numbers
        collision = any(check_collision((x, y, x + width, y + height), existing_box) for existing_box in annotations)
        if collision:
            continue  # Skip this number and try a new one

        bg_copy.paste(text_image, (x, y), text_image)
        annotations.append((number, x + x_center, y + y_center, width, height, angle))

    return bg_copy, annotations

def check_collision(box1, box2):
    # Ensure that all values are numeric
    box1 = [float(coord) for coord in box1]
    box2 = [float(coord) for coord in box2]

    return not (box1[2] < box2[0] or box1[0] > box2[2] or box1[3] < box2[1] or box1[1] > box2[3])


def rotated_rect_coordinates(x_center, y_center, width, height, angle):
    """Get the coordinates of a rotated rectangle."""
    # Get the corners of the rectangle relative to its center
    corners = [
        (-width/2, -height/2),
        (width/2, -height/2),
        (width/2, height/2),
        (-width/2, height/2)
    ]

    # Rotate the corners by the given angle
    rotated_corners = [rotate_point(x, y, angle) for x, y in corners]

    # Move the rotated corners back to the original position
    rotated_corners = [(x + x_center, y + y_center) for x, y in rotated_corners]

    return rotated_corners



def get_rectangle_corners(x_center, y_center, width, height):
    """Get the corners of a rectangle."""
    half_width = width / 2
    half_height = height / 2

    return [
        (x_center - half_width, y_center - half_height),
        (x_center + half_width, y_center - half_height),
        (x_center + half_width, y_center + half_height),
        (x_center - half_width, y_center + half_height)
    ]


def rotate_point(x, y, angle):
    """Rotate a point around the origin by a given angle (in degrees)."""
    theta = np.radians(-angle)  # Změna znaménka u úhlu
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return x_new, y_new



def draw_rotated_bounding_boxes(image, annotations):
    """Draw bounding boxes on the image based on the rotated number annotations with correct rotation."""
    fig, ax = plt.subplots(1)
    ax.imshow(image)

    for ann in annotations:
        number, x_center, y_center, width, height, angle = ann
        # Get rotated rectangle coordinates
        coordinates = rotated_rect_coordinates(x_center, y_center, width, height, angle)

        polygon = patches.Polygon(coordinates, edgecolor='r', facecolor='none')
        ax.add_patch(polygon)

    plt.axis('off')
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)

    # Generate and save 250 images
    for i in range(250):

        # Generate a new background and overlay 8 rotated numbers on it
        new_background = generate_polygon_background()
        num_numbers = random.randint(2, 5)
        new_image_with_rotated_numbers, annotations = overlay_rotated_numbers_on_background(new_background, num_numbers)

        # Save the generated image
        image_file_path = os.path.join(SAVE_DIR, f"image_{i + 1}.png")
        new_image_with_rotated_numbers.save(image_file_path)

        # Save the annotations as a JSON file
        # Save the annotations in the desired format
        annotations_file_path = os.path.join(SAVE_DIR, f"image_{i + 1}.txt")
        with open(annotations_file_path, 'w') as f:
            for ann in annotations:
                number, x_center, y_center, width, height, angle = ann
                # Normalizace souřadnic a omezení na rozsah [0, 1]
                x_center = min(max(x_center / WIDTH, 0), 1)
                y_center = min(max(y_center / HEIGHT, 0), 1)
                width = min(max(width / WIDTH, 0), 1)
                height = min(max(height / HEIGHT, 0), 1)

                # Přepsání hodnoty úhlu
                angle = angle / 360
                line = f"{number} {x_center} {y_center} {width} {height} {angle}\n"
                f.write(line)

    print(f"Generated 250 images and annotations in {SAVE_DIR}")




