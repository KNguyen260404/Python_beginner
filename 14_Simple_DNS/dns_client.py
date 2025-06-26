#!/usr/bin/env python3
"""
DNS Client - A simple DNS client for querying DNS records

This module provides a command-line interface and library for sending
DNS queries to DNS servers and processing the responses.
"""

import socket
import time
import argparse
import sys
import ipaddress
from typing import Dict, List, Tuple, Optional, Any, Union

from dns_message import DNSMessage, DNSQuestion, DNSResourceRecord, DNSType, DNSClass, DNSResponseCode


class DNSClient:
    """DNS Client for sending DNS queries and processing responses"""
    
    def __init__(self, server: str = "8.8.8.8", port: int = 53, timeout: float = 5.0):
        """
        Initialize the DNS client
        
        Args:
            server: DNS server IP address (default: 8.8.8.8)
            port: DNS server port (default: 53)
            timeout: Query timeout in seconds (default: 5.0)
        """
        self.server = server
        self.port = port
        self.timeout = timeout
    
    def query(self, domain: str, record_type: DNSType = DNSType.A, 
              record_class: DNSClass = DNSClass.IN) -> Tuple[Optional[DNSMessage], float]:
        """
        Send a DNS query and get the response
        
        Args:
            domain: Domain name to query
            record_type: DNS record type (default: A)
            record_class: DNS record class (default: IN)
            
        Returns:
            tuple: (response_message, query_time)
        """
        # Create the query message
        query_message = DNSMessage()
        query_message.create_query(domain, record_type, record_class)
        
        # Pack the query message
        query_bytes = query_message.pack()
        
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        try:
            # Record the start time
            start_time = time.time()
            
            # Send the query
            sock.sendto(query_bytes, (self.server, self.port))
            
            # Receive the response
            response_bytes, _ = sock.recvfrom(4096)
            
            # Record the end time
            end_time = time.time()
            
            # Calculate the query time
            query_time = end_time - start_time
            
            # Parse the response
            response_message = DNSMessage.unpack(response_bytes)
            
            return response_message, query_time
            
        except socket.timeout:
            print(f"Error: Query timed out after {self.timeout} seconds")
            return None, self.timeout
            
        except socket.error as e:
            print(f"Socket error: {e}")
            return None, 0
            
        finally:
            sock.close()
    
    def print_response(self, response: DNSMessage, query_time: float, verbose: bool = False) -> None:
        """
        Print the DNS response in a human-readable format
        
        Args:
            response: DNS response message
            query_time: Query time in seconds
            verbose: Whether to show detailed information
        """
        if not response:
            print("No response received")
            return
        
        # Print the response header
        print(f"Query time: {query_time * 1000:.2f} ms")
        print(f"Response code: {response.header.response_code.name}")
        
        if response.header.response_code != DNSResponseCode.NOERROR:
            print(f"Error: {response.header.response_code.name}")
            return
        
        # Print the question section
        if response.questions:
            print("\nQuestion section:")
            for question in response.questions:
                print(f"  {question}")
        
        # Print the answer section
        if response.answers:
            print("\nAnswer section:")
            for answer in response.answers:
                print(f"  {answer}")
        else:
            print("\nNo answers found")
        
        # Print the authority section if verbose or no answers
        if response.authorities and (verbose or not response.answers):
            print("\nAuthority section:")
            for authority in response.authorities:
                print(f"  {authority}")
        
        # Print the additional section if verbose
        if response.additionals and verbose:
            print("\nAdditional section:")
            for additional in response.additionals:
                print(f"  {additional}")
        
        # Print the response flags if verbose
        if verbose:
            print("\nResponse flags:")
            print(f"  ID: {response.header.id}")
            print(f"  Authoritative: {response.header.is_authoritative}")
            print(f"  Truncated: {response.header.is_truncated}")
            print(f"  Recursion desired: {response.header.recursion_desired}")
            print(f"  Recursion available: {response.header.recursion_available}")
    
    def resolve_name(self, domain: str) -> List[str]:
        """
        Resolve a domain name to IPv4 addresses
        
        Args:
            domain: Domain name to resolve
            
        Returns:
            list: List of IPv4 addresses
        """
        response, _ = self.query(domain, DNSType.A)
        
        if not response or response.header.response_code != DNSResponseCode.NOERROR:
            return []
        
        # Extract IPv4 addresses from the answer section
        addresses = []
        for answer in response.answers:
            if answer.rtype == DNSType.A:
                addresses.append(answer.rdata_text)
        
        return addresses
    
    def reverse_lookup(self, ip_address: str) -> List[str]:
        """
        Perform a reverse DNS lookup
        
        Args:
            ip_address: IP address to look up
            
        Returns:
            list: List of domain names
        """
        try:
            # Convert the IP address to a reverse DNS format
            reverse_name = ipaddress.ip_address(ip_address).reverse_pointer
            
            # Query for PTR records
            response, _ = self.query(reverse_name, DNSType.PTR)
            
            if not response or response.header.response_code != DNSResponseCode.NOERROR:
                return []
            
            # Extract domain names from the answer section
            names = []
            for answer in response.answers:
                if answer.rtype == DNSType.PTR:
                    names.append(answer.rdata_text)
            
            return names
            
        except ValueError:
            print(f"Error: Invalid IP address: {ip_address}")
            return []


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="DNS Client - Query DNS records",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "domain",
        help="Domain name to query"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=[t.name for t in DNSType],
        default="A",
        help="DNS record type"
    )
    
    parser.add_argument(
        "--server", "-s",
        default="8.8.8.8",
        help="DNS server IP address"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=53,
        help="DNS server port"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Query timeout in seconds"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )
    
    parser.add_argument(
        "--reverse", "-r",
        action="store_true",
        help="Perform reverse DNS lookup"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main function for the DNS client"""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create the DNS client
    client = DNSClient(args.server, args.port, args.timeout)
    
    # Handle reverse DNS lookup
    if args.reverse:
        try:
            # Validate the input as an IP address
            ipaddress.ip_address(args.domain)
            
            print(f"Performing reverse DNS lookup for {args.domain}...")
            names = client.reverse_lookup(args.domain)
            
            if names:
                print(f"\nDomain names for {args.domain}:")
                for name in names:
                    print(f"  {name}")
            else:
                print(f"No domain names found for {args.domain}")
            
            return
            
        except ValueError:
            print(f"Error: Invalid IP address for reverse lookup: {args.domain}")
            return
    
    # Get the record type from the argument
    try:
        record_type = DNSType[args.type]
    except KeyError:
        print(f"Error: Invalid record type: {args.type}")
        return
    
    # Perform the DNS query
    print(f"Querying {args.domain} for {record_type.name} records from {args.server}:{args.port}...")
    response, query_time = client.query(args.domain, record_type)
    
    # Print the response
    if response:
        client.print_response(response, query_time, args.verbose)


if __name__ == "__main__":
    main() 