import socket
import threading
from tkinter import Tk, Text, Entry, Button, END

# Server configuration
IP = '127.0.0.1'
PORT = 12345
clients = {}  # Dictionary to store client sockets and their usernames

# Function to broadcast messages to all clients except the sender
def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:  # Exclude the sender from receiving their own message
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]

# Function to handle each client connection
def handle_client(client_socket):
    try:
        # Receive the username first
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username  # Store the username

        # Send welcome message to the newly joined client
        welcome_message = f"Welcome {username}! You have joined the chat."
        client_socket.send(welcome_message.encode('utf-8'))

        # Send the list of currently online users to the newly joined client
        online_users = "Users currently online: " + ", ".join(clients.values())
        client_socket.send(online_users.encode('utf-8'))

        # Notify everyone that a new user has joined
        join_message = f"{username} has joined the chat!"
        chat_box.insert(END, join_message + "\n")
        broadcast(join_message, client_socket)

        # Handle messages from this client
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                formatted_message = f"{username}: {message}"
                chat_box.insert(END, formatted_message + "\n")
                broadcast(formatted_message, client_socket)
    except:
        # Handle client disconnect
        leave_message = f"{clients[client_socket]} has left the chat."
        chat_box.insert(END, leave_message + "\n")
        broadcast(leave_message)
        client_socket.close()
        del clients[client_socket]

# Function to start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    chat_box.insert(END, "Waiting for clients to connect...\n")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Function to send server messages
def send_message():
    message = msg_entry.get()
    if message:
        chat_box.insert(END, f"Server: {message}\n")
        broadcast(f"Server: {message}")
        msg_entry.delete(0, END)

# Setting up the server GUI
def setup_gui():
    global chat_box, msg_entry
    window = Tk()
    window.title("Chat Server Version 1.0")

    chat_box = Text(window, height=15, width=50)
    chat_box.pack()

    msg_entry = Entry(window, width=50)
    msg_entry.pack()
    msg_entry.bind("<Return>", lambda event: send_message())

    send_button = Button(window, text="Send", command=send_message)
    send_button.pack()

    threading.Thread(target=start_server, daemon=True).start()
    window.mainloop()

if __name__ == "__main__":
    setup_gui()
