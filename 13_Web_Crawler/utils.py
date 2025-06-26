#!/usr/bin/env python3
"""
Utils - Utility functions for the web crawler
"""

import os
import re
import time
import logging
import urllib.parse
from typing import List, Set, Dict, Any, Optional, Tuple
import validators

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing fragments, query parameters, and trailing slashes
    
    Args:
        url: URL to normalize
        
    Returns:
        str: Normalized URL
    """
    try:
        # Parse the URL
        parsed = urllib.parse.urlparse(url)
        
        # Remove the fragment
        parsed = parsed._replace(fragment="")
        
        # Reconstruct the URL
        normalized = urllib.parse.urlunparse(parsed)
        
        # Remove trailing slash if present (except for the domain root)
        if normalized.endswith("/") and len(normalized.rstrip("/").split("/")) > 3:
            normalized = normalized.rstrip("/")
        
        return normalized
    except Exception as e:
        logger.error(f"Error normalizing URL {url}: {str(e)}")
        return url


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    if not url:
        return False
    
    # Check if the URL is valid using validators
    return validators.url(url)


def get_domain(url: str) -> str:
    """
    Get the domain from a URL
    
    Args:
        url: URL to extract domain from
        
    Returns:
        str: Domain name
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc
    except Exception:
        return ""


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs have the same domain
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        bool: True if the URLs have the same domain, False otherwise
    """
    return get_domain(url1) == get_domain(url2)


def is_binary_content_type(content_type: str) -> bool:
    """
    Check if a content type is binary
    
    Args:
        content_type: Content type to check
        
    Returns:
        bool: True if the content type is binary, False otherwise
    """
    binary_types = [
        "application/octet-stream",
        "application/pdf",
        "application/zip",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/x-gzip",
        "application/x-bzip2",
        "application/msword",
        "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument",
        "image/",
        "audio/",
        "video/",
    ]
    
    return any(content_type.startswith(binary_type) for binary_type in binary_types)


def is_valid_file_extension(url: str, allowed_extensions: List[str]) -> bool:
    """
    Check if a URL has a valid file extension
    
    Args:
        url: URL to check
        allowed_extensions: List of allowed file extensions
        
    Returns:
        bool: True if the URL has a valid file extension, False otherwise
    """
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    
    # Check if the path has an extension
    if not path or "." not in path:
        return True  # No extension, assume it's a web page
    
    # Get the extension
    extension = os.path.splitext(path)[1].lower()
    
    # Check if the extension is in the allowed list
    return extension in allowed_extensions


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        list: List of extracted URLs
    """
    # Regular expression for URL matching
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    # Find all URLs in the text
    urls = url_pattern.findall(text)
    
    # Filter out invalid URLs
    valid_urls = [url for url in urls if is_valid_url(url)]
    
    return valid_urls


def get_absolute_url(base_url: str, url: str) -> str:
    """
    Convert a relative URL to an absolute URL
    
    Args:
        base_url: Base URL for the page
        url: URL to convert (may be relative)
        
    Returns:
        str: Absolute URL
    """
    try:
        return urllib.parse.urljoin(base_url, url)
    except Exception as e:
        logger.error(f"Error making absolute URL from {base_url} and {url}: {str(e)}")
        return ""


def extract_filename_from_url(url: str) -> str:
    """
    Extract filename from a URL
    
    Args:
        url: URL to extract filename from
        
    Returns:
        str: Extracted filename
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        
        # Get the filename from the path
        filename = os.path.basename(path)
        
        # If the filename is empty, use the URL hash
        if not filename:
            filename = f"file_{hash(url)}"
        
        return filename
    except Exception:
        return f"file_{hash(url)}"


def get_content_type_extension(content_type: str) -> str:
    """
    Get the file extension for a content type
    
    Args:
        content_type: Content type to get extension for
        
    Returns:
        str: File extension
    """
    # Map of content types to file extensions
    content_type_map = {
        "text/html": ".html",
        "text/plain": ".txt",
        "text/css": ".css",
        "text/javascript": ".js",
        "application/javascript": ".js",
        "application/json": ".json",
        "application/xml": ".xml",
        "text/xml": ".xml",
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/svg+xml": ".svg",
        "image/webp": ".webp",
    }
    
    # Get the base content type (without parameters)
    base_content_type = content_type.split(";")[0].strip()
    
    # Return the extension for the content type, or default to .bin
    return content_type_map.get(base_content_type, ".bin")


def create_filename_from_url(url: str, content_type: Optional[str] = None) -> str:
    """
    Create a filename from a URL and content type
    
    Args:
        url: URL to create filename from
        content_type: Content type (optional)
        
    Returns:
        str: Created filename
    """
    # Extract the filename from the URL
    filename = extract_filename_from_url(url)
    
    # If the filename doesn't have an extension and we have a content type, add the extension
    if "." not in filename and content_type:
        extension = get_content_type_extension(content_type)
        filename = f"{filename}{extension}"
    
    # Replace invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    # Limit the filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = f"{name[:245]}{ext}"
    
    return filename


def rate_limit(delay: float) -> None:
    """
    Rate limit function to delay execution
    
    Args:
        delay: Delay in seconds
    """
    time.sleep(delay)


def parse_content_type(content_type_header: str) -> Tuple[str, str]:
    """
    Parse a Content-Type header into content type and charset
    
    Args:
        content_type_header: Content-Type header value
        
    Returns:
        tuple: (content_type, charset)
    """
    content_type = "text/html"  # Default content type
    charset = "utf-8"  # Default charset
    
    if content_type_header:
        # Split the header into parts
        parts = content_type_header.split(";")
        
        # Get the content type
        content_type = parts[0].strip()
        
        # Get the charset
        for part in parts[1:]:
            part = part.strip()
            if part.startswith("charset="):
                charset = part[8:].strip().strip('"\'')
    
    return content_type, charset


def is_url_crawlable(url: str, excluded_extensions: List[str]) -> bool:
    """
    Check if a URL is crawlable
    
    Args:
        url: URL to check
        excluded_extensions: List of excluded file extensions
        
    Returns:
        bool: True if the URL is crawlable, False otherwise
    """
    # Check if the URL is valid
    if not is_valid_url(url):
        return False
    
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Check the scheme
    if parsed_url.scheme not in ["http", "https"]:
        return False
    
    # Check if the URL has an excluded extension
    path = parsed_url.path
    if path and "." in path:
        extension = os.path.splitext(path)[1].lower()
        if extension in excluded_extensions:
            return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    # Limit the filename length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = f"{name[:245]}{ext}"
    
    return sanitized 