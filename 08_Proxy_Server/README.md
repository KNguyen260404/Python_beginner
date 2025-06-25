# Proxy Server

A Python application with a graphical user interface that implements a fully functional HTTP/HTTPS proxy server with domain blocking and caching capabilities.

## Features

- **HTTP/HTTPS Proxy**: Supports both HTTP and HTTPS protocols
- **Domain Blocking**: Block specific domains from being accessed
- **Response Caching**: Cache responses to improve performance
- **Request Logging**: Log all requests with status codes and timestamps
- **Multithreaded**: Handle multiple connections simultaneously
- **User-friendly Interface**: Clean PyQt5 GUI with tabbed interface

## Requirements

- Python 3.6+
- PyQt5
- Standard library modules (socket, ssl, http.server, etc.)

## Installation

1. Install the required packages:

```bash
pip install PyQt5
```

2. Run the application:

```bash
python proxy_server.py
```

## Usage

### Starting the Proxy Server

1. Open the application
2. Configure the host (default: 127.0.0.1) and port (default: 8080)
3. Click "Start Server"
4. Configure your browser or system to use the proxy:
   - Proxy address: The host you configured (e.g., 127.0.0.1)
   - Proxy port: The port you configured (e.g., 8080)

### Domain Blocking

1. Go to the "Settings" tab
2. Enter a domain name (e.g., example.com) in the "Domain" field
3. Click "Block Domain"
4. The domain and all its subdomains will be blocked

### Caching

1. Go to the "Settings" tab
2. Enable or disable caching using the checkbox
3. Set the cache directory if needed
4. Use "Clear Cache" to remove all cached responses

## How It Works

The application works by:

1. Acting as an intermediary between clients (browsers) and servers
2. Intercepting HTTP/HTTPS requests from clients
3. Forwarding requests to the target servers
4. Returning responses back to clients
5. Optionally blocking requests to specific domains
6. Optionally caching responses for future requests

For HTTPS connections, the proxy uses the CONNECT method to establish a tunnel between the client and server, allowing encrypted traffic to pass through.

## Limitations

- The proxy does not support authentication
- HTTPS connections are tunneled rather than inspected (no HTTPS content filtering)
- The cache does not respect cache control headers from servers

## Security Considerations

- This proxy is intended for educational purposes and personal use
- Running a proxy server may expose your network to security risks
- Always run the proxy on a trusted network and limit access to trusted clients

## Future Improvements

- Add user authentication
- Support for proxy auto-configuration (PAC) files
- HTTPS content inspection (with custom CA certificates)
- Bandwidth throttling
- Advanced filtering rules
- Export logs and statistics 