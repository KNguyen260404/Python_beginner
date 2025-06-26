# UDP Group Chat Application

A feature-rich group chat application using UDP protocol with a PyQt5 graphical user interface. The application supports public messaging, private messaging, and group chats.

## Features

- **UDP Communication**: Efficient, connectionless communication using UDP protocol
- **Public Chat**: Broadcast messages to all connected users
- **Private Messaging**: Send direct messages to specific users
- **Group Chats**: Create and join chat groups
- **User List**: View all online users
- **Group List**: View available groups and member counts
- **Graphical Interface**: Modern PyQt5 interface with tabbed chats
- **Heartbeat System**: Automatic detection of inactive users

## Requirements

- Python 3.6+
- PyQt5
- Standard library modules (socket, json, threading, etc.)

## Installation

1. Install the required packages:

```bash
pip install PyQt5
```

2. Run the server:

```bash
python udp_group_chat_server.py [port]
```

3. Run the client:

```bash
python udp_group_chat_client.py [-s SERVER] [-p PORT] [-u USERNAME]
```

## Usage

### Server

Start the server by running `udp_group_chat_server.py`. By default, it listens on port 5000, but you can specify a different port as a command-line argument.

### Client

Start the client by running `udp_group_chat_client.py`. You can specify the server address, port, and username using command-line options:

- `-s` or `--server`: Server hostname or IP (default: 127.0.0.1)
- `-p` or `--port`: Server port (default: 5000)
- `-u` or `--username`: Your username

If you don't provide a username, you'll be prompted to enter one.

### Chat Commands

The application provides a graphical interface for all actions:

1. **Send Public Message**: Type in the "Main" tab and press Enter or click Send
2. **Join/Create Group**: Click "Join/Create Group" button and select or enter a group name
3. **Send Group Message**: Type in the group tab and press Enter or click Send
4. **Send Private Message**: Double-click a username in the user list and type in the private chat tab
5. **Leave Group**: Close the group tab

## Protocol Details

The application uses a simple JSON-based protocol for communication:

- **Registration**: `{"type": "register", "username": "name"}`
- **Public Message**: `{"type": "message", "content": "text", "target_type": "broadcast"}`
- **Group Message**: `{"type": "message", "content": "text", "target_type": "group", "target": "group_name"}`
- **Private Message**: `{"type": "message", "content": "text", "target_type": "private", "target": "username"}`
- **Join Group**: `{"type": "join_group", "group": "group_name"}`
- **Leave Group**: `{"type": "leave_group", "group": "group_name"}`
- **List Groups**: `{"type": "list_groups"}`
- **List Users**: `{"type": "list_users", "group": "group_name"}`
- **Heartbeat**: `{"type": "heartbeat"}`

## Architecture

The application consists of two main components:

1. **Server**: Handles message routing, group management, and client tracking
2. **Client**: Provides the user interface and communicates with the server

The client uses a multi-threaded architecture to separate the UI from network communication.

## Limitations

- UDP does not guarantee message delivery or order
- No message encryption or authentication
- No persistent message history
- Limited to local network or requires port forwarding for internet use

## Future Improvements

- Message encryption for privacy
- User authentication
- Persistent message history
- File sharing capabilities
- Custom user avatars and statuses
- Message read receipts 