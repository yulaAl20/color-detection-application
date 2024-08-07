import cv2
import pandas as pd
import numpy as np
import os
from tkinter import *
from tkinter import filedialog
from tkinter import Frame
from PIL import Image, ImageTk, ImageEnhance
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from tkinter import ttk


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

#Start Pdf Writing
# Create a PDF class extending FPDF to include the header
class PDF(FPDF):
    def header(self):
        # Logo
        self.image('Color Vista.png', 20, 5, 40)
        # Font
        self.set_font('helvetica', 'B', 30)
        # Title
        self.cell(0, 25, 'Color Vista', ln=1, align='C')
        # Line break
        self.ln(20)
        
        # Draw a line
        self.line(10, 50, 200, 50) 

# Create an instance of the PDF class
pdf = PDF('P', 'mm', 'Letter')

# Add a page
pdf.add_page()

# Add auto break pages
pdf.set_auto_page_break(auto=True, margin=15)

# Set font
pdf.set_font('helvetica', 'B', 14)

# Add text
pdf.cell(0, 20, 'Uploaded image', ln=True,align='C')

#add image
def add_image(self, img_path, x, y, w, h):
        if os.path.exists(img_path):
            self.image(img_path, x, y, w, h)
        else:
            print(f"Image at {img_path} not found")

# Function to print summary report
def print_summary():
    global img_path, dominant_colors, percentages, color_names, buf

    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    if os.path.exists(img_path):
        pdf.image(img_path, x=58, y=75, w=100)
        pdf.ln(110)

    pdf.cell(200, 10, txt="Dominant Colors:", ln=True, align='C')
    for color_name, percentage in zip(color_names, percentages):
        pdf.cell(200, 10, txt=f"{color_name}: {percentage:.2f}%", ln=True, align='C')

    pdf.output(pdf_path)
    print("PDF created successfully!")

#End pdf writing

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

#tab2 filter 
# Apply filters to an image
def apply_filter_image(filter_type):
    global img_pil
    if filter_type == "Grayscale":
        return img_pil.convert("L")
    elif filter_type == "Sepia":
        img_array = np.array(img_pil)
        sepia_filter = np.array([[0.393, 0.769, 0.189],
                                 [0.349, 0.686, 0.168],
                                 [0.272, 0.534, 0.131]])
        sepia_image = cv2.transform(img_array, sepia_filter)
        sepia_image = np.clip(sepia_image, 0, 255)
        return Image.fromarray(sepia_image.astype('uint8'))
    elif filter_type == "Negative":
        img_array = np.array(img_pil)
        negative_image = 255 - img_array
        return Image.fromarray(negative_image)
    elif filter_type == "Brighten":
        img_array = np.array(img_pil)
        brighten_image = cv2.convertScaleAbs(img_array, alpha=1.2, beta=30)
        return Image.fromarray(brighten_image)
    elif filter_type == "Contrast":
        img_array = np.array(img_pil)
        contrast_image = cv2.convertScaleAbs(img_array, alpha=1.5, beta=0)
        return Image.fromarray(contrast_image)
    else:
        return img_pil

# Function to display the histogram
def display_histogram(original_image, filtered_image):
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # Plot histogram for original image
    original_array = np.array(original_image)
    original_hist = cv2.calcHist([original_array], [0], None, [256], [0, 256])
    ax[0].plot(original_hist, color='gray')
    ax[0].set_title('Original Image Histogram')

    # Plot histogram for filtered image
    filtered_array = np.array(filtered_image)
    filtered_hist = cv2.calcHist([filtered_array], [0], None, [256], [0, 256])
    ax[1].plot(filtered_hist, color='blue')
    ax[1].set_title('Filtered Image Histogram')

    # Save the histogram to a BytesIO object
    hist_io = BytesIO()
    plt.savefig(hist_io, format='png')
    hist_io.seek(0)
    hist_image = Image.open(hist_io)
    
    plt.close(fig)  # Close the figure to avoid displaying it in a separate window
    return hist_image

# Function to update the tab2 content
def update_tab2():
    global img_pil, tk_img_filtered, filtered_canvas_img, hist_canvas_img

    # Update original image display
    img_pil_resized = img_pil.copy()
    img_pil_resized.thumbnail((250, 250))
    tk_img_original = ImageTk.PhotoImage(img_pil_resized)
    original_image_canvas.itemconfig(original_canvas_img, image=tk_img_original)
    original_image_canvas.image = tk_img_original

    # Apply the selected filter and update the filtered image display
    filter_type = filter_var.get()
    img_filtered = apply_filter_image(filter_type)
    img_filtered_resized = img_filtered.copy()
    img_filtered_resized.thumbnail((250, 250))
    tk_img_filtered = ImageTk.PhotoImage(img_filtered_resized)
    filtered_image_canvas.itemconfig(filtered_canvas_img, image=tk_img_filtered)
    filtered_image_canvas.image = tk_img_filtered

    # Generate and display the histogram
    hist_image = display_histogram(img_pil, img_filtered)
    hist_image.thumbnail((600, 600)) 
    tk_hist_image = ImageTk.PhotoImage(hist_image)
    histogram_canvas.itemconfig(hist_canvas_img, image=tk_hist_image)
    histogram_canvas.image = tk_hist_image


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

