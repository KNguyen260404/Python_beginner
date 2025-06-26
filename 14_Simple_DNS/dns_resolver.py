#!/usr/bin/env python3
"""
DNS Resolver - Resolves DNS queries using local records or upstream servers

This module provides the core DNS resolution functionality for the DNS server.
It can resolve queries using a local database of records or by forwarding
queries to upstream DNS servers.
"""

import socket
import time
import random
import logging
from typing import Dict, List, Tuple, Optional, Any, Union

from dns_message import DNSMessage, DNSQuestion, DNSResourceRecord, DNSType, DNSClass, DNSResponseCode
from dns_cache import DNSCache
from dns_records import DNSRecordDB

# Configure logging
logger = logging.getLogger(__name__)


class DNSResolver:
    """DNS resolver for handling DNS queries"""
    
    def __init__(self, record_db: DNSRecordDB, cache: DNSCache, 
                 upstream_servers: List[str] = None, timeout: float = 5.0):
        """
        Initialize the DNS resolver
        
        Args:
            record_db: Database of local DNS records
            cache: DNS response cache
            upstream_servers: List of upstream DNS servers (default: ["8.8.8.8", "8.8.4.4"])
            timeout: Timeout for upstream queries in seconds (default: 5.0)
        """
        self.record_db = record_db
        self.cache = cache
        self.upstream_servers = upstream_servers or ["8.8.8.8", "8.8.4.4"]
        self.timeout = timeout
    
    def resolve(self, query: DNSMessage) -> DNSMessage:
        """
        Resolve a DNS query
        
        Args:
            query: The DNS query message
            
        Returns:
            DNSMessage: The DNS response message
        """
        # Create a response message
        response = DNSMessage()
        response.create_response(query)
        
        # Check if the query is valid
        if not query.questions:
            response.header.response_code = DNSResponseCode.FORMERR
            return response
        
        # Get the question
        question = query.questions[0]
        domain = question.name
        qtype = question.qtype
        qclass = question.qclass
        
        logger.info(f"Resolving query for {domain} ({qtype.name})")
        
        # Try to get the response from cache
        cache_key = f"{domain}:{qtype.name}:{qclass.name}"
        cached_response = self.cache.get(cache_key)
        
        if cached_response:
            logger.info(f"Cache hit for {cache_key}")
            
            # Copy the cached response data to our response
            response.answers = cached_response.answers
            response.authorities = cached_response.authorities
            response.additionals = cached_response.additionals
            
            # Update the counts in the header
            response.header.answer_count = len(response.answers)
            response.header.authority_count = len(response.authorities)
            response.header.additional_count = len(response.additionals)
            
            return response
        
        # Try to resolve using local records
        local_records = self.record_db.lookup(domain, qtype, qclass)
        
        if local_records:
            logger.info(f"Found local records for {domain} ({qtype.name})")
            
            # Add the records to the response
            for record in local_records:
                response.add_answer(record)
            
            # Add any additional records if needed
            self._add_additional_records(response)
            
            # Cache the response
            self.cache.put(cache_key, response)
            
            return response
        
        # If we don't have local records, try upstream servers
        logger.info(f"No local records for {domain} ({qtype.name}), trying upstream servers")
        upstream_response = self._query_upstream(query)
        
        if upstream_response:
            # Cache the response
            self.cache.put(cache_key, upstream_response)
            
            return upstream_response
        
        # If we couldn't resolve the query, return NXDOMAIN
        response.header.response_code = DNSResponseCode.NXDOMAIN
        return response
    
    def _query_upstream(self, query: DNSMessage) -> Optional[DNSMessage]:
        """
        Query upstream DNS servers
        
        Args:
            query: The DNS query message
            
        Returns:
            Optional[DNSMessage]: The DNS response message, or None if no response
        """
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        # Pack the query message
        query_bytes = query.pack()
        
        # Try each upstream server until we get a response
        for server in self.upstream_servers:
            try:
                logger.debug(f"Querying upstream server {server}")
                
                # Send the query
                sock.sendto(query_bytes, (server, 53))
                
                # Receive the response
                response_bytes, _ = sock.recvfrom(4096)
                
                # Parse the response
                response = DNSMessage.unpack(response_bytes)
                
                logger.debug(f"Received response from {server} with code {response.header.response_code.name}")
                
                # Return the response if it's valid
                if response and response.header.id == query.header.id:
                    return response
                
            except socket.timeout:
                logger.warning(f"Timeout querying upstream server {server}")
                continue
                
            except socket.error as e:
                logger.error(f"Socket error querying upstream server {server}: {e}")
                continue
                
            except Exception as e:
                logger.error(f"Error querying upstream server {server}: {e}")
                continue
        
        # If we couldn't get a response from any server, return None
        return None
    
    def _add_additional_records(self, response: DNSMessage) -> None:
        """
        Add additional records to a response
        
        Args:
            response: The DNS response message to add records to
        """
        # Get all domain names from the answer section
        domains = set()
        
        for answer in response.answers:
            # For MX records, add the mail server domain
            if answer.rtype == DNSType.MX:
                # MX record data format: <preference> <mail server>
                parts = answer.rdata_text.split(" ", 1)
                if len(parts) == 2:
                    domains.add(parts[1])
            
            # For NS records, add the nameserver domain
            elif answer.rtype == DNSType.NS:
                domains.add(answer.rdata_text)
            
            # For CNAME records, add the canonical name
            elif answer.rtype == DNSType.CNAME:
                domains.add(answer.rdata_text)
        
        # Look up A and AAAA records for these domains
        for domain in domains:
            # Look up A records
            a_records = self.record_db.lookup(domain, DNSType.A)
            for record in a_records:
                response.add_additional(record)
            
            # Look up AAAA records
            aaaa_records = self.record_db.lookup(domain, DNSType.AAAA)
            for record in aaaa_records:
                response.add_additional(record)


