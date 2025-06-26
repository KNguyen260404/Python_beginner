#!/usr/bin/env python3
"""
DNS Server - A simple DNS server implementation

This module provides a DNS server that can resolve DNS queries using
a local database of records or by forwarding queries to upstream DNS servers.
"""

import os
import sys
import socket
import threading
import argparse
import logging
import json
import signal
import time
from typing import Dict, List, Tuple, Optional, Any, Union

from dns_message import DNSMessage, DNSType, DNSClass, DNSResponseCode
from dns_resolver import DNSResolver, RecursiveResolver
from dns_cache import DNSCache
from dns_records import DNSRecordDB
from dns_config import DNSConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DNSServer:
    """DNS server implementation"""
    
    def __init__(self, config: DNSConfig):
        """
        Initialize the DNS server
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.running = False
        self.socket = None
        self.stats = {
            'queries': 0,
            'responses': 0,
            'errors': 0,
            'start_time': time.time(),
            'queries_by_type': {},
            'queries_by_domain': {}
        }
        
        # Create the record database
        self.record_db = DNSRecordDB(config.record_db_file)
        
        # Create the cache
        self.cache = DNSCache(
            max_size=config.cache_max_size,
            ttl=config.cache_ttl,
            cleanup_interval=config.cache_cleanup_interval
        )
        
        # Create the resolver
        if config.recursive:
            self.resolver = RecursiveResolver(
                self.record_db,
                self.cache,
                config.upstream_servers,
                config.upstream_timeout,
                config.max_recursion_depth
            )
        else:
            self.resolver = DNSResolver(
                self.record_db,
                self.cache,
                config.upstream_servers,
                config.upstream_timeout
            )
    
    def start(self) -> None:
        """Start the DNS server"""
        if self.running:
            logger.warning("Server is already running")
            return
        
        try:
            # Create a UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Allow address reuse
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to the specified address and port
            self.socket.bind((self.config.listen_address, self.config.listen_port))
            
            logger.info(f"DNS server listening on {self.config.listen_address}:{self.config.listen_port}")
            
            # Set the server as running
            self.running = True
            
            # Start the main loop in a separate thread
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # If not running in foreground, return immediately
            if not self.config.foreground:
                return
            
            # Otherwise, wait for the thread to finish
            while self.running:
                try:
                    self.thread.join(1)
                except KeyboardInterrupt:
                    self.stop()
                    break
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.running = False
            if self.socket:
                self.socket.close()
    
    def stop(self) -> None:
        """Stop the DNS server"""
        if not self.running:
            logger.warning("Server is not running")
            return
        
        logger.info("Stopping DNS server")
        self.running = False
        
        # Close the socket
        if self.socket:
            self.socket.close()
        
        # Wait for the thread to finish
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(5)
    
    def _run(self) -> None:
        """Main server loop"""
        while self.running:
            try:
                # Receive data from the socket
                data, addr = self.socket.recvfrom(4096)
                
                # Handle the query in a separate thread
                threading.Thread(target=self._handle_query, args=(data, addr)).start()
                
            except socket.error as e:
                if self.running:
                    logger.error(f"Socket error: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"Error in server loop: {e}")
    
    def _handle_query(self, data: bytes, addr: Tuple[str, int]) -> None:
        """
        Handle a DNS query
        
        Args:
            data: Query data
            addr: Client address (IP, port)
        """
        try:
            # Parse the query
            query = DNSMessage.unpack(data)
            
            # Update statistics
            self._update_query_stats(query)
            
            # Log the query
            if query.questions:
                question = query.questions[0]
                logger.info(f"Query from {addr[0]}:{addr[1]}: {question.name} {question.qtype.name}")
            
            # Resolve the query
            response = self.resolver.resolve(query)
            
            # Log the response
            if response.header.response_code != DNSResponseCode.NOERROR:
                logger.warning(f"Response to {addr[0]}:{addr[1]}: {response.header.response_code.name}")
            else:
                logger.info(f"Response to {addr[0]}:{addr[1]}: {len(response.answers)} answers")
            
            # Send the response
            self.socket.sendto(response.pack(), addr)
            
            # Update statistics
            self.stats['responses'] += 1
            
        except Exception as e:
            logger.error(f"Error handling query from {addr[0]}:{addr[1]}: {e}")
            self.stats['errors'] += 1
    
    def _update_query_stats(self, query: DNSMessage) -> None:
        """
        Update query statistics
        
        Args:
            query: DNS query message
        """
        self.stats['queries'] += 1
        
        if query.questions:
            question = query.questions[0]
            qtype = question.qtype.name
            domain = question.name
            
            # Update queries by type
            if qtype not in self.stats['queries_by_type']:
                self.stats['queries_by_type'][qtype] = 0
            self.stats['queries_by_type'][qtype] += 1
            
            # Update queries by domain
            if domain not in self.stats['queries_by_domain']:
                self.stats['queries_by_domain'][domain] = 0
            self.stats['queries_by_domain'][domain] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get server statistics
        
        Returns:
            dict: Server statistics
        """
        # Calculate uptime
        uptime = time.time() - self.stats['start_time']
        
        # Calculate queries per second
        qps = self.stats['queries'] / uptime if uptime > 0 else 0
        
        # Get the top 10 domains
        top_domains = sorted(
            self.stats['queries_by_domain'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Return the statistics
        return {
            'uptime': uptime,
            'queries': self.stats['queries'],
            'responses': self.stats['responses'],
            'errors': self.stats['errors'],
            'qps': qps,
            'queries_by_type': self.stats['queries_by_type'],
            'top_domains': dict(top_domains),
            'cache_size': self.cache.size()
        }
    
    def _signal_handler(self, sig, frame) -> None:
        """
        Handle signals
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        if sig == signal.SIGINT:
            logger.info("Received SIGINT, stopping server")
        elif sig == signal.SIGTERM:
            logger.info("Received SIGTERM, stopping server")
        
        self.stop()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="DNS Server - A simple DNS server implementation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--config", "-c",
        default="data/config.json",
        help="Path to the configuration file"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        help="Port to listen on (overrides config file)"
    )
    
    parser.add_argument(
        "--address", "-a",
        help="Address to listen on (overrides config file)"
    )
    
    parser.add_argument(
        "--foreground", "-f",
        action="store_true",
        help="Run in foreground mode"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main function"""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = DNSConfig(args.config)
    
    # Override configuration with command-line arguments
    if args.port:
        config.listen_port = args.port
    
    if args.address:
        config.listen_address = args.address
    
    if args.foreground:
        config.foreground = True
    
    # Create and start the server
    server = DNSServer(config)
    server.start()
    
    # If running in foreground, print statistics periodically
    if config.foreground:
        try:
            while server.running:
                time.sleep(10)
                stats = server.get_stats()
                print(f"\nServer statistics:")
                print(f"  Uptime: {stats['uptime']:.1f} seconds")
                print(f"  Queries: {stats['queries']} ({stats['qps']:.1f} qps)")
                print(f"  Responses: {stats['responses']}")
                print(f"  Errors: {stats['errors']}")
                print(f"  Cache size: {stats['cache_size']}")
                print(f"  Queries by type:")
                for qtype, count in sorted(stats['queries_by_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    {qtype}: {count}")
                print(f"  Top domains:")
                for domain, count in list(stats['top_domains'].items())[:5]:
                    print(f"    {domain}: {count}")
        except KeyboardInterrupt:
            server.stop()


if __name__ == "__main__":
    main() 