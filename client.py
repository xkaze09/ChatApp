import socket
import threading
from tkinter import Tk, Text, Entry, Button, END, simpledialog

# Server configuration
IP = '127.0.0.1'
PORT = 12345

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                chat_box.insert(END, f"{message}\n")
                chat_box.see(END)
        except:
            break

# Function to send client messages
def send_message():
    message = msg_entry.get()
    if message:
        chat_box.insert(END, f"{username}: {message}\n")
        client_socket.send(message.encode('utf-8'))
        msg_entry.delete(0, END)

# Setting up the client GUI
def setup_gui():
    global chat_box, msg_entry
    window = Tk()
    window.title("CMSC 137 Lab 5 Activity (Client)")

    chat_box = Text(window, height=15, width=50)
    chat_box.pack()

    msg_entry = Entry(window, width=50)
    msg_entry.pack()
    msg_entry.bind("<Return>", lambda event: send_message())

    send_button = Button(window, text="Send", command=send_message)
    send_button.pack()

    threading.Thread(target=receive_messages, daemon=True).start()
    window.mainloop()

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

# Prompt for a username when starting the client
username = simpledialog.askstring("Username", "Please enter a username:")
client_socket.send(username.encode('utf-8'))  # Send username to the server

setup_gui()
