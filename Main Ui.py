import cv2
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from io import BytesIO

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
        
        # Call dominant color finding function
        dominant_colors()

# Function for dominant colors
def dominant_colors():
    global img_path
    
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
    img_reshaped = img_rgb.reshape((-1, 3)) 

    k = 5  
    kmeans = KMeans(n_clusters=k)  # Initialize KMeans
    kmeans.fit(img_reshaped)  # Fit KMeans
    dominant_colors = kmeans.cluster_centers_.astype(int)  # Get dominant colors

    labels = kmeans.labels_  # Get cluster labels for each pixel
    label_counts = np.bincount(labels)  # Count pixels in each cluster
    total_count = len(labels)  # Tot pixels

    #calculate percentage
    percentages = [count / total_count * 100 for count in label_counts]

    # dominant color display
    dominant_colors_img = np.zeros((100, 100 * k, 3), dtype=int)
    for i in range(k):
        dominant_colors_img[:, i * 100:(i + 1) * 100, :] = dominant_colors[i]

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.imshow(dominant_colors_img, aspect='auto')
    ax.set_title('Dominant Colors')
    ax.axis('off')

    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)

    dominant_colors_image = Image.open(buf) 
    tk_dominant_colors_image = ImageTk.PhotoImage(dominant_colors_image)

    dominant_colors_label.config(image=tk_dominant_colors_image)
    dominant_colors_label.image = tk_dominant_colors_image

    # Display color names and percentages
    color_info = ""
    for i in range(k):
        color_name = get_color_name(*dominant_colors[i])  
        percentage = percentages[i] 
        color_info += f" {color_name}: {percentage:.2f}, "  # disply format( one line)
    
    color_info_label.config(text=color_info)


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
root.iconbitmap('Color Vista.ico') 
root.geometry("1000x750")

# background color
bg_color = '#FAF9F6'
root.configure(bg=bg_color)

# Load CSV file
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Add canvas to display image
canvas = Canvas(root, width=300, height=300, bg=bg_color, highlightthickness=0)
canvas.pack()

# Add button to open image
btn_open = Button(root, text="Open Image", command=open_image)
btn_open.pack(side=TOP, pady=10)

# Labels to display color information
color_name_label = Label(root, text="Color Name:", font=('Arial', 14),bg=bg_color, bd=0)
color_name_label.pack()

hex_label = Label(root, text="Hex Value:", font=('Arial', 14), bg=bg_color, bd=0)
hex_label.pack()

rgb_label = Label(root, text="RGB Value:", font=('Arial', 14), bg=bg_color, bd=0)
rgb_label.pack()

color_display = Label(root, width=20, height=2, font=('Arial', 14), bg=bg_color, bd=0)
color_display.pack(pady=10)

# Add button to display dominant colors
btn_colors = Button(root, text="Refresh Dominant Colors", command=dominant_colors)
btn_colors.pack(side=TOP, pady=10)

# Label to display dominant colors
dominant_colors_label = Label(root, bg=bg_color, bd=0 , width=800, height=30)
dominant_colors_label.pack(pady=10)

# heading for names and the display
color_info_label = Label(root, text="Dominant color names and the percentages", font=('Arial', 13))
color_info_label.pack(pady=10)

# Label to display color names and percentages
color_info_label = Label(root, text="", font=('Arial', 11), bg=bg_color, bd=0)
color_info_label.pack(pady=10)

# Bind mouse click event to the canvas
canvas.bind("<Button-1>", on_click)

root.mainloop()
