import socket
import threading
from datetime import datetime
from tkinter import Tk, Text, Entry, Button, END, Label, Frame, simpledialog

# Server configuration
clients = {}

# Function to add a timestamp to messages
def add_timestamp(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"[{timestamp}] {message}"

# Function to broadcast messages to all clients except the sender
def broadcast(message, sender_socket=None):
    # Add timestamp only once on the server
    timestamped_message = add_timestamp(message)
    for client in clients:
        if client != sender_socket:  # Exclude the sender from receiving their own message
            try:
                client.send(timestamped_message.encode('utf-8'))
            except:
                client.close()
                del clients[client]
    update_status()  # Update status after broadcasting

# Function to handle each client connection
def handle_client(client_socket):
    try:
        # Receive the username first
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username

        # Send Message of the Day (MOTD) to the newly connected client
        motd = add_timestamp(f"Welcome {username}!\nNumber of online users: {len(clients)}\nOnline users: " + ", ".join(clients.values()) + "\n")
        client_socket.send(motd.encode('utf-8'))

        # Notify everyone that a new user has joined
        join_message = f"{username} has joined the chat!"
        chat_box.insert(END, add_timestamp(join_message) + "\n")
        broadcast(join_message, client_socket)
        update_status()

        # Handle messages from this client
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                formatted_message = f"{username}: {message}"
                chat_box.insert(END, add_timestamp(formatted_message) + "\n")
                broadcast(formatted_message, client_socket)
    except:
        # Handle client disconnect
        leave_message = f"{clients[client_socket]} has left the chat."
        chat_box.insert(END, add_timestamp(leave_message) + "\n")
        broadcast(leave_message)
        client_socket.close()
        del clients[client_socket]
        update_status()

# Function to start the server
def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    chat_box.insert(END, f"Server started on {ip}:{port}\nWaiting for clients to connect...\n")
    update_status()

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Function to send server messages
def send_message():
    message = msg_entry.get()
    if message:
        timestamped_message = add_timestamp(f"Server: {message}")
        chat_box.insert(END, timestamped_message + "\n")
        broadcast(f"Server: {message}")  # Broadcast without adding a second timestamp
        msg_entry.delete(0, END)

# Update server status in the GUI
def update_status():
    num_clients = len(clients)
    if num_clients == 0:
        status_label.config(text="Status: Waiting for clients", fg="blue")
    else:
        status_label.config(text=f"Status: {num_clients} online", fg="green")

# Setting up the server GUI
def setup_gui(ip, port):
    global chat_box, msg_entry, status_label

    # Main window setup
    window = Tk()
    window.title("CMSC 137 Lab 5 Activity (Server)")

    # Header frame with connection information
    header_frame = Frame(window)
    header_frame.pack(fill='x', padx=5, pady=5)

    Label(header_frame, text="Your Entered Address:", anchor='w').grid(row=0, column=0, sticky='w')
    Label(header_frame, text=ip, anchor='w').grid(row=0, column=1, sticky='w')
    Label(header_frame, text="Your Entered Port Number:", anchor='w').grid(row=1, column=0, sticky='w')
    Label(header_frame, text=port, anchor='w').grid(row=1, column=1, sticky='w')
    status_label = Label(header_frame, text="Status: Waiting for clients", fg="blue", anchor='w')
    status_label.grid(row=2, column=0, columnspan=2, sticky='w')

    # Chat display area
    chat_box = Text(window, height=15, width=50)
    chat_box.pack(padx=5, pady=5)

    # Message entry and send button
    msg_entry = Entry(window, width=40)
    msg_entry.pack(side='left', padx=(5, 0), pady=5)
    send_button = Button(window, text="Send", command=send_message)
    send_button.pack(side='left', padx=(5, 5), pady=5)

    threading.Thread(target=start_server, args=(ip, port), daemon=True).start()
    window.mainloop()

if __name__ == "__main__":
    # Prompt for IP and Port
    root = Tk()
    root.withdraw()  # Hide the root window
    ip = simpledialog.askstring("Server IP", "Enter IP Address for the server:", initialvalue="127.0.0.1")
    port = simpledialog.askinteger("Port", "Enter Port Number for the server:", initialvalue=12345)
    root.destroy()

    # Start the GUI with the entered IP and Port
    setup_gui(ip, port)
