# Multi-Client Chat Application

## Project Overview

This is a multi-client chat application built using Python. It demonstrates core networking concepts in a client-server architecture. Each client can connect to the server with a unique username, send messages, view who is online, and receive notifications when other users join or leave the chat.

## Key Features

- **Client-Server Architecture**: Centralized server managing multiple client connections.
- **Username Identification**: Unique usernames for each client to distinguish users in the chat.
- **Message Broadcasting**: Server broadcasts messages, join notifications, and leave notifications to all clients.
- **GUI for Clients and Server**: A graphical interface built with `tkinter` for displaying messages and sending inputs.
- **Online User List**: New users receive a welcome message and a list of online users.

## Technology Stack

- **Python**: Main programming language.
- **Socket Programming**: `socket` library used for client-server communication.
- **Concurrency**: `threading` library used to handle multiple clients simultaneously.
- **GUI**: `tkinter` library used to create a simple graphical interface.

## Getting Started

### Prerequisites

- Python 3.x installed on your machine.

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/username/chat-application.git
    cd chat-application
    ```

2. Run the server:
    ```bash
    python server.py
    ```

3. Run the client:
    ```bash
    python client.py
    ```

   - Each client will be prompted to enter a unique username upon connecting.

## Usage

1. Start the server by running `server.py`.
2. Open multiple instances of `client.py` to simulate different users joining the chat.
3. Each client enters a username, receives a welcome message, and sees the list of online users.
4. Users can send messages, which will be broadcasted to all connected clients. Notifications are also displayed when users join or leave.

## Learning Objectives

This project was developed as part of a Data Communications and Networking course to demonstrate:

- **Client-Server Architecture**: Understanding and implementing a centralized server with multiple clients.
- **Socket Programming**: Establishing reliable TCP connections using Python’s `socket` library.
- **Concurrency**: Managing multiple connections with threading.
- **Broadcasting**: Sending messages to multiple clients.
- **Session Management**: Managing unique client sessions with usernames.

## Troubleshooting

- **Duplicate Messages**: Ensure the server’s `broadcast()` function excludes the sender to prevent clients from receiving their own messages back.
- **Disconnected Clients**: Use exception handling to remove clients from the list upon disconnection.

## Future Improvements

- **Message Encryption**: Add encryption for message privacy.
- **Enhanced GUI**: Improve the user interface for a more polished experience.
- **Persistent User Sessions**: Store usernames persistently for reconnecting users.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was developed for educational purposes in a Data Communications and Networking course to provide practical experience with real-world networking concepts.
