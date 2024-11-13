import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

# Server configuration
clients = {}

# FUNCTIONS
''' Add a timestamp to messages '''
def add_timestamp():
    return datetime.now().strftime('%b %d, %Y - %I:%M %p')

''' Broadcast messages to all clients except the sender '''
def broadcast(message, sender_socket=None):
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]


def handle_client(client_socket):
    try:
        # Receive the username from client and add it to dictionary
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username

        # Update the online users list only once when the client joins
        update_online_users()

        # Notify all clients that a new user has joined
        join_message = f"{username} has joined the chat!"
        display_message(join_message, "System")
        broadcast(join_message, client_socket)

        # Continuously listen for messages from the client
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                formatted_message = f"{username}: {message}"
                display_message(formatted_message, username)
                broadcast(formatted_message, client_socket)
    except:
        # Handle client disconnection
        if client_socket in clients:
            leave_message = f"{clients[client_socket]} has left the chat."
            display_message(leave_message, "System")
            broadcast(leave_message)
            client_socket.close()
            del clients[client_socket]
            update_online_users()  # Update online users after removing the client


''' Send the updated list of online users to all clients '''
def update_online_users():
    # Create a comma-separated list of usernames
    user_list = ",".join(clients.values())
    # Send this list to all clients without any prefix
    for client in clients.keys():
        try:
            client.send(user_list.encode('utf-8'))
        except:
            client.close()
            del clients[client]

''' Display messages in the GUI '''
def display_message(message, sender):
    message_frame = tk.Frame(scrollable_frame, bg="#263859", pady=2)
    
    timestamp_label = tk.Label(message_frame, text=add_timestamp(), bg="#263859", fg="lightgray", font=("Helvetica", 8, "italic"))
    timestamp_label.pack(anchor="e" if sender == "Server" else "w")

    if sender == "Server":
        message_label = tk.Label(message_frame, text=message, bg="#3b4b67", fg="white", font=("Helvetica", 10), padx=10, pady=5, anchor="e", justify="right")
        message_label.pack(anchor="e")
        message_frame.pack(anchor="e", fill="x", pady=5)
    else:
        message_label = tk.Label(
            message_frame,
            text=message,
            bg="#4c5c77",
            fg="white",
            font=("Helvetica", 10),
            padx=10,
            pady=5,
            anchor="w",
            justify="left"
        )
        message_label.pack(anchor="w")
        message_frame.pack(anchor="w", fill="x", padx=(10, 230), pady=5)

    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

''' Start the server '''
def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    display_message(f"Server started on {ip}:{port}\nWaiting for clients to connect...", "System")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

''' Send server messages '''
def send_server_message():
    message = msg_text.get("1.0", tk.END).strip()
    if message:
        display_message(f"Server: {message}", "Server")
        broadcast(f"Server: {message}")
        msg_text.delete("1.0", tk.END)

''' Setting up the server GUI '''
def setup_gui(ip, port):
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

    # Chat display area with scrollable frame
    chat_frame = tk.Frame(window, bg="#263859")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Canvas and Scrollbar setup
    canvas = tk.Canvas(chat_frame, bg="#263859", borderwidth=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#263859")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=460)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Message entry box
    msg_text = tk.Text(window, width=50, height=1, font=("Helvetica", 11), bg="#3b4b67", fg="white", insertbackground="white", wrap="word", relief="flat", pady=4, padx=4)
    msg_text.pack(side='left', padx=(10, 0), pady=0)
    msg_text.bind("<Return>", lambda event: send_server_message(event))
    msg_text.bind("<Shift-Return>", lambda event: msg_text.insert(tk.END, "\n"))

    # Send button
    send_button = tk.Button(
        window, text="Send", command=send_server_message,
        font=("Helvetica", 10, "bold"), bg="#4c5c77", fg="white",
        activebackground="#3b4b67", relief="flat", width=10, height=1
    )
    send_button.pack(side='left', padx=(10, 10), pady=10)

    threading.Thread(target=start_server, args=(ip, port), daemon=True).start()
    window.mainloop()

''' Main setup '''
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ip = simpledialog.askstring("Server IP", "Enter IP Address for the server:", initialvalue="127.0.0.1")
    if ip is None:  # Exit if "Cancel" is pressed
        exit()
    port = simpledialog.askinteger("Port", "Enter Port Number for the server:", initialvalue=12345)
    if port is None:  # Exit if "Cancel" is pressed
        exit()
    root.destroy()

    setup_gui(ip, port)