# Create a notebook (tabs container)
notebook = ttk.Notebook(root)
notebook.pack(pady=5, expand=True)

# Create two frames to be used as tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# Add the frames as tabs
notebook.add(tab1, text="Main")
notebook.add(tab2, text="Filter")

root.configure(bg=bg_color)
# Main Tab content (tab1)

# Load CSV file
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Main frame
main_frame = Frame(tab1, bg=bg_color)
main_frame.pack(pady=20)

# Add canvas to display image
canvas_frame = Frame(main_frame, bg=bg_color)
canvas_frame.grid(row=0, column=0, padx=20, pady=10)
canvas = Canvas(canvas_frame, width=500, height=400, bg='#3C3C3C', highlightthickness=0)
canvas.pack()

# Create a frame to hold the buttons
button_frame = Frame(canvas_frame,bg='#3C3C3C')
button_frame.pack(pady=10)

# Add button to open image
btn_open = Button(button_frame, text="Open Image", command=open_image, font=('Arial', 14), bg=button_color, fg=button_text_color)
btn_open.pack(side=LEFT, padx=5)

# Add button to take picture
btn_take_picture = Button(button_frame, text="Take Picture", command=take_picture, font=('Arial', 14), bg=button_color, fg=button_text_color)
btn_take_picture.pack(side=LEFT, padx=5)

# Create a frame to hold the filter menu and remove filter button
filter_frame = Frame(canvas_frame,bg='#3C3C3C')
filter_frame.pack(pady=10)

# Add filter dropdown menu
filter_var = StringVar()
filter_var.set("Select Filter")

filter_options = ["Grayscale", "Sepia", "Negative", "Brighten", "Contrast"]
filter_menu = OptionMenu(filter_frame, filter_var, *filter_options, command=apply_filter)
filter_menu.config(font=('Arial', 14), bg=highlight_color, fg=button_text_color)
filter_menu.pack(side=LEFT, padx=5)

# Add button to remove filter
btn_remove_filter = Button(filter_frame, text="Remove Filter", command=remove_filter, font=('Arial', 14), bg=print_button_color, fg=button_text_color)
btn_remove_filter.pack(side=LEFT, padx=5)

# Add button to print summary report
btn_print = Button(canvas_frame, text="Print Summary Report", command=print_summary, font=('Arial', 14), bg=print_button_color, fg=button_text_color)
btn_print.pack(pady=10)

# Controls frame
controls_frame = Frame(main_frame, bg=bg_color)
controls_frame.grid(row=0, column=1, padx=20, pady=10,sticky='nsew')

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

# Bind mouse click event to the canvas
canvas.bind("<Button-1>", on_click)

# Tab 2 content

# Main frame
main_frame_tab2 = Frame(tab2, bg=bg_color)
main_frame_tab2.pack(pady=10)

# Frame for original and filtered images
image_frame = Frame(tab2, bg=bg_color)
image_frame.pack(pady=20)

# Configure style to set the background color for ttk frames
style = ttk.Style()
style.configure('TFrame', background=bg_color)

# Canvas for displaying original image
original_image_canvas = Canvas(image_frame, width=250, height=250, bg='#505050', highlightthickness=0)
original_image_canvas.pack(side=LEFT, padx=10)
original_canvas_img = original_image_canvas.create_image(0, 0, anchor=NW)

# Canvas for displaying filtered image
filtered_image_canvas = Canvas(image_frame, width=250, height=250, bg='#505050', highlightthickness=0)
filtered_image_canvas.pack(side=LEFT, padx=10)
filtered_canvas_img = filtered_image_canvas.create_image(0, 0, anchor=NW)

# Dropdown menu for filters
filter_var = StringVar()
filter_var.set("Select Filter")

filter_options = ["Grayscale", "Sepia", "Negative", "Brighten", "Contrast"]
filter_menu = OptionMenu(tab2, filter_var, *filter_options)
filter_menu.config(font=('Arial', 14), bg=highlight_color, fg=text_color)
filter_menu.pack(pady=10)

# Button to apply filter and update tab2
btn_apply_filter = Button(tab2, text="Apply Filter", command=update_tab2, font=('Arial', 14), bg=button_color, fg=text_color)
btn_apply_filter.pack(pady=10)

# Canvas for displaying histogram
histogram_canvas = Canvas(tab2, width=600, height=600, bg=bg_color, highlightthickness=0)
histogram_canvas.pack(pady=10)
hist_canvas_img = histogram_canvas.create_image(0, 0, anchor=NW)

root.mainloop()
