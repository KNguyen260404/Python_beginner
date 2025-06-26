# Network Programming Projects

This directory contains a collection of 15 networking projects implemented in Python, each demonstrating different aspects of network programming with various user interfaces.

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

### 9. UDP Group Chat (09_UDP_Group_Chat)
A group chat application using UDP multicast for efficient group communication.

### 10. Email Automation (10_Email_Automation)
Tools for automating email tasks including bulk sending and template-based emails.

### 11. Remote Control (11_Remote_Control)
A secure remote control application with encrypted communications and authentication.

### 12. REST API (12_REST_API)
A complete REST API implementation with authentication, data models, and documentation.

### 13. Web Crawler (13_Web_Crawler)
A web crawler for extracting and analyzing data from websites with customizable parsers.

### 14. Simple DNS (14_Simple_DNS)
A simple DNS server and client implementation for domain name resolution.

### 15. VoIP Application (15_VoIP_Application)
A Voice over IP application with real-time audio communication and text chat capabilities.

## Requirements

All required packages are listed in the `requirements.txt` file. Install them using:

```bash
pip install -r requirements.txt
```

Additionally, each project may have its own specific requirements file.

## Running the Projects

Each project directory contains its own README file with specific instructions. In general:

1. Navigate to the project directory
2. Install any project-specific dependencies
3. Run the main Python file

### Examples:

#### Chat Application
```bash
cd 01_Chat_App
python server.py  # In one terminal
python client.py  # In another terminal
```

#### Web Server
```bash
cd 02_Web_Server
python app.py
# Access at http://localhost:5000
```

#### File Transfer
```bash
cd 03_File_Transfer
python server.py  # In one terminal
python client.py  # In another terminal
```

#### VoIP Application
```bash
cd 15_VoIP_Application
pip install -r requirements.txt  # Install PyAudio
python server.py  # In one terminal
python client.py  # In another terminal
```

## Learning Objectives

These projects demonstrate various networking concepts:

- Socket programming (TCP/UDP)
- Client-server architecture
- HTTP/HTTPS protocols
- Multithreading in network applications
- GUI development with PyQt5 and Tkinter
- Network monitoring and analysis
- Web development with Flask
- Proxy servers and tunneling
- API development and authentication
- Voice over IP and real-time communication
- DNS protocol implementation
- Web crawling and data extraction

## Notes

- Some applications may require administrator/root privileges to access low-level network features
- The projects are designed for educational purposes and may not be production-ready
- All projects include error handling and user-friendly interfaces 