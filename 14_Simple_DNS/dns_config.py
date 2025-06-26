#!/usr/bin/env python3
"""
DNS Config - Configuration management for the DNS server

This module provides functionality for loading and managing
DNS server configuration from a JSON file.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)


class DNSConfig:
    """DNS server configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the DNS server configuration
        
        Args:
            config_file: Path to the configuration file (default: None, use defaults)
        """
        # Default configuration
        self.listen_address = "0.0.0.0"
        self.listen_port = 53
        self.foreground = False
        self.recursive = True
        self.upstream_servers = ["8.8.8.8", "8.8.4.4"]
        self.upstream_timeout = 5.0
        self.max_recursion_depth = 10
        self.cache_max_size = 1000
        self.cache_ttl = 300
        self.cache_cleanup_interval = 60
        self.record_db_file = "data/records.json"
        self.zone_dir = "data/zones"
        self.log_file = "data/dns_server.log"
        self.log_level = "INFO"
        
        # Load configuration from file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if the configuration was loaded successfully, False otherwise
        """
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                logger.warning(f"Configuration file not found: {file_path}")
                
                # Create a default configuration file
                self.save_to_file(file_path)
                logger.info(f"Created default configuration file: {file_path}")
                
                return True
            
            # Load the configuration
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Update the configuration
            self.listen_address = config.get('listen_address', self.listen_address)
            self.listen_port = config.get('listen_port', self.listen_port)
            self.foreground = config.get('foreground', self.foreground)
            self.recursive = config.get('recursive', self.recursive)
            self.upstream_servers = config.get('upstream_servers', self.upstream_servers)
            self.upstream_timeout = config.get('upstream_timeout', self.upstream_timeout)
            self.max_recursion_depth = config.get('max_recursion_depth', self.max_recursion_depth)
            self.cache_max_size = config.get('cache_max_size', self.cache_max_size)
            self.cache_ttl = config.get('cache_ttl', self.cache_ttl)
            self.cache_cleanup_interval = config.get('cache_cleanup_interval', self.cache_cleanup_interval)
            self.record_db_file = config.get('record_db_file', self.record_db_file)
            self.zone_dir = config.get('zone_dir', self.zone_dir)
            self.log_file = config.get('log_file', self.log_file)
            self.log_level = config.get('log_level', self.log_level)
            
            logger.info(f"Loaded configuration from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save configuration to a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if the configuration was saved successfully, False otherwise
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Create the configuration dictionary
            config = {
                'listen_address': self.listen_address,
                'listen_port': self.listen_port,
                'foreground': self.foreground,
                'recursive': self.recursive,
                'upstream_servers': self.upstream_servers,
                'upstream_timeout': self.upstream_timeout,
                'max_recursion_depth': self.max_recursion_depth,
                'cache_max_size': self.cache_max_size,
                'cache_ttl': self.cache_ttl,
                'cache_cleanup_interval': self.cache_cleanup_interval,
                'record_db_file': self.record_db_file,
                'zone_dir': self.zone_dir,
                'log_file': self.log_file,
                'log_level': self.log_level
            }
            
            # Write to the file
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved configuration to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary
        
        Returns:
            dict: Configuration as a dictionary
        """
        return {
            'listen_address': self.listen_address,
            'listen_port': self.listen_port,
            'foreground': self.foreground,
            'recursive': self.recursive,
            'upstream_servers': self.upstream_servers,
            'upstream_timeout': self.upstream_timeout,
            'max_recursion_depth': self.max_recursion_depth,
            'cache_max_size': self.cache_max_size,
            'cache_ttl': self.cache_ttl,
            'cache_cleanup_interval': self.cache_cleanup_interval,
            'record_db_file': self.record_db_file,
            'zone_dir': self.zone_dir,
            'log_file': self.log_file,
            'log_level': self.log_level
        }
    
    def __str__(self) -> str:
        """String representation of the configuration"""
        return json.dumps(self.to_dict(), indent=2)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create a default configuration
    config = DNSConfig()
    
    # Save to a file
    config.save_to_file("data/config.json")
    
    # Load from a file
    config2 = DNSConfig("data/config.json")
    
    # Print the configuration
    print(config2) 