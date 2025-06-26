#!/usr/bin/env python3
"""
DNS Cache - Caches DNS responses to improve performance

This module provides a simple cache for DNS responses to reduce
the need for repeated queries to upstream DNS servers.
"""

import time
import threading
from typing import Dict, Optional, Any
import logging

from dns_message import DNSMessage

# Configure logging
logger = logging.getLogger(__name__)


class CacheEntry:
    """A single DNS cache entry"""
    
    def __init__(self, message: DNSMessage, ttl: int = 300):
        """
        Initialize a cache entry
        
        Args:
            message: The DNS message to cache
            ttl: Time to live in seconds (default: 300)
        """
        self.message = message
        self.ttl = ttl
        self.timestamp = time.time()
    
    def is_expired(self) -> bool:
        """
        Check if the cache entry has expired
        
        Returns:
            bool: True if the entry has expired, False otherwise
        """
        return time.time() > self.timestamp + self.ttl
    
    def time_remaining(self) -> int:
        """
        Get the time remaining until the cache entry expires
        
        Returns:
            int: Time remaining in seconds
        """
        remaining = int(self.timestamp + self.ttl - time.time())
        return max(0, remaining)
    
    def update_ttl(self, message: DNSMessage) -> None:
        """
        Update the TTL of the cache entry
        
        Args:
            message: The updated DNS message
        """
        self.message = message
        self.timestamp = time.time()


