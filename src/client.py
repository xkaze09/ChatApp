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
online_users = []
status_value_label = None
online_users_label = None
canvas = None
scrollable_frame = None
msg_entry = None

# Function to format message with a timestamp
def format_message(sender, message):
    timestamp = datetime.now().strftime('%b %d, %Y - %I:%M %p')
    return f"[{timestamp}] {sender}: {message}"

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
    create_label(header_frame, "Connected with:", f"{server_ip}:{server_port}", row=3)
    status_value_label = create_label(header_frame, "Status:", "Connecting...", row=2, status=True)

    # Online users frame (static, above the chat box)
    online_users_frame = tk.Frame(root, bg="#1f2a44", pady=5)
    online_users_frame.pack(fill="x", padx=10, pady=(0, 10))
    online_users_label = tk.Label(online_users_frame, text="Online Users: ", font=text_font, bg="#1f2a44", fg="lightgreen")
    online_users_label.pack(anchor="w")

    # Chat display area (scrollable)
    chat_frame = tk.Frame(root, bg="#263859")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    canvas = tk.Canvas(chat_frame, bg="#263859")
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
    global online_users, online_users_label
    online_users = users
    users_text = "Online Users: " + ", ".join(online_users)
    online_users_label.config(text=users_text)

# Display a message in the chat display area, aligning based on sender
def display_message(message, sender):
    global canvas, scrollable_frame

    message_frame = tk.Frame(scrollable_frame, bg="#263859", pady=5)
    if sender == username:  # User's own message
        tk.Label(message_frame, text=message, bg="#3b4b67", fg="white", font=("Helvetica", 10), padx=10, pady=5, wraplength=300, anchor="e", justify="right").pack(anchor="e")
        message_frame.pack(anchor="e", fill="x", padx=10, pady=5)
    else:  # Message from others
        tk.Label(message_frame, text=message, bg="#4c5c77", fg="white", font=("Helvetica", 10), padx=10, pady=5, wraplength=300, anchor="w", justify="left").pack(anchor="w")
        message_frame.pack(anchor="w", fill="x", padx=10, pady=5)

    canvas.update_idletasks()
    canvas.yview_moveto(1.0)  # Auto-scroll to the bottom

# Send a message to the server and display it locally
def send_message():
    global msg_entry, client_socket
    message = msg_entry.get()
    if message:
        formatted_message = format_message(username, message)
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
            if message.startswith("ONLINE_USERS:"):
                # Update the online users list
                users = message.split(":")[1].split(",")
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
