import cv2
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

# Function to open and display an image
def open_image():
    global img_path, img, tk_img, img_resized, img_pil, canvas_img, original_img_pil
    img_path = filedialog.askopenfilename()
    if img_path:
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        original_img_pil = img_pil.copy()  # Save the original image

        # Resize image to fit within the canvas while maintaining aspect ratio
        img_pil.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
        img_resized = img_pil
        tk_img = ImageTk.PhotoImage(img_resized)
        canvas_img = canvas.create_image(0, 0, anchor=NW, image=tk_img)
        
        # Call dominant color finding function
        dominant_colors(dominant_colors_label, color_info_frame)

# Function to take and display a picture from the webcam
def take_picture():
    global img_path, img, tk_img, img_resized, img_pil, canvas_img, original_img_pil

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam")
        return
    
    ret, frame = cap.read()
    cap.release()

    if ret:
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        original_img_pil = img_pil.copy()  # Save the original image
        
        # Resize image to fit within the canvas while maintaining aspect ratio
        img_pil.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
        img_resized = img_pil
        tk_img = ImageTk.PhotoImage(img_resized)
        canvas_img = canvas.create_image(0, 0, anchor=NW, image=tk_img)
        
        # Call dominant color finding function
        dominant_colors(dominant_colors_label, color_info_frame)
    else:
        print("Failed to capture image")

# Function for dominant colors
def dominant_colors(label_widget, info_widget):
    global img_path, percentages, color_names
    
    img = np.array(img_pil)
    img_rgb = img[:, :, :3]  # Convert to RGB
    img_reshaped = img_rgb.reshape((-1, 3)) 

    k = 5  
    kmeans = KMeans(n_clusters=k)  # Initialize KMeans
    kmeans.fit(img_reshaped)  # Fit KMeans
    dominant_colors = kmeans.cluster_centers_.astype(int)  # Get dominant colors

    labels = kmeans.labels_  # Get cluster labels for each pixel
    label_counts = np.bincount(labels)  # Count pixels in each cluster
    total_count = len(labels)  # Total pixels

    # Calculate percentage
    percentages = [count / total_count * 100 for count in label_counts]

    # Dominant color display
    dominant_colors_img = np.zeros((100, 100 * k, 3), dtype=int)
    for i in range(k):
        dominant_colors_img[:, i * 100:(i + 1) * 100, :] = dominant_colors[i]

    fig, ax = plt.subplots(figsize=(5, 1))
    ax.imshow(dominant_colors_img, aspect='auto')
    ax.axis('off')

    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)

    dominant_colors_image = Image.open(buf) 
    tk_dominant_colors_image = ImageTk.PhotoImage(dominant_colors_image)

    label_widget.config(image=tk_dominant_colors_image)
    label_widget.image = tk_dominant_colors_image

    # Clear previous color names and percentages
    for widget in info_widget.winfo_children():
        widget.destroy()

    color_names = []

    # Display color names and percentages below each color
    for i in range(k):
        color_name = get_color_name(*dominant_colors[i])  
        percentage = percentages[i]
        hex_value = f'#{dominant_colors[i][0]:02x}{dominant_colors[i][1]:02x}{dominant_colors[i][2]:02x}'.upper()
        color_info = f"{color_name}: {percentage:.2f}%"
        hex_info = f"{hex_value}"
        
        color_label = Label(info_widget, text=color_info, font=('Arial', 11), bg=bg_color, fg=text_color, bd=0)
        color_label.grid(row=1, column=i, padx=10, pady=5)  # Display below the color
        hex_label = Label(info_widget, text=hex_info, font=('Arial', 11), bg=bg_color, fg=text_color, bd=0)
        hex_label.grid(row=2, column=i, padx=10, pady=5)  # Display below the name and percentage
        
        color_names.append(color_name)

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
    global b, g, r, x_pos, y_pos, img_resized, img_pil
    x_pos = event.x
    y_pos = event.y

    # Adjust coordinates according to the resized image
    width_ratio = img_pil.size[0] / img_resized.width
    height_ratio = img_pil.size[1] / img_resized.height
    x_adjusted = int(x_pos * width_ratio)
    y_adjusted = int(y_pos * height_ratio)
    
    r, g, b = img_pil.getpixel((x_adjusted, y_adjusted))
    update_color_info()

# Function to update and display color information
def update_color_info():
    global r, g, b
    color_name = get_color_name(r, g, b)
    hex_value = f'#{r:02x}{g:02x}{b:02x}'.upper()
    rgb_value = f'RGB: ({r}, {g}, {b})'

    color_name_label.config(text=f"Color Name: {color_name}")
    hex_label.config(text=f"Hex Value: {hex_value}")
    rgb_label.config(text=f"RGB Value: {rgb_value}")
    color_display.config(bg=hex_value)

# Function to print summary report
def print_summary():
    global img_path, dominant_colors, percentages, color_names, buf

    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    c = pdf_canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 100, "Color Detection Summary Report")

    # Insert image
    img = ImageReader(img_path)
    c.drawImage(img, 100, height - 500, width=400, height=400, preserveAspectRatio=True)

    # Insert dominant colors
    c.drawString(100, height - 550, "Dominant Colors:")
    for i, (color_name, percentage) in enumerate(zip(color_names, percentages)):
        c.drawString(100, height - 570 - i*20, f"{color_name}: {percentage:.2f}%")

    c.save()

