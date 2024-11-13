import socket
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import font, simpledialog

# Global variables for server IP, port, and username
client_socket = None
server_ip = None
server_port = None
username = None
status_value_label = None
online_users_label = None  # New variable for the Online Users label
canvas = None
scrollable_frame = None
msg_entry = None

# Function to add a timestamp to messages
def add_timestamp():
    return datetime.now().strftime('%b %d, %Y - %I:%M %p')

# Setup the chat client GUI 
def setup_gui(root, client_ip, client_port):
    global status_value_label, online_users_label, canvas, scrollable_frame, msg_entry
    
    text_font = font.Font(family="Helvetica", size=11)
    root.title("Chat Client")
    root.configure(bg="#1f2a44") 
    root.resizable(False, False)

    # Header frame with client information
    header_frame = tk.Frame(root, bg="#1f2a44")
    header_frame.pack(fill='x', padx=10, pady=5)

    # Display client and server info in the header
    create_label(header_frame, "Your IP Address:", client_ip, row=0)
    create_label(header_frame, "Your Port Number:", client_port, row=1)
    create_label(header_frame, "Your Name:", username, row=2)
    create_label(header_frame, "Connected with:", f"{server_ip}:{server_port}", row=3)
    status_value_label = create_label(header_frame, "Status:", "Connecting...", row=4, status=True)

    # Online Users frame
    online_users_frame = tk.LabelFrame(root, text="Online Users", font=("Helvetica", 10), bg="#1f2a44", fg="lightgreen", labelanchor="n")
    online_users_frame.pack(fill='x', padx=10, pady=10)

    # Online Users label for displaying comma-separated users
    online_users_label = tk.Label(online_users_frame, text="", font=("Helvetica", 10), bg="#3b4b67", fg="white", padx=10, pady=5, anchor="w", justify="left", wraplength=300)
    online_users_label.pack(fill="x")

    # Chat display area (scrollable)
    chat_frame = tk.Frame(root, bg="#263859")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Canvas and Scrollbar setup for scrollable chat
    canvas = tk.Canvas(chat_frame, bg="#263859", borderwidth=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#263859")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Message entry and send button
    msg_entry = tk.Entry(root, font=text_font, bg="#3b4b67", fg="white", insertbackground="white", relief="flat")
    msg_entry.pack(side='left', padx=(10, 0), pady=10, fill="x", expand=True)
    msg_entry.bind("<Return>", lambda e: send_message())
    
    # Send button with styling and hover effect
    send_button = tk.Button(root, text="Send", command=send_message, font=text_font, bg="#4c5c77", fg="white", width=10, relief="flat")
    send_button.pack(side='left', padx=(10, 10), pady=10)
    send_button.bind("<Enter>", lambda e: send_button.config(bg="#596985"))
    send_button.bind("<Leave>", lambda e: send_button.config(bg="#4c5c77"))

# Helper function to create labels for header information
def create_label(frame, label_text, value_text, row, status=False):
    text_font = font.Font(family="Helvetica", size=11)
    tk.Label(frame, text=label_text, font=text_font, bg="#1f2a44", fg="white").grid(row=row, column=0, sticky='e', padx=5, pady=2)
    label = tk.Label(frame, text=value_text, font=text_font, bg="#3b4b67", fg="white", width=20, anchor='w')
    label.grid(row=row, column=1, sticky='w', padx=5, pady=2)
    return label if status else None

# Update the online users list display
def update_online_users(users):
    global online_users_label
    users_text = ", ".join(users)
    online_users_label.config(text=users_text)


# Display a message in the chat display area
def display_message(message, sender):
    global canvas, scrollable_frame

    # Create message frame in the scrollable area
    message_frame = tk.Frame(scrollable_frame, bg="#263859", pady=5)
    
    # Display timestamp label with alignment based on sender
    timestamp_label = tk.Label(
        message_frame,
        text=add_timestamp(),
        bg="#263859",
        fg="lightgray",
        font=("Helvetica", 8, "italic")
    )
    timestamp_label.pack(anchor="e" if sender == username else "w")  # Right-align for user's own messages

    # Define common properties for message label
    wrap_length = 300
    bg_color = "#3b4b67" if sender == username else "#4c5c77"
    anchor = "e" if sender == username else "w"
    justify = "right" if sender == username else "left"
    padx = (230, 10) if sender == username else (10, 50)  # Adjust padding for right alignment

    # Create the message label with dynamic properties based on sender
    message_label = tk.Label(
        message_frame,
        text=message,
        bg=bg_color,
        fg="white",
        font=("Helvetica", 10),
        padx=10,
        pady=5,
        wraplength=wrap_length,
        anchor=anchor,
        justify=justify
    )
    message_label.pack(anchor=anchor)
    message_frame.pack(anchor=anchor, fill="x", padx=padx, pady=5)

    # Update the canvas to scroll to the bottom for each new message
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)  # Auto-scroll to the bottom

# Send a message to the server and display it locally
def send_message():
    global msg_entry, client_socket
    message = msg_entry.get()
    if message:
        formatted_message = f"{username}: {message}"
        display_message(formatted_message, username)
        try:
            client_socket.send(message.encode('utf-8'))
        except (BrokenPipeError, OSError):
            display_message("Message not sent. Server is offline.", "System")
        msg_entry.delete(0, tk.END)

# Update the status label with connection status
def update_status(message, color):
    global status_value_label
    status_value_label.config(text=message, bg=color)

# Function to handle receiving messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            # Treat the message as online users list if it’s comma-separated usernames only
            if all(part.isalpha() or part.isnumeric() for part in message.split(",")):
                users = message.split(",")
                update_online_users(users)
            else:
                # Display regular message
                sender = message.split(":")[0]
                display_message(message, sender)
        except (ConnectionResetError, OSError):
            update_status("Reconnecting...", "orange")
            display_message("Connection lost. Attempting to reconnect...", "System")
            attempt_reconnect()
            break


# Function to attempt reconnection
def attempt_reconnect():
    global client_socket
    while True:
        try:
            time.sleep(5)  # Wait before attempting to reconnect
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
            client_socket.connect((server_ip, server_port))  # Try to reconnect
            client_socket.send(username.encode('utf-8'))  # Resend username after reconnecting
            update_status("Connected", "lightgreen")
            threading.Thread(target=receive_messages, daemon=True).start()  # Restart message receiving thread
            display_message("Reconnected to the server.", "System")
            break
        except (ConnectionRefusedError, OSError):
            update_status("Reconnecting...", "orange")
            continue

# Initial connection setup
def initial_connect():
    global client_socket
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            return
        except (ConnectionRefusedError, OSError):
            print("Server is offline. Attempting to reconnect...")
            time.sleep(5)

# Main setup
if __name__ == "__main__":
    # Prompt for server IP, port, and username
    root = tk.Tk()
    root.withdraw()
    server_ip = simpledialog.askstring("Server IP", "Enter IP Address of the server:", initialvalue="127.0.0.1")
    server_port = simpledialog.askinteger("Port", "Enter Port Number of the server:", initialvalue=12345)
    username = simpledialog.askstring("Username", "Please enter a username:")
    root.destroy()

    # Attempt initial connection
    initial_connect()

    # Send username to the server
    client_socket.send(username.encode('utf-8'))

    # Retrieve client's local IP and port
    client_ip, client_port = client_socket.getsockname()

    # Setup the GUI
    root = tk.Tk()
    setup_gui(root, client_ip, client_port)
    update_status("Connected", "lightgreen")

    # Start the receiving thread
    threading.Thread(target=receive_messages, daemon=True).start()

    # Start the GUI mainloop
    root.mainloop()