class DNSCache:
    """Cache for DNS responses"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300, cleanup_interval: int = 60):
        """
        Initialize the DNS cache
        
        Args:
            max_size: Maximum number of entries in the cache (default: 1000)
            ttl: Default time to live in seconds (default: 300)
            cleanup_interval: Interval for cache cleanup in seconds (default: 60)
        """
        self.max_size = max_size
        self.default_ttl = ttl
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        
        # Start the cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def put(self, key: str, message: DNSMessage, ttl: Optional[int] = None) -> None:
        """
        Add a DNS message to the cache
        
        Args:
            key: Cache key (usually domain:type:class)
            message: DNS message to cache
            ttl: Time to live in seconds (default: None, uses default TTL)
        """
        with self.lock:
            # Check if we need to evict an entry
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_one()
            
            # Use the minimum TTL from the DNS records if available
            if ttl is None:
                ttl = self._get_min_ttl(message)
            
            # Add the entry to the cache
            self.cache[key] = CacheEntry(message, ttl)
            logger.debug(f"Added cache entry for {key} with TTL {ttl}s")
    
    def get(self, key: str) -> Optional[DNSMessage]:
        """
        Get a DNS message from the cache
        
        Args:
            key: Cache key (usually domain:type:class)
            
        Returns:
            Optional[DNSMessage]: The cached DNS message, or None if not found or expired
        """
        with self.lock:
            entry = self.cache.get(key)
            
            if entry is None:
                return None
            
            # Check if the entry has expired
            if entry.is_expired():
                logger.debug(f"Cache entry for {key} has expired")
                del self.cache[key]
                return None
            
            # Update TTLs in the message based on the time remaining
            message = self._update_message_ttls(entry)
            
            logger.debug(f"Cache hit for {key}, TTL remaining: {entry.time_remaining()}s")
            return message
    
    def remove(self, key: str) -> None:
        """
        Remove a DNS message from the cache
        
        Args:
            key: Cache key (usually domain:type:class)
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Removed cache entry for {key}")
    
    def clear(self) -> None:
        """Clear the entire cache"""
        with self.lock:
            self.cache.clear()
            logger.debug("Cache cleared")
    
    def size(self) -> int:
        """
        Get the current size of the cache
        
        Returns:
            int: Number of entries in the cache
        """
        with self.lock:
            return len(self.cache)
    
    def _evict_one(self) -> None:
        """Evict one entry from the cache"""
        with self.lock:
            # Find the oldest or expired entry
            oldest_key = None
            oldest_time = float('inf')
            
            for key, entry in self.cache.items():
                # If the entry has expired, remove it
                if entry.is_expired():
                    del self.cache[key]
                    logger.debug(f"Evicted expired cache entry for {key}")
                    return
                
                # Otherwise, find the oldest entry
                if entry.timestamp < oldest_time:
                    oldest_time = entry.timestamp
                    oldest_key = key
            
            # Remove the oldest entry
            if oldest_key:
                del self.cache[oldest_key]
                logger.debug(f"Evicted oldest cache entry for {oldest_key}")
    
    def _cleanup_loop(self) -> None:
        """Periodically clean up expired cache entries"""
        while True:
            time.sleep(self.cleanup_interval)
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up expired cache entries"""
        with self.lock:
            # Find all expired entries
            expired_keys = []
            
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            # Remove expired entries
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _get_min_ttl(self, message: DNSMessage) -> int:
        """
        Get the minimum TTL from a DNS message
        
        Args:
            message: DNS message to get TTL from
            
        Returns:
            int: Minimum TTL in seconds
        """
        min_ttl = self.default_ttl
        
        # Check TTLs in the answer section
        for answer in message.answers:
            min_ttl = min(min_ttl, answer.ttl)
        
        # Check TTLs in the authority section
        for authority in message.authorities:
            min_ttl = min(min_ttl, authority.ttl)
        
        # Check TTLs in the additional section
        for additional in message.additionals:
            min_ttl = min(min_ttl, additional.ttl)
        
        # Ensure the TTL is at least 1 second
        return max(1, min_ttl)
    
    def _update_message_ttls(self, entry: CacheEntry) -> DNSMessage:
        """
        Update TTLs in a cached message based on the time remaining
        
        Args:
            entry: Cache entry containing the message
            
        Returns:
            DNSMessage: Updated DNS message
        """
        # Create a deep copy of the message
        message = DNSMessage()
        message.header = entry.message.header
        message.questions = entry.message.questions.copy()
        
        # Calculate the time elapsed since the entry was cached
        time_remaining = entry.time_remaining()
        
        # Update TTLs in the answer section
        message.answers = []
        for answer in entry.message.answers:
            updated_answer = DNSResourceRecord()
            updated_answer.name = answer.name
            updated_answer.rtype = answer.rtype
            updated_answer.rclass = answer.rclass
            updated_answer.ttl = min(answer.ttl, time_remaining)
            updated_answer.rdata = answer.rdata
            updated_answer.rdata_text = answer.rdata_text
            message.answers.append(updated_answer)
        
        # Update TTLs in the authority section
        message.authorities = []
        for authority in entry.message.authorities:
            updated_authority = DNSResourceRecord()
            updated_authority.name = authority.name
            updated_authority.rtype = authority.rtype
            updated_authority.rclass = authority.rclass
            updated_authority.ttl = min(authority.ttl, time_remaining)
            updated_authority.rdata = authority.rdata
            updated_authority.rdata_text = authority.rdata_text
            message.authorities.append(updated_authority)
        
        # Update TTLs in the additional section
        message.additionals = []
        for additional in entry.message.additionals:
            updated_additional = DNSResourceRecord()
            updated_additional.name = additional.name
            updated_additional.rtype = additional.rtype
            updated_additional.rclass = additional.rclass
            updated_additional.ttl = min(additional.ttl, time_remaining)
            updated_additional.rdata = additional.rdata
            updated_additional.rdata_text = additional.rdata_text
            message.additionals.append(updated_additional)
        
        # Update the header counts
        message.header.answer_count = len(message.answers)
        message.header.authority_count = len(message.authorities)
        message.header.additional_count = len(message.additionals)
        
        return message


if __name__ == "__main__":
    # Example usage
    from dns_message import DNSMessage, DNSResourceRecord, DNSType, DNSClass
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create a cache
    cache = DNSCache(max_size=10, ttl=60, cleanup_interval=5)
    
    # Create a test message
    message = DNSMessage()
    message.header.id = 1234
    message.header.is_response = True
    
    # Add a question
    question = DNSQuestion("example.com", DNSType.A, DNSClass.IN)
    message.add_question(question)
    
    # Add an answer
    answer = DNSResourceRecord()
    answer.name = "example.com"
    answer.rtype = DNSType.A
    answer.rclass = DNSClass.IN
    answer.ttl = 3600
    answer.rdata = bytes([93, 184, 216, 34])
    answer.rdata_text = "93.184.216.34"
    message.add_answer(answer)
    
    # Add the message to the cache
    cache.put("example.com:A:IN", message)
    
    # Get the message from the cache
    cached_message = cache.get("example.com:A:IN")
    print("Cached message:", cached_message)
    
    # Wait for a while
    print("Waiting for 2 seconds...")
    time.sleep(2)
    
    # Get the message again
    cached_message = cache.get("example.com:A:IN")
    print("Cached message after 2 seconds:", cached_message)
    
    # Clear the cache
    cache.clear()
    print("Cache cleared, size:", cache.size()) 