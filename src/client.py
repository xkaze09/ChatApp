'''
Authors: Kristina Celis & Christian Salinas

Description: client.py implements the client-side functionality
of the chat app. It allows user to connect to a chat server,
send and receive messages, and view a list of online users.
'''

# IMPORTS
import socket
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import font, simpledialog

# GLOBALS (avoids multiple,repetitive parameters)
client_socket = None
server_ip = None
server_port = None
username = None
status_value_label = None
online_users_label = None
canvas = None
scrollable_frame = None
msg_entry = None

# UTILITY FUNCTIONS
def add_timestamp():
    ''' Add a timestamp to messages '''
    return datetime.now().strftime('%b %d, %Y - %I:%M %p')

def create_label(frame, label_text, value_text, row, status=False):
    ''' Create labels for header information '''
    text_font = font.Font(family="Helvetica", size=11)
    tk.Label(frame, text=label_text, font=text_font, bg="#1f2a44", fg="white").grid(row=row, column=0, sticky='e', padx=5, pady=2)
    label = tk.Label(frame, text=value_text, font=text_font, bg="#3b4b67", fg="white", width=20, anchor='w')
    label.grid(row=row, column=1, sticky='w', padx=5, pady=2)
    return label if status else None

def update_online_users(users):
    ''' Update the online users list display '''
    global online_users_label
    users_text = ", ".join(users)
    online_users_label.config(text=users_text)

def update_status(message, color):
    ''' Update the status label with connection status '''
    global status_value_label
    status_value_label.config(text=message, bg=color)

# GUI SETUP FUNCTIONS
def setup_gui(root, client_ip, client_port):
    ''' Setup the chat client GUI '''
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

    # Online Users frame & labels
    online_users_frame = tk.LabelFrame(root, text="Online Users", font=("Helvetica", 10), bg="#1f2a44", fg="lightgreen", labelanchor="n")
    online_users_frame.pack(fill='x', padx=10, pady=10)

    online_users_label = tk.Label(online_users_frame, text="", font=("Helvetica", 10), bg="#3b4b67", fg="white", padx=10, pady=5, anchor="w", justify="left", wraplength=300)
    online_users_label.pack(fill="x")

    # Chat display area
    chat_frame = tk.Frame(root, bg="#263859")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Canvas and Scrollbar setup
    canvas = tk.Canvas(chat_frame, bg="#263859", borderwidth=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#263859")

    scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Message entry and send button
    msg_entry = tk.Entry(root, font=text_font, bg="#3b4b67", fg="white", insertbackground="white", relief="flat")
    msg_entry.pack(side='left', padx=(10, 0), pady=10, fill="x", expand=True)
    msg_entry.bind("<Return>", lambda e: send_message())
    
    send_button = tk.Button(root, text="Send", command=send_message, font=text_font, bg="#4c5c77", fg="white", width=10, relief="flat")
    send_button.pack(side='left', padx=(10, 10), pady=10)
    send_button.bind("<Enter>", lambda e: send_button.config(bg="#596985"))
    send_button.bind("<Leave>", lambda e: send_button.config(bg="#4c5c77"))

def display_message(message, sender):
    ''' Display a message in the chat display area '''
    global canvas, scrollable_frame

    # Create message frame in the scrollable area
    message_frame = tk.Frame(scrollable_frame, bg="#263859", pady=5)
    
    # Display timestamp label
    timestamp_label = tk.Label(
        message_frame,
        text=add_timestamp(),
        bg="#263859",
        fg="lightgray",
        font=("Helvetica", 8, "italic")
    )
    timestamp_label.pack(anchor="e" if sender == username else "w")

    # Define common properties
    wrap_length = 300
    bg_color = "#3b4b67" if sender == username else "#4c5c77"
    anchor = "e" if sender == username else "w"
    justify = "right" if sender == username else "left"
    padx = (230, 10) if sender == username else (10, 50)

    # Create the message label based on sender
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
    canvas.yview_moveto(1.0) 

# CLIENT FUNCTIONS
def send_message():
    ''' Send a message to the server and display it locally '''
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

def receive_messages():
    ''' Handle receiving messages from the server '''
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            # Check if message is an online users list
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

def attempt_reconnect():
    ''' Function to attempt reconnection '''
    global client_socket
    while True:
        try:
            time.sleep(5)  # Wait before attempting to reconnect
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket for clean, stable reconnection
            client_socket.connect((server_ip, server_port))  # Try to reconnect
            client_socket.send(username.encode('utf-8'))  # Resend username after reconnecting
            update_status("Connected", "lightgreen")
            threading.Thread(target=receive_messages, daemon=True).start()  # Restart message receiving thread
            display_message("Reconnected to the server.", "System")
            break
        except (ConnectionRefusedError, OSError):
            update_status("Reconnecting...", "orange")
            continue

def initial_connect():
    ''' Initial client connection setup '''
    global client_socket
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            return
        except (ConnectionRefusedError, OSError):
            print("Server is offline. Attempting to reconnect...")
            time.sleep(5)


# PROGRAM ENTRY POINT
if __name__ == "__main__":
    # Initialize Tkinter root for prompts
    root = tk.Tk()
    root.withdraw()

    # Prompt for server IP, port, and username, exit if any prompt is canceled
    server_ip = simpledialog.askstring("Server IP", "Enter IP Address of the server:", initialvalue="127.0.0.1")
    server_port = simpledialog.askinteger("Port", "Enter Port Number of the server:", initialvalue=12345)
    username = simpledialog.askstring("Username", "Please enter a username:")

    # If any input is canceled, exit the program
    if not all([server_ip, server_port, username]):
        root.destroy()
        exit()

    # Close the prompt window as input collection is complete
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

    # Start the receiving thread to continuously listen for new messages from the server
    threading.Thread(target=receive_messages, daemon=True).start()

    # Start the GUI mainloop
    root.mainloop()
