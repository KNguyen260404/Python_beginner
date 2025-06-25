# Network Programming Projects

This directory contains a collection of 8 networking projects implemented in Python, each demonstrating different aspects of network programming with graphical user interfaces.

## Projects

### 1. Chat Application (01_Chat_App)
A client-server chat application with a PyQt5 GUI that supports public, private, and group messaging.

### 2. Web Server (02_Web_Server)
A Flask-based web server with HTML templates, static files, and an admin interface.

### 3. File Transfer (03_File_Transfer)
A client-server application for transferring files with progress tracking and a PyQt5 GUI.

### 4. Network Monitor (04_Network_Monitor)
A tool for monitoring network traffic, bandwidth usage, and connections with real-time graphs.

### 5. Port Scanner (05_Port_Scanner)
A network port scanner with various scanning methods (TCP, UDP, SYN) and a PyQt5 interface.

### 6. Packet Analyzer (06_Packet_Analyzer)
A packet capture and analysis tool using Scapy with protocol decoding and filtering.

### 7. Multithreaded Downloader (07_Multithreaded_Downloader)
A download accelerator that splits files into chunks for parallel downloading with a PyQt5 GUI.

### 8. Proxy Server (08_Proxy_Server)
An HTTP/HTTPS proxy server with domain blocking, caching, and request logging capabilities.

## Requirements

All required packages are listed in the `requirements.txt` file. Install them using:

```bash
pip install -r requirements.txt
```

## Running the Projects

Each project directory contains its own README file with specific instructions. In general:

1. Navigate to the project directory
2. Install any project-specific dependencies
3. Run the main Python file

For example:

```bash
cd 01_Chat_App
python server.py  # In one terminal
python client.py  # In another terminal
```

## Learning Objectives

These projects demonstrate various networking concepts:

- Socket programming
- Client-server architecture
- HTTP/HTTPS protocols
- Multithreading in network applications
- GUI development with PyQt5
- Network monitoring and analysis
- Web development with Flask
- Proxy servers and tunneling

## Notes

- Some applications may require administrator/root privileges to access low-level network features
- The projects are designed for educational purposes and may not be production-ready
- All projects include error handling and user-friendly interfaces 