class RecursiveResolver(DNSResolver):
    """DNS resolver with recursive resolution capability"""
    
    def __init__(self, record_db: DNSRecordDB, cache: DNSCache, 
                 upstream_servers: List[str] = None, timeout: float = 5.0,
                 max_recursion: int = 10):
        """
        Initialize the recursive resolver
        
        Args:
            record_db: Database of local DNS records
            cache: DNS response cache
            upstream_servers: List of upstream DNS servers (default: ["8.8.8.8", "8.8.4.4"])
            timeout: Timeout for upstream queries in seconds (default: 5.0)
            max_recursion: Maximum recursion depth (default: 10)
        """
        super().__init__(record_db, cache, upstream_servers, timeout)
        self.max_recursion = max_recursion
        
        # Root nameservers
        self.root_servers = [
            "198.41.0.4",       # a.root-servers.net
            "199.9.14.201",     # b.root-servers.net
            "192.33.4.12",      # c.root-servers.net
            "199.7.91.13",      # d.root-servers.net
            "192.203.230.10",   # e.root-servers.net
            "192.5.5.241",      # f.root-servers.net
            "192.112.36.4",     # g.root-servers.net
            "198.97.190.53",    # h.root-servers.net
            "192.36.148.17",    # i.root-servers.net
            "192.58.128.30",    # j.root-servers.net
            "193.0.14.129",     # k.root-servers.net
            "199.7.83.42",      # l.root-servers.net
            "202.12.27.33"      # m.root-servers.net
        ]
    
    def resolve(self, query: DNSMessage) -> DNSMessage:
        """
        Resolve a DNS query recursively
        
        Args:
            query: The DNS query message
            
        Returns:
            DNSMessage: The DNS response message
        """
        # First try non-recursive resolution
        response = super().resolve(query)
        
        # If we got a valid response, return it
        if response.header.response_code == DNSResponseCode.NOERROR and response.answers:
            return response
        
        # If the query has recursion desired and we don't have a valid response,
        # try recursive resolution
        if query.header.recursion_desired:
            logger.info("Attempting recursive resolution")
            
            # Get the question
            question = query.questions[0]
            domain = question.name
            qtype = question.qtype
            
            # Try recursive resolution
            recursive_response = self._resolve_recursive(domain, qtype, 0)
            
            if recursive_response:
                # Create a response message
                response = DNSMessage()
                response.create_response(query)
                
                # Copy the recursive response data
                response.answers = recursive_response.answers
                response.authorities = recursive_response.authorities
                response.additionals = recursive_response.additionals
                
                # Update the counts in the header
                response.header.answer_count = len(response.answers)
                response.header.authority_count = len(response.authorities)
                response.header.additional_count = len(response.additionals)
                
                # Cache the response
                cache_key = f"{domain}:{qtype.name}:{question.qclass.name}"
                self.cache.put(cache_key, response)
                
                return response
        
        # If we still don't have a valid response, return what we have
        return response
    
    def _resolve_recursive(self, domain: str, qtype: DNSType, depth: int) -> Optional[DNSMessage]:
        """
        Recursively resolve a DNS query
        
        Args:
            domain: The domain name to resolve
            qtype: The query type
            depth: Current recursion depth
            
        Returns:
            Optional[DNSMessage]: The DNS response message, or None if no response
        """
        # Check recursion depth
        if depth >= self.max_recursion:
            logger.warning(f"Maximum recursion depth reached for {domain}")
            return None
        
        # Start with root nameservers
        nameservers = self.root_servers
        
        # Split the domain into labels
        labels = domain.split(".")
        
        # Resolve the domain step by step
        while labels:
            # Create a query for the current domain
            current_domain = ".".join(labels)
            
            # Try each nameserver until we get a response
            response = None
            for nameserver in nameservers:
                # Create a query message
                query = DNSMessage()
                query.create_query(current_domain, qtype)
                
                # Send the query to the nameserver
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                
                try:
                    # Send the query
                    sock.sendto(query.pack(), (nameserver, 53))
                    
                    # Receive the response
                    response_bytes, _ = sock.recvfrom(4096)
                    
                    # Parse the response
                    response = DNSMessage.unpack(response_bytes)
                    
                    # Break if we got a valid response
                    if response and response.header.id == query.header.id:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error querying nameserver {nameserver}: {e}")
                    continue
                    
                finally:
                    sock.close()
            
            # If we didn't get a response from any nameserver, return None
            if not response:
                logger.warning(f"No response from any nameserver for {current_domain}")
                return None
            
            # If we got answers, return the response
            if response.answers:
                return response
            
            # If we got NS records in the authority section, use them as the next nameservers
            if response.authorities:
                new_nameservers = []
                
                for authority in response.authorities:
                    if authority.rtype == DNSType.NS:
                        # Get the nameserver domain
                        ns_domain = authority.rdata_text
                        
                        # Look for the nameserver's IP in the additional section
                        for additional in response.additionals:
                            if additional.name == ns_domain and additional.rtype == DNSType.A:
                                new_nameservers.append(additional.rdata_text)
                
                # If we found new nameservers, use them
                if new_nameservers:
                    nameservers = new_nameservers
                    
                    # Remove the leftmost label and continue
                    labels = labels[1:]
                    
                    # If no more labels, we're done
                    if not labels:
                        break
                else:
                    # If we didn't find any nameserver IPs, we need to resolve them
                    for authority in response.authorities:
                        if authority.rtype == DNSType.NS:
                            # Get the nameserver domain
                            ns_domain = authority.rdata_text
                            
                            # Recursively resolve the nameserver domain
                            ns_response = self._resolve_recursive(ns_domain, DNSType.A, depth + 1)
                            
                            if ns_response and ns_response.answers:
                                for answer in ns_response.answers:
                                    if answer.rtype == DNSType.A:
                                        new_nameservers.append(answer.rdata_text)
                    
                    # If we found new nameservers, use them
                    if new_nameservers:
                        nameservers = new_nameservers
                        
                        # Remove the leftmost label and continue
                        labels = labels[1:]
                        
                        # If no more labels, we're done
                        if not labels:
                            break
                    else:
                        # If we still don't have any nameservers, return None
                        logger.warning(f"Could not find nameserver IPs for {current_domain}")
                        return None
            else:
                # If we don't have any authority records, return None
                logger.warning(f"No authority records for {current_domain}")
                return None
        
        # If we've exhausted all labels and still don't have an answer, return None
        return None


if __name__ == "__main__":
    # Example usage
    from dns_records import DNSRecordDB
    from dns_cache import DNSCache
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create a record database
    record_db = DNSRecordDB()
    
    # Add some test records
    record_db.add_record("example.local", DNSType.A, "192.168.1.10", ttl=3600)
    record_db.add_record("example.local", DNSType.AAAA, "2001:db8::1", ttl=3600)
    record_db.add_record("mail.example.local", DNSType.A, "192.168.1.20", ttl=3600)
    record_db.add_record("example.local", DNSType.MX, "10 mail.example.local", ttl=3600)
    
    # Create a cache
    cache = DNSCache(max_size=1000, ttl=300)
    
    # Create a resolver
    resolver = DNSResolver(record_db, cache)
    
    # Create a test query
    query = DNSMessage()
    query.create_query("example.local", DNSType.A)
    
    # Resolve the query
    response = resolver.resolve(query)
    
    # Print the response
    print(response)
    
    # Create another test query
    query = DNSMessage()
    query.create_query("example.local", DNSType.MX)
    
    # Resolve the query
    response = resolver.resolve(query)
    
    # Print the response
    print("\n" + str(response)) 