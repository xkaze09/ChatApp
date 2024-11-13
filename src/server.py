import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

# Server configuration
clients = {}
server_socket = None
server_running = False  # Flag to track server status
lock = threading.Lock()  # Lock to manage access to shared resources

# FUNCTIONS
def add_timestamp():
    return datetime.now().strftime('%b %d, %Y - %I:%M %p')

def broadcast(message, sender_socket=None):
    def broadcast_thread():
        with lock:
            for client in list(clients.keys()):
                if client != sender_socket:
                    try:
                        client.send(message.encode('utf-8'))
                    except:
                        client.close()
                        del clients[client]
    threading.Thread(target=broadcast_thread, daemon=True).start()

def handle_client(client_socket):
    try:
        username = client_socket.recv(1024).decode('utf-8')
        with lock:
            clients[client_socket] = username
        update_online_users()
        join_message = f"{username} has joined the chat!"
        display_message_thread(join_message, "System")
        broadcast(join_message, client_socket)

        while server_running:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                formatted_message = f"{username}: {message}"
                display_message_thread(formatted_message, username)
                broadcast(formatted_message, client_socket)
    except:
        pass
    finally:
        with lock:
            if client_socket in clients:
                leave_message = f"{clients[client_socket]} has left the chat."
                display_message_thread(leave_message, "System")
                broadcast(leave_message)
                client_socket.close()
                del clients[client_socket]
                update_online_users()

def update_online_users():
    user_list = ",".join(clients.values())
    with lock:
        for client in clients.keys():
            try:
                client.send(user_list.encode('utf-8'))
            except:
                client.close()
                del clients[client]

def display_message_thread(message, sender):
    window.after(0, display_message, message, sender)

def display_message(message, sender):
    message_frame = tk.Frame(scrollable_frame, bg="#263859", pady=2)
    timestamp_label = tk.Label(message_frame, text=add_timestamp(), bg="#263859", fg="lightgray", font=("Helvetica", 8, "italic"))
    timestamp_label.pack(anchor="e" if sender == "Server" else "w")
    message_label = tk.Label(
        message_frame,
        text=message,
        bg="#3b4b67" if sender == "Server" else "#4c5c77",
        fg="white",
        font=("Helvetica", 10),
        padx=10,
        pady=5,
        anchor="e" if sender == "Server" else "w",
        justify="right" if sender == "Server" else "left"
    )
    message_label.pack(anchor="e" if sender == "Server" else "w")
    message_frame.pack(anchor="e" if sender == "Server" else "w", fill="x", padx=(10, 230) if sender != "Server" else 0, pady=5)
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

def start_server(ip, port):
    global server_socket, server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))
    server_socket.listen()
    display_message_thread(f"Server started on {ip}:{port}\nWaiting for clients to connect...", "System")
    
    while server_running:
        try:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
        except OSError:
            break  # Server socket closed, exit loop

def stop_server():
    def stop_server_thread():
        global server_socket, server_running
        server_running = False
        with lock:
            # Disconnect all clients
            for client_socket in list(clients.keys()):
                try:
                    client_socket.send("Server is shutting down.".encode('utf-8'))
                    client_socket.close()
                except:
                    pass
                del clients[client_socket]  # Remove client from list
            window.after(0, lambda: display_message("All clients have been disconnected.", "System"))
        
        if server_socket:
            try:
                server_socket.shutdown(socket.SHUT_RDWR)  # Gracefully close socket
            except:
                pass
            server_socket.close()
            server_socket = None
        window.after(0, lambda: display_message("Server stopped.", "System"))

    threading.Thread(target=stop_server_thread, daemon=True).start()

def toggle_server(ip, port, button):
    global server_running
    if server_running:
        stop_server()
        button.config(text="Start Server")
    else:
        server_running = True
        threading.Thread(target=start_server, args=(ip, port), daemon=True).start()
        button.config(text="Stop Server")

def send_server_message(event=None):
    message = msg_text.get("1.0", tk.END).strip()
    if message:
        display_message_thread(f"Server: {message}", "Server")
        broadcast(f"Server: {message}")
        msg_text.delete("1.0", tk.END)

def setup_gui(ip, port):
    global window, canvas, scrollable_frame, msg_text

    window = tk.Tk()
    window.title("Chat Server")
    window.configure(bg="#1f2a44")
    window.resizable(False, False)

    header_frame = tk.Frame(window, bg="#1f2a44", pady=5)
    header_frame.pack(fill='x', padx=10, pady=5)

    tk.Label(header_frame, text="Server IP Address:", font=("Helvetica", 10), bg="#1f2a44", fg="white").grid(row=0, column=0, sticky='e', padx=5, pady=2)
    tk.Label(header_frame, text=ip, font=("Helvetica", 10), bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=0, column=1, sticky='w', padx=5, pady=2)
    tk.Label(header_frame, text="Server Port Number:", font=("Helvetica", 10), bg="#1f2a44", fg="white").grid(row=1, column=0, sticky='e', padx=5, pady=2)
    tk.Label(header_frame, text=port, font=("Helvetica", 10), bg="#3b4b67", fg="white", width=20, anchor='w').grid(row=1, column=1, sticky='w', padx=5, pady=2)

    chat_frame = tk.Frame(window, bg="#263859")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

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

    msg_text = tk.Text(window, width=50, height=1, font=("Helvetica", 11), bg="#3b4b67", fg="white", insertbackground="white", wrap="word", relief="flat", pady=4, padx=4)
    msg_text.pack(side='left', padx=(10, 0), pady=0)
    msg_text.bind("<Return>", lambda event: send_server_message(event))
    msg_text.bind("<Shift-Return>", lambda event: msg_text.insert(tk.END, "\n"))

    send_button = tk.Button(
        window, text="Send", command=send_server_message,
        font=("Helvetica", 10, "bold"), bg="#4c5c77", fg="white",
        activebackground="#3b4b67", relief="flat", width=10, height=1
    )
    send_button.pack(side='left', padx=(10, 10), pady=10)

    toggle_button = tk.Button(
        window, text="Start Server", command=lambda: toggle_server(ip, port, toggle_button),
        font=("Helvetica", 10, "bold"), bg="#4c5c77", fg="white",
        activebackground="#3b4b67", relief="flat", width=10, height=1
    )
    toggle_button.pack(side='left', padx=(10, 10), pady=10)

    window.mainloop()

if __name__ == "__main__":
    # Prompt for server IP and port
    root = tk.Tk()
    root.withdraw()
    
    ip = simpledialog.askstring("Server IP", "Enter IP Address for the server:", initialvalue="127.0.0.1")
    if ip is None:
        root.destroy()
        exit()  # Exit if "Cancel" is clicked on the IP prompt
    
    port = simpledialog.askinteger("Port", "Enter Port Number for the server:", initialvalue=12345)
    if port is None:
        root.destroy()
        exit()  # Exit if "Cancel" is clicked on the Port prompt
    
    root.destroy()

    # Setup the GUI
    setup_gui(ip, port)
