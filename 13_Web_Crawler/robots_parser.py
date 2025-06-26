#!/usr/bin/env python3
"""
Robots Parser - Handles robots.txt parsing and checking
"""

import urllib.parse
import logging
from typing import Dict, List, Set, Optional
import requests
from urllib3.exceptions import HTTPError

logger = logging.getLogger(__name__)


class RobotsParser:
    """Parser for robots.txt files"""
    
    def __init__(self, user_agent: str):
        """
        Initialize the robots parser
        
        Args:
            user_agent: User agent string to use for checking rules
        """
        self.user_agent = user_agent
        self.rules: Dict[str, Dict[str, List[str]]] = {}
        self.sitemaps: List[str] = []
        self.default_agent = "*"
        self.fetched_domains: Set[str] = set()
    
    def fetch(self, robots_url: str) -> bool:
        """
        Fetch and parse a robots.txt file
        
        Args:
            robots_url: URL of the robots.txt file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Parse the domain from the URL
            parsed_url = urllib.parse.urlparse(robots_url)
            domain = parsed_url.netloc
            
            # Check if we've already fetched this domain
            if domain in self.fetched_domains:
                return True
            
            # Fetch the robots.txt file
            logger.info(f"Fetching robots.txt from {robots_url}")
            response = requests.get(robots_url, timeout=10)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the robots.txt content
                self._parse_content(response.text)
                self.fetched_domains.add(domain)
                return True
            elif response.status_code == 404:
                # No robots.txt file, assume everything is allowed
                logger.info(f"No robots.txt found at {robots_url}")
                self.fetched_domains.add(domain)
                return True
            else:
                logger.warning(f"Failed to fetch robots.txt from {robots_url}: HTTP {response.status_code}")
                return False
                
        except (requests.RequestException, HTTPError) as e:
            logger.warning(f"Error fetching robots.txt from {robots_url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error fetching robots.txt from {robots_url}: {str(e)}")
            return False
    
    def _parse_content(self, content: str) -> None:
        """
        Parse robots.txt content
        
        Args:
            content: Content of the robots.txt file
        """
        # Initialize rules dictionary
        self.rules = {}
        self.sitemaps = []
        
        # Current user agent
        current_agent = None
        
        # Process each line
        for line in content.splitlines():
            # Remove comments
            if "#" in line:
                line = line[:line.find("#")]
            
            # Strip whitespace
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Split into field and value
            if ":" in line:
                field, value = line.split(":", 1)
            else:
                field, value = line.split(" ", 1)
            
            field = field.strip().lower()
            value = value.strip()
            
            # Process fields
            if field == "user-agent":
                current_agent = value.lower()
                if current_agent not in self.rules:
                    self.rules[current_agent] = {"allow": [], "disallow": []}
            elif field == "disallow" and current_agent:
                if value:
                    self.rules[current_agent]["disallow"].append(value)
            elif field == "allow" and current_agent:
                if value:
                    self.rules[current_agent]["allow"].append(value)
            elif field == "sitemap":
                if value:
                    self.sitemaps.append(value)
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if a URL can be fetched according to robots.txt rules
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if the URL can be fetched, False otherwise
        """
        # If no rules have been fetched, assume allowed
        if not self.rules:
            return True
        
        # Parse the URL path
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        if not path:
            path = "/"
        
        # Check if the path is allowed for the user agent
        return self._is_allowed(path, self.user_agent)
    
    def _is_allowed(self, path: str, user_agent: str) -> bool:
        """
        Check if a path is allowed for a user agent
        
        Args:
            path: URL path to check
            user_agent: User agent to check
            
        Returns:
            bool: True if the path is allowed, False otherwise
        """
        # Check specific user agent rules
        if user_agent in self.rules:
            if self._check_rules(path, self.rules[user_agent]):
                return True
        
        # Check default user agent rules
        if self.default_agent in self.rules:
            return self._check_rules(path, self.rules[self.default_agent])
        
        # If no rules match, assume allowed
        return True
    
    def _check_rules(self, path: str, rules: Dict[str, List[str]]) -> bool:
        """
        Check if a path matches any allow/disallow rules
        
        Args:
            path: URL path to check
            rules: Dictionary of allow/disallow rules
            
        Returns:
            bool: True if the path is allowed, False otherwise
        """
        # Find the most specific matching rule
        allow_match = self._find_most_specific_match(path, rules.get("allow", []))
        disallow_match = self._find_most_specific_match(path, rules.get("disallow", []))
        
        # If no rules match, assume allowed
        if allow_match is None and disallow_match is None:
            return True
        
        # If only one rule type matches, use that
        if allow_match is None:
            return False
        if disallow_match is None:
            return True
        
        # If both match, use the longer (more specific) one
        return len(allow_match) >= len(disallow_match)
    
    def _find_most_specific_match(self, path: str, patterns: List[str]) -> Optional[str]:
        """
        Find the most specific matching pattern for a path
        
        Args:
            path: URL path to check
            patterns: List of patterns to check
            
        Returns:
            str: The most specific matching pattern, or None if no match
        """
        matches = []
        
        for pattern in patterns:
            # Check if the pattern matches the path
            if self._matches_pattern(path, pattern):
                matches.append(pattern)
        
        # Return the longest (most specific) match
        if matches:
            return max(matches, key=len)
        
        return None
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a pattern
        
        Args:
            path: URL path to check
            pattern: Pattern to check
            
        Returns:
            bool: True if the path matches the pattern, False otherwise
        """
        # Handle wildcards
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        
        # Handle exact matches
        return path.startswith(pattern)
    
    def get_sitemaps(self) -> List[str]:
        """
        Get the sitemaps listed in robots.txt
        
        Returns:
            list: List of sitemap URLs
        """
        return self.sitemaps 