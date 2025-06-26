#!/usr/bin/env python3
"""
DNS Utils - Utility functions for the DNS server and client

This module provides utility functions for working with DNS names,
IP addresses, and other DNS-related operations.
"""

import socket
import ipaddress
import time
import logging
from typing import List, Tuple, Optional, Union, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


def is_valid_domain(domain: str) -> bool:
    """
    Check if a domain name is valid
    
    Args:
        domain: Domain name to check
        
    Returns:
        bool: True if the domain is valid, False otherwise
    """
    if not domain:
        return False
    
    # Remove trailing dot if present
    if domain.endswith('.'):
        domain = domain[:-1]
    
    # Check length
    if len(domain) > 253:
        return False
    
    # Check each label
    labels = domain.split('.')
    for label in labels:
        # Check label length
        if len(label) < 1 or len(label) > 63:
            return False
        
        # Check label characters
        if not all(c.isalnum() or c == '-' for c in label):
            return False
        
        # Check that label doesn't start or end with a hyphen
        if label.startswith('-') or label.endswith('-'):
            return False
    
    return True


def is_valid_ip(ip: str) -> bool:
    """
    Check if an IP address is valid
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if the IP is valid, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_ipv4(ip: str) -> bool:
    """
    Check if an IPv4 address is valid
    
    Args:
        ip: IPv4 address to check
        
    Returns:
        bool: True if the IPv4 is valid, False otherwise
    """
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


def is_valid_ipv6(ip: str) -> bool:
    """
    Check if an IPv6 address is valid
    
    Args:
        ip: IPv6 address to check
        
    Returns:
        bool: True if the IPv6 is valid, False otherwise
    """
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ValueError:
        return False


def get_ip_version(ip: str) -> Optional[int]:
    """
    Get the IP version of an IP address
    
    Args:
        ip: IP address to check
        
    Returns:
        Optional[int]: 4 for IPv4, 6 for IPv6, None if invalid
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.version
    except ValueError:
        return None


def domain_to_reverse_ptr(ip: str) -> Optional[str]:
    """
    Convert an IP address to a reverse DNS pointer
    
    Args:
        ip: IP address to convert
        
    Returns:
        Optional[str]: Reverse DNS pointer, or None if invalid
    """
    try:
        return ipaddress.ip_address(ip).reverse_pointer
    except ValueError:
        return None


def is_subdomain(subdomain: str, domain: str) -> bool:
    """
    Check if a domain is a subdomain of another domain
    
    Args:
        subdomain: The potential subdomain
        domain: The parent domain
        
    Returns:
        bool: True if subdomain is a subdomain of domain, False otherwise
    """
    # Normalize domains
    subdomain = subdomain.lower()
    domain = domain.lower()
    
    # Remove trailing dots
    if subdomain.endswith('.'):
        subdomain = subdomain[:-1]
    if domain.endswith('.'):
        domain = domain[:-1]
    
    # Check if subdomain ends with domain
    return subdomain == domain or subdomain.endswith(f".{domain}")


def get_root_domain(domain: str) -> str:
    """
    Get the root domain of a domain
    
    Args:
        domain: Domain name
        
    Returns:
        str: Root domain
    """
    # Normalize domain
    domain = domain.lower()
    
    # Remove trailing dot
    if domain.endswith('.'):
        domain = domain[:-1]
    
    # Split into labels
    labels = domain.split('.')
    
    # If there are at least two labels, return the last two
    if len(labels) >= 2:
        return '.'.join(labels[-2:])
    
    # Otherwise, return the domain
    return domain


def get_system_nameservers() -> List[str]:
    """
    Get the system nameservers
    
    Returns:
        list: List of nameserver IP addresses
    """
    nameservers = []
    
    try:
        # Try to read /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if line.startswith('nameserver'):
                    parts = line.split()
                    if len(parts) >= 2 and is_valid_ip(parts[1]):
                        nameservers.append(parts[1])
    except Exception:
        pass
    
    # If no nameservers found, use default
    if not nameservers:
        nameservers = ['8.8.8.8', '8.8.4.4']
    
    return nameservers


def get_system_hostname() -> str:
    """
    Get the system hostname
    
    Returns:
        str: System hostname
    """
    try:
        return socket.gethostname()
    except Exception:
        return 'localhost'


def get_local_ip() -> str:
    """
    Get the local IP address
    
    Returns:
        str: Local IP address
    """
    try:
        # Create a socket to connect to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def format_time(seconds: float) -> str:
    """
    Format a time duration in seconds to a human-readable string
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.2f}s"
    else:
        hours = int(seconds / 3600)
        seconds = seconds % 3600
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{hours}h {minutes}m {seconds:.2f}s"


def format_ttl(ttl: int) -> str:
    """
    Format a TTL in seconds to a human-readable string
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        str: Formatted TTL string
    """
    if ttl < 60:
        return f"{ttl}s"
    elif ttl < 3600:
        minutes = ttl // 60
        seconds = ttl % 60
        if seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {seconds}s"
    elif ttl < 86400:
        hours = ttl // 3600
        minutes = (ttl % 3600) // 60
        if minutes == 0:
            return f"{hours}h"
        return f"{hours}h {minutes}m"
    else:
        days = ttl // 86400
        hours = (ttl % 86400) // 3600
        if hours == 0:
            return f"{days}d"
        return f"{days}d {hours}h"


def parse_ttl(ttl_str: str) -> int:
    """
    Parse a TTL string to seconds
    
    Args:
        ttl_str: TTL string (e.g., '1d', '2h30m', '5m30s')
        
    Returns:
        int: TTL in seconds
    """
    ttl = 0
    current_value = ''
    
    for c in ttl_str:
        if c.isdigit():
            current_value += c
        elif c in 'dhms':
            if current_value:
                value = int(current_value)
                if c == 'd':
                    ttl += value * 86400
                elif c == 'h':
                    ttl += value * 3600
                elif c == 'm':
                    ttl += value * 60
                elif c == 's':
                    ttl += value
                current_value = ''
        elif c.isspace():
            pass
        else:
            raise ValueError(f"Invalid character in TTL string: {c}")
    
    # Add any remaining value
    if current_value:
        ttl += int(current_value)
    
    return ttl


def is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is private
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if the IP is private, False otherwise
    """
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def is_loopback_ip(ip: str) -> bool:
    """
    Check if an IP address is a loopback address
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if the IP is a loopback address, False otherwise
    """
    try:
        return ipaddress.ip_address(ip).is_loopback
    except ValueError:
        return False


