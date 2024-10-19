import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pandas as pd
from reportlab.pdfgen import canvas

# Global variables
clicked = False
r = g = b = xpos = ypos = 0
file_path = ""
df = None
img = None  # Define img globally

# Load colors data
csv_path = 'colors.csv'
index = ['color', 'color_name', 'hex', 'R', 'G', 'B']
df = pd.read_csv(csv_path, names=index, header=None)

# Function to get the most matching color
def get_color_name(R, G, B):
    global df
    if df is None:
        # Load colors data
        csv_path = 'colors.csv'
        index = ['color', 'color_name', 'hex', 'R', 'G', 'B']
        df = pd.read_csv(csv_path, names=index, header=None)

    minimum = 1000
    cname = ""
    for i in range(len(df)):
        d = abs(R - int(df.loc[i, 'R'])) + abs(G - int(df.loc[i, 'G'])) + abs(B - int(df.loc[i, 'B']))
        if d <= minimum:
            minimum = d
            cname = df.loc[i, 'color_name']
    return cname

# Function to get x,y coordinates of mouse double click
def draw_function(event, x, y, flags, param):
    global b, g, r, xpos, ypos, clicked, img  # Ensure img is global
    if event == cv2.EVENT_LBUTTONDBLCLK:
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]  # Access img here
        b = int(b)
        g = int(g)
        r = int(r)
        color = get_color_name(r, g, b)
        color_listbox.insert(tk.END, f"Color: {color}, RGB: ({r}, {g}, {b})")

def choose_image():
    global file_path, img  # Make img global here too
    file_path = filedialog.askopenfilename()
    if file_path:
        file_label.config(text="Selected file: " + file_path.split("/")[-1])
        img = cv2.imread(file_path)
        img = cv2.resize(img, (800, 600))
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', draw_function)
        while True:
            cv2.imshow('image', img)
            if clicked:
                cv2.rectangle(img, (20, 20), (600, 60), (b, g, r), -1)
                text = get_color_name(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)
                cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                if r + g + b >= 600:
                    cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        cv2.destroyAllWindows()

def start_camera():
    global clicked, img  # Make img global here
    clicked = False
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('camera')
    cv2.setMouseCallback('camera', draw_function)

    while True:
        ret, img = cap.read()
        if not ret:
            break

        cv2.imshow('camera', img)
        if clicked:
            cv2.rectangle(img, (20, 20), (600, 60), (b, g, r), -1)
            text = get_color_name(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)
            cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            if r + g + b >= 600:
                cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
        if cv2.waitKey(20) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def print_image():
    global img
    if file_path:
        img = Image.open(file_path)
        img.show()

def print_colors():
    if color_listbox.size() > 0:
        c = canvas.Canvas("detected_colors.pdf")
        c.drawString(100, 750, "Detected Colors:")
        y = 730
        for i in range(color_listbox.size()):
            c.drawString(100, y, color_listbox.get(i))
            y -= 20
        c.save()
        messagebox.showinfo("Print Colors", "The detected colors have been saved to detected_colors.pdf")

def close_app():
    root.destroy()

# Set up Tkinter
root = tk.Tk()
root.title("Image Color Detector")

choose_button = tk.Button(root, text="Choose Image", command=choose_image, font=('Arial', 20, 'bold'), padx=20, pady=10,
                          bg='lightblue', fg='darkblue', relief='raised', borderwidth=3)
choose_button.pack(pady=20)

file_label = tk.Label(root, text="", font=('Arial', 12), pady=10)
file_label.pack()

upload_button = tk.Button(root, text="Upload Image", command=choose_image, font=('Arial', 20, 'bold'), padx=20, pady=10,
                          bg='green', fg='white', relief='raised', borderwidth=3)
upload_button.pack(pady=10)

start_camera_button = tk.Button(root, text="Start Camera", command=start_camera, font=('Arial', 20, 'bold'), padx=20, pady=10,
                          bg='orange', fg='white', relief='raised', borderwidth=3)
start_camera_button.pack(pady=10)

color_listbox = tk.Listbox(root, font=('Arial', 12), width=50, height=10)
color_listbox.pack(pady=10)

print_image_button = tk.Button(root, text="Print Image", command=print_image, font=('Arial', 20, 'bold'), padx=20, pady=10,
                               bg='blue', fg='white', relief='raised', borderwidth=3)
print_image_button.pack(pady=10)

print_colors_button = tk.Button(root, text="Print Colors", command=print_colors, font=('Arial', 20, 'bold'), padx=20, pady=10,
                                bg='purple', fg='white', relief='raised', borderwidth=3)
print_colors_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=close_app, font=('Arial', 20, 'bold'), padx=20, pady=10,
                        bg='red', fg='white', relief='raised', borderwidth=3)
exit_button.pack(pady=10)

root.mainloop()
