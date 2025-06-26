# Simple DNS Project

A Python implementation of a simple DNS server and client that demonstrates the Domain Name System protocol. This project includes both a DNS server that can resolve domain names from a local database or forward requests to upstream DNS servers, and a DNS client for querying DNS records.

## Features

- **DNS Server**:
  - Local DNS record database
  - Caching of DNS responses
  - Forwarding to upstream DNS servers
  - Support for common DNS record types (A, AAAA, MX, CNAME, TXT, NS)
  - Basic DNS zone management
  - Query logging and statistics

- **DNS Client**:
  - Command-line interface for DNS queries
  - Support for different record types
  - Detailed response information
  - Query timing statistics
  - Custom DNS server selection

- **DNS Protocol**:
  - DNS message encoding/decoding
  - Support for standard DNS message format
  - Error handling for malformed DNS messages

## Project Structure

- `dns_server.py`: Main DNS server implementation
- `dns_client.py`: DNS client implementation
- `dns_message.py`: DNS protocol message encoding/decoding
- `dns_resolver.py`: DNS resolution logic
- `dns_cache.py`: DNS response caching
- `dns_records.py`: DNS record types and database
- `dns_zone.py`: DNS zone management
- `dns_config.py`: Configuration management
- `dns_utils.py`: Utility functions
- `data/`: Directory for DNS zone files and configuration
  - `zones/`: DNS zone files
  - `config.json`: Server configuration
  - `records.db`: Sample DNS records database

## Requirements

- Python 3.8+
- No external dependencies for core functionality

## Installation

1. Clone the repository
2. Navigate to the project directory
3. No additional installation required for basic functionality

## Usage

### DNS Server

Start the DNS server:

```bash
python dns_server.py --port 53 --config data/config.json
```

Options:
- `--port`: Port to listen on (default: 53)
- `--config`: Path to configuration file
- `--foreground`: Run in foreground mode
- `--debug`: Enable debug logging

### DNS Client

Query a DNS record:

```bash
python dns_client.py example.com --type A --server 127.0.0.1
```

Options:
- `--type`: Record type (A, AAAA, MX, CNAME, TXT, NS)
- `--server`: DNS server to query (default: system DNS)
- `--port`: DNS server port (default: 53)
- `--timeout`: Query timeout in seconds
- `--verbose`: Show detailed information

## DNS Record Database

The DNS server can use a local database of records stored in JSON format:

```json
{
  "example.com": {
    "A": ["93.184.216.34"],
    "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"],
    "MX": ["10 mail.example.com"],
    "TXT": ["v=spf1 -all"]
  }
}
```

## DNS Protocol

This project implements a simplified version of the DNS protocol as defined in RFC 1035. The DNS message format includes:

- Header section
- Question section
- Answer section
- Authority section
- Additional section

## Educational Purpose

This project is designed for educational purposes to understand:

1. How DNS works at the protocol level
2. DNS resolution process
3. Network programming with UDP sockets
4. Binary protocol implementation in Python

## License

MIT License 