def is_multicast_ip(ip: str) -> bool:
    """
    Check if an IP address is a multicast address
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if the IP is a multicast address, False otherwise
    """
    try:
        return ipaddress.ip_address(ip).is_multicast
    except ValueError:
        return False


def is_reserved_ip(ip: str) -> bool:
    """
    Check if an IP address is reserved
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if the IP is reserved, False otherwise
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        # Check for reserved addresses
        if ip_obj.is_reserved:
            return True
        # Check for link-local addresses
        if ip_obj.is_link_local:
            return True
        # Check for unspecified addresses
        if ip_obj.is_unspecified:
            return True
        return False
    except ValueError:
        return False


def get_domain_labels(domain: str) -> List[str]:
    """
    Split a domain name into labels
    
    Args:
        domain: Domain name
        
    Returns:
        list: List of domain labels
    """
    # Normalize domain
    domain = domain.lower()
    
    # Remove trailing dot
    if domain.endswith('.'):
        domain = domain[:-1]
    
    # Split into labels
    return domain.split('.')


def join_domain_labels(labels: List[str]) -> str:
    """
    Join domain labels into a domain name
    
    Args:
        labels: List of domain labels
        
    Returns:
        str: Domain name
    """
    return '.'.join(labels)


if __name__ == "__main__":
    # Example usage
    print("Domain validation:")
    print(f"  example.com: {is_valid_domain('example.com')}")
    print(f"  invalid-domain-: {is_valid_domain('invalid-domain-')}")
    
    print("\nIP validation:")
    print(f"  192.168.1.1: {is_valid_ip('192.168.1.1')}")
    print(f"  2001:db8::1: {is_valid_ip('2001:db8::1')}")
    print(f"  invalid-ip: {is_valid_ip('invalid-ip')}")
    
    print("\nIP version:")
    print(f"  192.168.1.1: {get_ip_version('192.168.1.1')}")
    print(f"  2001:db8::1: {get_ip_version('2001:db8::1')}")
    
    print("\nReverse DNS pointer:")
    print(f"  192.168.1.1: {domain_to_reverse_ptr('192.168.1.1')}")
    print(f"  2001:db8::1: {domain_to_reverse_ptr('2001:db8::1')}")
    
    print("\nSubdomain check:")
    print(f"  www.example.com is subdomain of example.com: {is_subdomain('www.example.com', 'example.com')}")
    print(f"  example.com is subdomain of example.org: {is_subdomain('example.com', 'example.org')}")
    
    print("\nRoot domain:")
    print(f"  www.example.com: {get_root_domain('www.example.com')}")
    print(f"  example.com: {get_root_domain('example.com')}")
    
    print("\nSystem nameservers:")
    print(f"  {get_system_nameservers()}")
    
    print("\nSystem hostname:")
    print(f"  {get_system_hostname()}")
    
    print("\nLocal IP:")
    print(f"  {get_local_ip()}")
    
    print("\nTime formatting:")
    print(f"  0.0005: {format_time(0.0005)}")
    print(f"  0.5: {format_time(0.5)}")
    print(f"  5: {format_time(5)}")
    print(f"  300: {format_time(300)}")
    print(f"  3600: {format_time(3600)}")
    
    print("\nTTL formatting:")
    print(f"  30: {format_ttl(30)}")
    print(f"  300: {format_ttl(300)}")
    print(f"  3600: {format_ttl(3600)}")
    print(f"  86400: {format_ttl(86400)}")
    
    print("\nTTL parsing:")
    print(f"  1d: {parse_ttl('1d')}")
    print(f"  2h30m: {parse_ttl('2h30m')}")
    print(f"  5m30s: {parse_ttl('5m30s')}")
    
    print("\nIP classification:")
    print(f"  192.168.1.1 is private: {is_private_ip('192.168.1.1')}")
    print(f"  127.0.0.1 is loopback: {is_loopback_ip('127.0.0.1')}")
    print(f"  224.0.0.1 is multicast: {is_multicast_ip('224.0.0.1')}")
    print(f"  240.0.0.1 is reserved: {is_reserved_ip('240.0.0.1')}")
    
    print("\nDomain labels:")
    print(f"  www.example.com: {get_domain_labels('www.example.com')}")
    print(f"  Join labels: {join_domain_labels(['www', 'example', 'com'])}") 