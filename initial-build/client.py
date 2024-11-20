import socket
import threading
import time
from datetime import datetime
from tkinter import Tk, Text, Entry, Button, END, Label, Frame, simpledialog, font

# Global variables for server IP, port, and username
server_ip = None
server_port = None
username = None

# Function to add a timestamp to messages
def add_timestamp(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"[{timestamp}] {message}"

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                timestamped_message = add_timestamp(message)
                chat_box.insert(END, f"{timestamped_message}\n")
                chat_box.see(END)
        except (ConnectionResetError, OSError):
            # Connection lost, initiate reconnection attempts
            update_status("Reconnecting...")
            chat_box.insert(END, "Connection lost. Attempting to reconnect...\n")
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
            update_status("Connected")
            threading.Thread(target=receive_messages, daemon=True).start()  # Restart message receiving thread
            chat_box.insert(END, "Reconnected to the server.\n")
            break
        except (ConnectionRefusedError, OSError):
            update_status("Reconnecting...")  # Update status to indicate reconnection attempts
            continue

# Function to send client messages
def send_message():
    message = msg_entry.get()
    if message:
        formatted_message = f"{username}: {message}"
        timestamped_message = add_timestamp(formatted_message)
        chat_box.insert(END, f"{timestamped_message}\n")
        try:
            client_socket.send(message.encode('utf-8'))
        except (BrokenPipeError, OSError):
            chat_box.insert(END, "Message not sent. Server is offline.\n")
        msg_entry.delete(0, END)

# Update client status in the GUI
def update_status(message):
    if message == "Connected":
        status_value_label.config(text="Connected", bg="lightgreen", fg="black")
    elif message == "Reconnecting...":
        status_value_label.config(text="Reconnecting...", bg="orange", fg="black")
    else:
        status_value_label.config(text="Disconnected", bg="red", fg="white")

# Setting up the client GUI with a blue theme and table-like header
def setup_gui(server_ip_param, server_port_param, client_ip, client_port):
    global chat_box, msg_entry, status_value_label, server_ip, server_port, username

    server_ip = server_ip_param
    server_port = server_port_param

    # Main window setup
    window = Tk()
    window.title("Modern Chat Client")
    window.configure(bg="#1f2a44")

    # Define a modern font
    text_font = font.Font(family="Helvetica", size=11)

    # Header frame with table-like layout
    header_frame = Frame(window, bg="#1f2a44")
    header_frame.pack(fill='x', padx=10, pady=10)

    # Table-like layout using grid in the header frame
    Label(header_frame, text="Your Entered Address:", font=text_font, bg="#1f2a44", fg="white").grid(row=0, column=0, sticky='e', padx=5, pady=2)
    Label(header_frame, text=client_ip, font=text_font, bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=0, column=1, sticky='w', padx=5, pady=2)

    Label(header_frame, text="Your Entered Port Number:", font=text_font, bg="#1f2a44", fg="white").grid(row=1, column=0, sticky='e', padx=5, pady=2)
    Label(header_frame, text=client_port, font=text_font, bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=1, column=1, sticky='w', padx=5, pady=2)

    Label(header_frame, text="Status:", font=text_font, bg="#1f2a44", fg="white").grid(row=2, column=0, sticky='e', padx=5, pady=2)
    status_value_label = Label(header_frame, text="Connecting...", font=text_font, bg="orange", fg="white", width=20, anchor='w')
    status_value_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)

    Label(header_frame, text="Connected with:", font=text_font, bg="#1f2a44", fg="white").grid(row=3, column=0, sticky='e', padx=5, pady=2)
    Label(header_frame, text=f"{server_ip}:{server_port}", font=text_font, bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=3, column=1, sticky='w', padx=5, pady=2)

    # Chat display area
    chat_box = Text(window, height=15, width=60, font=text_font, bg="#263859", fg="white", wrap="word")
    chat_box.pack(padx=10, pady=10)

    # Message entry and send button
    msg_entry = Entry(window, width=50, font=text_font, bg="#3b4b67", fg="white")
    msg_entry.pack(side='left', padx=(10, 0), pady=10)
    send_button = Button(window, text="Send", command=send_message, font=text_font, bg="#4c5c77", fg="white", activebackground="#3b4b67")
    send_button.pack(side='left', padx=(10, 10), pady=10)

    # Prompt for a username
    username = simpledialog.askstring("Username", "Please enter a username:")
    client_socket.send(username.encode('utf-8'))  # Send username to the server

    # Update the status to "Connected" once the username is sent successfully
    update_status("Connected")

    threading.Thread(target=receive_messages, daemon=True).start()
    window.mainloop()

# Initial connection setup
def initial_connect():
    global client_socket, server_ip, server_port
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            return
        except (ConnectionRefusedError, OSError):
            print("Server is offline. Attempting to reconnect...")
            time.sleep(5)

# Connect to the server
root = Tk()
root.withdraw()
server_ip = simpledialog.askstring("Server IP", "Enter IP Address of the server:", initialvalue="127.0.0.1")
server_port = simpledialog.askinteger("Port", "Enter Port Number of the server:", initialvalue=12345)
root.destroy()

# Attempt initial connection
initial_connect()

# Retrieve the client's local IP and port
client_ip, client_port = client_socket.getsockname()
setup_gui(server_ip, server_port, client_ip, client_port)
