# Color Detection Application

## Description
This is a simple color detection tool built using Python, `tkinter`, and `PIL` (Pillow). It allows users to load an image and click on any part of the image to get the RGB and HEX values of the color at the clicked position. Additionally, it provides the closest color name from a predefined CSV file containing a list of color names and their corresponding RGB values.

## Key Features
- Load and display an image on a canvas.
- Detect and display the RGB and HEX values of the clicked pixel.
- Show the closest color name based on a predefined list.
- Resize the image to fit within the application window while maintaining aspect ratio.

## Requirements
- Python 3.x
- OpenCV
- Pandas
- Pillow
- tkinter (comes with Python standard library)

## Installation
1. Ensure you have Python 3.x installed on your system.
2. Install the required libraries using pip:
   ```sh
   pip install opencv-python pandas pillow
