import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from stegano import lsb

# Initialize the selected_image_path variable
selected_image_path = None

# Function to open a file dialog and select an image
def open_image():
    global selected_image_path
    file_path = filedialog.askopenfilename()
    if file_path:
        img = Image.open(file_path)
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.photo = photo
        selected_image_path = file_path
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, selected_image_path)

# Function to encode a message into the selected image
def encode_message():
    global selected_image_path
    if selected_image_path is None:
        messagebox.showerror("Error", "Please select an image first.")
        return

    message = message_entry.get()

    if not message:
        messagebox.showerror("Error", "Please enter a message.")
        return

    # Embed the message in the image
    encoded_image = lsb.hide(selected_image_path, message)

    # Save the encoded image to a file
    save_path = filedialog.asksaveasfilename(defaultextension=".png")
    if save_path:
        encoded_image.save(save_path)
        messagebox.showinfo("Success", "Message encoded and saved successfully.")

# Function to decode the message from the selected image
def decode_message():
    global selected_image_path
    if selected_image_path is None:
        messagebox.showerror("Error", "Please select an image first.")
        return

    try:
        decoded_message = lsb.reveal(selected_image_path)
        message_entry.delete(0, tk.END)
        message_entry.insert(0, decoded_message)
        messagebox.showinfo("Decoded Message", "Message decoded and displayed.")
    except Exception as e:
        messagebox.showerror("Error", "Decoding failed.")

# Create the main GUI window
window = tk.Tk()
window.title("Steganography")

# Create and configure widgets
select_image_button = tk.Button(window, text="Select Image", command=open_image)
image_label = tk.Label(window)
image_path_label = tk.Label(window, text="Image Path:")
image_path_entry = tk.Entry(window, width=50)
message_label = tk.Label(window, text="Message:")
message_entry = tk.Entry(window, width=50)
encode_button = tk.Button(window, text="Encode Message", command=encode_message)
decode_button = tk.Button(window, text="Decode Message", command=decode_message)

# Place widgets in the window
select_image_button.pack()
image_label.pack()
image_path_label.pack()
image_path_entry.pack()
message_label.pack()
message_entry.pack()
encode_button.pack()
decode_button.pack()

# Start the GUI main loop
window.mainloop()
