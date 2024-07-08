import cv2
import pandas as pd
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

# Function to open and display an image
def open_image():
    global img_path, img, tk_img, img_resized, img_pil, canvas_img
    img_path = filedialog.askopenfilename()
    if img_path:
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Resize image to fit within the canvas while maintaining aspect ratio
        img_pil.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
        img_resized = img_pil
        tk_img = ImageTk.PhotoImage(img_resized)
        canvas_img = canvas.create_image(0, 0, anchor=NW, image=tk_img)

# Function to get the closest color name from the CSV
def get_color_name(R, G, B):
    minimum = 10000
    cname = ""
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

# Function to handle click events on the image
def on_click(event):
    global b, g, r, x_pos, y_pos, img_resized, img
    x_pos = event.x
    y_pos = event.y

    # Adjust coordinates according to the resized image
    width_ratio = img.shape[1] / img_resized.width
    height_ratio = img.shape[0] / img_resized.height
    x_adjusted = int(x_pos * width_ratio)
    y_adjusted = int(y_pos * height_ratio)

    b, g, r = img[y_adjusted, x_adjusted]
    b = int(b)
    g = int(g)
    r = int(r)
    update_color_info()

# Function to update and display color information
def update_color_info():
    global r, g, b
    color_name = get_color_name(r, g, b)
    hex_value = f'#{r:02x}{g:02x}{b:02x}'.upper()
    rgb_value = f'RGB: ({r}, {g}, {b})'

    color_name_label.config(text=color_name)
    hex_label.config(text=hex_value)
    rgb_label.config(text=rgb_value)
    color_display.config(bg=hex_value)

# Initialize tkinter window
root = Tk()
root.title("Color Detection App")
root.geometry("800x600")

# Load CSV file
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Add canvas to display image
canvas = Canvas(root, width=800, height=400)
canvas.pack()

# Add button to open image
btn = Button(root, text="Open Image", command=open_image)
btn.pack(side=TOP, pady=10)

# Labels to display color information
color_name_label = Label(root, text="Color Name:", font=('Arial', 14))
color_name_label.pack()

hex_label = Label(root, text="Hex Value:", font=('Arial', 14))
hex_label.pack()

rgb_label = Label(root, text="RGB Value:", font=('Arial', 14))
rgb_label.pack()

color_display = Label(root, width=20, height=2, font=('Arial', 14))
color_display.pack(pady=10)

# Bind mouse click event to the canvas
canvas.bind("<Button-1>", on_click)

root.mainloop()
