'''
Authors: Kristina Celis & Christian Salinas

Description: server.py implements the server-side functionality
of the chat app. It listens for incoming client connections, 
handles client messages, and broadcasts these messages to other 
clients in real-time.
'''

# IMPORTS
import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
import crc_functions  # Import the CRC functions

# Dictionary to keep track of connected clients with their usernames
clients = {}

# UTILITY FUNCTIONS
def add_timestamp():
    ''' Add a timestamp to messages '''
    return datetime.now().strftime('%b %d, %Y - %I:%M %p')

def broadcast(message, sender_socket=None):
    ''' Broadcast messages to all clients except the sender '''
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                # Ensure the message has the correct format
                if ":" in message:
                    client.send(message.encode('utf-8'))
                else:
                    print(f"Invalid message format: {message}")
            except Exception as e:
                print(f"Error broadcasting to a client: {e}")
                client.close()
                del clients[client]


# CLIENT HANDLER FUNCTIONS
def handle_client(client_socket):
    ''' Handles communication with a connected client '''
    try:
        # Receive and store username
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        update_online_users()  # Update client list for all users

        # Notify others that a new user has joined
        join_message = f"{username} has joined the chat!"
        display_message(join_message, "System")
        broadcast(join_message, client_socket)

        # Continuously listen for messages from the client
        while True:
            try:
                received_message = client_socket.recv(1024).decode('utf-8')
                if received_message:
                    sender, message_with_crc = received_message.split(":", 1)
                    generator = "10011"

                    if crc_functions.validate_crc(message_with_crc, generator):
                        binary_message = message_with_crc[:-4]
                        original_message = ''.join(
                            chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8)
                        )
                        formatted_message = f"{sender}: {original_message}"
                        display_message(formatted_message, sender)
                        broadcast(formatted_message, client_socket)
                    else:
                        error_message = f"Corrupted message from {sender}."
                        display_message(error_message, "System")
                        client_socket.send(f"System:{error_message}".encode('utf-8'))
            except Exception as e:
                display_message(f"Error processing message: {e}", "System")
                break
    except Exception as e:
        display_message(f"Client handler error: {e}", "System")
    finally:
        # Cleanup on disconnection
        if client_socket in clients:
            leave_message = f"{clients[client_socket]} has left the chat."
            display_message(leave_message, "System")
            broadcast(leave_message)
            del clients[client_socket]
            client_socket.close()
            update_online_users()

def update_online_users():
    ''' Send the updated list of online users to all clients '''
    user_list = ",".join(clients.values())
    for client in clients.keys():
        try:
            client.send(user_list.encode('utf-8'))
        except:
            client.close()
            del clients[client]

# SERVER MANAGEMENT FUNCTIONS
def start_server(ip, port):
    ''' Initializes and starts the server '''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    display_message(f"Server started on {ip}:{port}\nWaiting for clients to connect...", "System")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

def send_server_message():
    ''' Send server messages to all clients '''
    global msg_text
    message = msg_text.get("1.0", tk.END).strip()
    if message:
        # Convert server message to binary
        binary_message = crc_functions.string_to_binary(message)

        # Compute CRC for the message using the generator polynomial
        generator = "10011"  # x^4 + x + 1
        checksum = crc_functions.crc(binary_message, generator)

        # Append CRC to the binary message
        message_with_crc = binary_message + checksum

        # Introduce a 5% chance of error
        message_with_crc = crc_functions.introduce_error(message_with_crc)

        # Log the transmitted message for debugging
        print(f"Server > {message}")
        print(f"Sent: {message_with_crc}")

        # Encode the message with CRC and broadcast it
        formatted_message = f"Server:{message_with_crc}"
        display_message(message, "Server")
        broadcast(formatted_message)
        msg_text.delete("1.0", tk.END)

# GUI DISPLAY FUNCTIONS
def display_message(message, sender):
    ''' Display messages in the GUI '''
    message_frame = tk.Frame(scrollable_frame, bg="#263859", pady=2)
    
    timestamp_label = tk.Label(message_frame, text=add_timestamp(), bg="#263859", fg="lightgray", font=("Helvetica", 8, "italic"))
    timestamp_label.pack(anchor="e" if sender == "Server" else "w")

    if sender == "Server":
        message_label = tk.Label(message_frame, text=message, bg="#3b4b67", fg="white", font=("Helvetica", 10), padx=10, pady=5)
        message_label.pack(anchor="e")
        message_frame.pack(anchor="e", fill="x", pady=5)
    else:
        message_label = tk.Label(message_frame, text=message, bg="#4c5c77", fg="white", font=("Helvetica", 10), padx=10, pady=5)
        message_label.pack(anchor="w")
        message_frame.pack(anchor="w", fill="x", padx=(10, 230), pady=5)

    # Update the canvas to scroll to the bottom for each new message
    canvas.update_idletasks()
    canvas.yview_moveto(1.0) 

def setup_gui(ip, port):
    ''' Setting up the server GUI '''
    global canvas, scrollable_frame, msg_text

    # Main window setup
    window = tk.Tk()
    window.title("Chat Server")
    window.configure(bg="#1f2a44")
    window.resizable(False, False)

    # Header frame with connection information
    header_frame = tk.Frame(window, bg="#1f2a44", pady=5)
    header_frame.pack(fill='x', padx=10, pady=5)

    tk.Label(header_frame, text="Server IP Address:", font=("Helvetica", 10), bg="#1f2a44", fg="white").grid(row=0, column=0, sticky='e', padx=5, pady=2)
    tk.Label(header_frame, text=ip, font=("Helvetica", 10), bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=0, column=1, sticky='w', padx=5, pady=2)
    tk.Label(header_frame, text="Server Port Number:", font=("Helvetica", 10), bg="#1f2a44", fg="white").grid(row=1, column=0, sticky='e', padx=5, pady=2)
    tk.Label(header_frame, text=port, font=("Helvetica", 10), bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=1, column=1, sticky='w', padx=5, pady=2)

    # Chat display area
    chat_frame = tk.Frame(window, bg="#263859")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Canvas and Scrollbar setup
    canvas = tk.Canvas(chat_frame, bg="#263859", borderwidth=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#263859")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=460)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Message entry box
    msg_text = tk.Text(window, width=50, height=1, font=("Helvetica", 11), bg="#3b4b67", fg="white", insertbackground="white", wrap="word", relief="flat", pady=4, padx=4)
    msg_text.pack(side='left', padx=(10, 0), pady=0)
    msg_text.bind("<Return>", lambda event: send_server_message())
    msg_text.bind("<Shift-Return>", lambda event: msg_text.insert(tk.END, "\n"))

    # Send button
    send_button = tk.Button(
        window, text="Send", command=send_server_message,
        font=("Helvetica", 10, "bold"), bg="#4c5c77", fg="white",
        activebackground="#3b4b67", relief="flat", width=10, height=1
    )
    send_button.pack(side='left', padx=(10, 10), pady=10)

    # Start server in a separate thread to keep GUI responsive
    threading.Thread(target=start_server, args=(ip, port), daemon=True).start()
    window.mainloop()


# PROGRAM ENTRY POINT
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    # Prompt user to input server IP and Port
    ip = simpledialog.askstring("Server IP", "Enter IP Address for the server:", initialvalue="127.0.0.1")
    if ip is None:  # Exit if "Cancel" is pressed
        exit()
    port = simpledialog.askinteger("Port", "Enter Port Number for the server:", initialvalue=12345)
    if port is None:  # Exit if "Cancel" is pressed
        exit()
    root.destroy()

    # Launch GUI
    setup_gui(ip, port)