# Function to apply filter to the image
def apply_filter(filter_type):
    global img_pil, img_resized, tk_img, canvas_img

    img_filtered = img_pil.copy()

    if filter_type == "Grayscale":
        img_filtered = img_filtered.convert("L").convert("RGB")
    elif filter_type == "Sepia":
        sepia_filter = ImageEnhance.Color(img_filtered)
        img_filtered = sepia_filter.enhance(0.3)
    elif filter_type == "Negative":
        img_filtered = Image.eval(img_filtered, lambda p: 255 - p)
    elif filter_type == "Brighten":
        enhancer = ImageEnhance.Brightness(img_filtered)
        img_filtered = enhancer.enhance(1.5)
    elif filter_type == "Contrast":
        enhancer = ImageEnhance.Contrast(img_filtered)
        img_filtered = enhancer.enhance(1.5)

    img_resized = img_filtered.copy()
    img_resized.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
    tk_img = ImageTk.PhotoImage(img_resized)
    canvas.itemconfig(canvas_img, image=tk_img)

# Function to remove filter
def remove_filter():
    global img_pil, img_resized, tk_img, canvas_img, original_img_pil

    img_pil = original_img_pil.copy()
    img_resized = img_pil.copy()
    img_resized.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
    tk_img = ImageTk.PhotoImage(img_resized)
    canvas.itemconfig(canvas_img, image=tk_img)

# Initialize tkinter window
root = Tk()

root.title("Color Detection App")
root.iconbitmap('Color Vista.ico')
root.geometry("1000x750")

# Set dark background color
bg_color = '#2E2E2E'
text_color = '#E0E0E0'
button_color = '#4CAF50'
print_button_color = '#ff4b2f'
button_text_color = 'white'
highlight_color = '#2196F3'

root.configure(bg=bg_color)

# Load CSV file
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Main frame
main_frame = Frame(root, bg=bg_color)
main_frame.pack(pady=20)

# Add canvas to display image
canvas_frame = Frame(main_frame, bg=bg_color)
canvas_frame.grid(row=0, column=0, padx=20, pady=10)
canvas = Canvas(canvas_frame, width=500, height=400, bg='#3C3C3C', highlightthickness=0)
canvas.pack()

# Controls frame
controls_frame = Frame(main_frame, bg=bg_color)
controls_frame.grid(row=0, column=1, padx=20, pady=10)

# Add button to open image
btn_open = Button(controls_frame, text="Open Image", command=open_image, font=('Arial', 14), bg=button_color, fg=button_text_color)
btn_open.pack(pady=10)

# Add button to take picture
btn_take_picture = Button(controls_frame, text="Take Picture", command=take_picture, font=('Arial', 14), bg=button_color, fg=button_text_color)
btn_take_picture.pack(pady=10)

# Labels to display color information
color_name_label = Label(controls_frame, text="Color Name:", font=('Arial', 14), bg=bg_color, fg=text_color, bd=0)
color_name_label.pack(pady=5)

hex_label = Label(controls_frame, text="Hex Value:", font=('Arial', 14), bg=bg_color, fg=text_color, bd=0)
hex_label.pack(pady=5)

rgb_label = Label(controls_frame, text="RGB Value:", font=('Arial', 14), bg=bg_color, fg=text_color, bd=0)
rgb_label.pack(pady=5)

color_display = Label(controls_frame, width=20, height=2, font=('Arial', 14), bg=bg_color, bd=0)
color_display.pack(pady=10)

# Label to display dominant colors
dominant_colors_label = Label(controls_frame, bg=bg_color, bd=0)
dominant_colors_label.pack(pady=10)

# Frame to display color names and percentages
color_info_frame = Frame(controls_frame, bg=bg_color)
color_info_frame.pack(pady=10)

# Add button to generate a new color palette
btn_generate_palette = Button(controls_frame, text="Generate New Color Palette", command=lambda: dominant_colors(dominant_colors_label2, color_info_frame2), font=('Arial', 14), bg=highlight_color, fg=button_text_color)
btn_generate_palette.pack(pady=10)

# Label to display another dominant colors
dominant_colors_label2 = Label(controls_frame, bg=bg_color, bd=0)
dominant_colors_label2.pack(pady=10)

# Frame to display color names and percentages
color_info_frame2 = Frame(controls_frame, bg=bg_color)
color_info_frame2.pack(pady=10)

# Add filter dropdown menu
filter_var = StringVar()
filter_var.set("Select Filter")

filter_options = ["Grayscale", "Sepia", "Negative", "Brighten", "Contrast"]
filter_menu = OptionMenu(controls_frame, filter_var, *filter_options, command=apply_filter)
filter_menu.config(font=('Arial', 14), bg=highlight_color, fg=button_text_color)
filter_menu.pack(pady=10)

# Add button to remove filter
btn_remove_filter = Button(controls_frame, text="Remove Filter", command=remove_filter, font=('Arial', 14), bg=print_button_color, fg=button_text_color)
btn_remove_filter.pack(pady=10)

# Add button to print summary report
btn_print = Button(canvas_frame, text="Print Summary Report", command=print_summary, font=('Arial', 14), bg=print_button_color, fg=button_text_color)
btn_print.pack(pady=10)

# Bind mouse click event to the canvas
canvas.bind("<Button-1>", on_click)

root.mainloop()
