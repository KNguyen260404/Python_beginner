# Remote Control Application

A Python-based remote control application that allows users to remotely manage and control computers over a network. This project includes both server and client components for secure remote command execution, file transfer, and system monitoring.

## Features

- **Remote Command Execution**: Execute shell commands on remote machines
- **File Transfer**: Upload and download files between client and server
- **System Monitoring**: Monitor CPU, memory, disk usage, and running processes
- **Screen Capture**: Take screenshots of the remote computer
- **Secure Communication**: Encrypted communication using SSL/TLS
- **Authentication**: Username and password authentication for security
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Project Structure

```
11_Remote_Control/
├── server.py            # Server application
├── client.py            # Client application
├── common.py            # Shared utilities and constants
├── requirements.txt     # Required Python packages
├── certs/               # SSL/TLS certificates directory
│   ├── generate_cert.py # Script to generate self-signed certificates
│   └── README.md        # Instructions for certificate generation
└── README.md            # This file
```

## Requirements

- Python 3.6+
- Required packages (install using `pip install -r requirements.txt`):
  - `psutil` - For system monitoring
  - `pillow` - For screenshot functionality
  - `cryptography` - For encryption
  - `paramiko` - For SSH functionality (optional)

## Setup

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Generate SSL/TLS certificates:
   ```
   cd certs
   python generate_cert.py
   ```
4. Start the server on the computer you want to control:
   ```
   python server.py
   ```
5. Connect from the client on another computer:
   ```
   python client.py
   ```

## Security Considerations

- Always use strong passwords for authentication
- Keep your SSL/TLS certificates secure
- Be careful about who you give remote access to
- Consider using a VPN for additional security
- Regularly update the software to patch security vulnerabilities

## Usage Examples

### Starting the Server

```bash
python server.py --port 8000 --password your_secure_password
```

### Connecting with the Client

```bash
python client.py --host 192.168.1.100 --port 8000
```

### Remote Command Execution

```
> execute ls -la
total 32
drwxr-xr-x  6 user  staff   192 Oct 15 14:30 .
drwxr-xr-x  8 user  staff   256 Oct 15 14:28 ..
-rw-r--r--  1 user  staff  1234 Oct 15 14:30 client.py
-rw-r--r--  1 user  staff   567 Oct 15 14:29 common.py
-rw-r--r--  1 user  staff   345 Oct 15 14:29 requirements.txt
-rw-r--r--  1 user  staff  2345 Oct 15 14:30 server.py
```

### File Transfer

```
> upload local_file.txt remote_file.txt
File uploaded successfully.

> download remote_file.txt downloaded_file.txt
File downloaded successfully.
```

### System Monitoring

```
> sysinfo
CPU: 23% | Memory: 4.2GB/16GB (26%) | Disk: 120GB/500GB (24%)
```

## License

This project is for educational purposes only. Use responsibly and in accordance with all applicable laws and regulations. 