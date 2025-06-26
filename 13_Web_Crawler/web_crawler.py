#!/usr/bin/env python3
"""
Web Crawler - Core Implementation
"""

import os
import time
import logging
import threading
import queue
import urllib.parse
from collections import defaultdict
from typing import Dict, List, Set, Optional, Any, Tuple
import requests
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError
from bs4 import BeautifulSoup
import validators

from html_parser import HTMLParser
from robots_parser import RobotsParser
from data_storage import DataStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class WebCrawler:
    """Main web crawler class that handles the crawling process"""
    
    def __init__(
        self,
        start_url: str,
        max_depth: int = 2,
        delay: float = 0.5,
        max_urls: int = 100,
        respect_robots: bool = True,
        same_domain: bool = True,
        threads: int = 1,
        user_agent: str = "PythonWebCrawler/1.0",
        timeout: int = 10,
        output_dir: str = "output",
        download_images: bool = False,
        download_files: bool = False,
        file_extensions: List[str] = None,
    ):
        """
        Initialize the web crawler with configuration parameters
        
        Args:
            start_url: The URL to start crawling from
            max_depth: Maximum depth to crawl (default: 2)
            delay: Delay between requests in seconds (default: 0.5)
            max_urls: Maximum number of URLs to crawl (default: 100)
            respect_robots: Whether to respect robots.txt (default: True)
            same_domain: Whether to stay on the same domain (default: True)
            threads: Number of threads to use (default: 1)
            user_agent: User agent string to use (default: PythonWebCrawler/1.0)
            timeout: Request timeout in seconds (default: 10)
            output_dir: Directory to save output files (default: output)
            download_images: Whether to download images (default: False)
            download_files: Whether to download files (default: False)
            file_extensions: List of file extensions to download (default: None)
        """
        # Validate the start URL
        if not validators.url(start_url):
            raise ValueError(f"Invalid URL: {start_url}")
        
        self.start_url = start_url
        self.max_depth = max_depth
        self.delay = delay
        self.max_urls = max_urls
        self.respect_robots = respect_robots
        self.same_domain = same_domain
        self.threads = threads
        self.user_agent = user_agent
        self.timeout = timeout
        self.output_dir = output_dir
        self.download_images = download_images
        self.download_files = download_files
        self.file_extensions = file_extensions or ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
        
        # Parse the domain from the start URL
        parsed_url = urllib.parse.urlparse(start_url)
        self.domain = parsed_url.netloc
        self.scheme = parsed_url.scheme
        
        # Initialize data structures
        self.visited_urls: Set[str] = set()
        self.urls_queue: queue.Queue = queue.Queue()
        self.urls_in_queue: Set[str] = set()
        self.url_data: Dict[str, Dict[str, Any]] = {}
        self.errors: Dict[str, str] = {}
        
        # Initialize components
        self.html_parser = HTMLParser()
        self.robots_parser = RobotsParser(self.user_agent) if self.respect_robots else None
        self.data_storage = DataStorage(self.output_dir)
        
        # Thread synchronization
        self.lock = threading.Lock()
        self.active_threads = 0
        self.crawl_complete = threading.Event()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Add the start URL to the queue with depth 0
        self._add_url_to_queue(self.start_url, 0)
        
        # Session for making requests
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def _add_url_to_queue(self, url: str, depth: int) -> bool:
        """
        Add a URL to the crawling queue if it hasn't been visited or queued
        
        Args:
            url: URL to add
            depth: Current depth level
            
        Returns:
            bool: True if URL was added, False otherwise
        """
        # Normalize the URL
        url = self._normalize_url(url)
        
        # Check if URL is valid
        if not url or not validators.url(url):
            return False
        
        # Check if we're staying in the same domain
        if self.same_domain:
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.netloc != self.domain:
                return False
        
        # Check if URL has already been visited or queued
        with self.lock:
            if url in self.visited_urls or url in self.urls_in_queue:
                return False
            
            # Check if we've reached the maximum number of URLs
            if len(self.visited_urls) + len(self.urls_in_queue) >= self.max_urls:
                return False
            
            # Check if we've reached the maximum depth
            if depth > self.max_depth:
                return False
            
            # Check robots.txt
            if self.respect_robots and self.robots_parser:
                if not self.robots_parser.can_fetch(url):
                    logger.debug(f"Robots.txt disallows: {url}")
                    return False
            
            # Add URL to the queue
            self.urls_queue.put((url, depth))
            self.urls_in_queue.add(url)
            return True
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize a URL by removing fragments and trailing slashes
        
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
            if normalized.endswith("/") and normalized != f"{self.scheme}://{self.domain}/":
                normalized = normalized[:-1]
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {str(e)}")
            return url
    
    def _make_absolute_url(self, base_url: str, url: str) -> str:
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
    
    def _fetch_url(self, url: str) -> Tuple[Optional[str], Optional[requests.Response]]:
        """
        Fetch the content of a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            tuple: (content, response) or (None, None) on error
        """
        try:
            # Respect the delay between requests
            time.sleep(self.delay)
            
            # Make the request
            response = self.session.get(url, timeout=self.timeout)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Check if the content is HTML
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    return response.text, response
                else:
                    logger.debug(f"Skipping non-HTML content: {url} (Content-Type: {content_type})")
                    return None, response
            else:
                logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                self.errors[url] = f"HTTP {response.status_code}"
                return None, None
                
        except RequestException as e:
            logger.warning(f"Request error for {url}: {str(e)}")
            self.errors[url] = f"Request error: {str(e)}"
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
            self.errors[url] = f"Unexpected error: {str(e)}"
            return None, None
    
    def _process_url(self, url: str, depth: int) -> None:
        """
        Process a single URL: fetch it, extract links, and add them to the queue
        
        Args:
            url: URL to process
            depth: Current depth level
        """
        logger.info(f"Crawling: {url} (depth: {depth})")
        
        # Fetch the URL content
        content, response = self._fetch_url(url)
        
        # Mark URL as visited
        with self.lock:
            self.visited_urls.add(url)
            if url in self.urls_in_queue:
                self.urls_in_queue.remove(url)
        
        # If content is None, there was an error or non-HTML content
        if content is None:
            return
        
        # Parse the HTML
        soup = BeautifulSoup(content, "lxml")
        
        # Extract data using the HTML parser
        page_data = self.html_parser.parse(soup, url)
        
        # Store the data
        with self.lock:
            self.url_data[url] = {
                "url": url,
                "depth": depth,
                "title": page_data.get("title", ""),
                "description": page_data.get("description", ""),
                "links": page_data.get("links", []),
                "images": page_data.get("images", []),
                "headers": page_data.get("headers", {}),
                "text_content": page_data.get("text_content", ""),
                "timestamp": time.time()
            }
        
        # Download images if requested
        if self.download_images and response:
            for img_url in page_data.get("images", []):
                absolute_img_url = self._make_absolute_url(url, img_url)
                self._download_resource(absolute_img_url, "images")
        
        # Download files if requested
        if self.download_files and response:
            for link in page_data.get("links", []):
                link_url = link.get("url", "")
                if any(link_url.endswith(ext) for ext in self.file_extensions):
                    absolute_link_url = self._make_absolute_url(url, link_url)
                    self._download_resource(absolute_link_url, "files")
        
        # Extract links and add them to the queue
        for link in page_data.get("links", []):
            link_url = link.get("url", "")
            if link_url:
                absolute_link_url = self._make_absolute_url(url, link_url)
                self._add_url_to_queue(absolute_link_url, depth + 1)
    
    def _download_resource(self, url: str, resource_type: str) -> None:
        """
        Download a resource (image or file) from a URL
        
        Args:
            url: URL of the resource
            resource_type: Type of resource ("images" or "files")
        """
        try:
            # Create the resource directory if it doesn't exist
            resource_dir = os.path.join(self.output_dir, resource_type)
            os.makedirs(resource_dir, exist_ok=True)
            
            # Extract the filename from the URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # If the filename is empty or invalid, use the URL hash
            if not filename or filename == "":
                filename = f"{hash(url)}"
            
            # Create the full path
            filepath = os.path.join(resource_dir, filename)
            
            # Download the resource
            logger.debug(f"Downloading {resource_type}: {url}")
            response = self.session.get(url, timeout=self.timeout, stream=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.debug(f"Downloaded {url} to {filepath}")
            else:
                logger.warning(f"Failed to download {url}: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
    
    def _worker(self) -> None:
        """Worker thread function for multi-threaded crawling"""
        with self.lock:
            self.active_threads += 1
        
        try:
            while not self.crawl_complete.is_set():
                try:
                    # Get a URL from the queue with a timeout
                    url, depth = self.urls_queue.get(timeout=1)
                    
                    # Process the URL
                    self._process_url(url, depth)
                    
                    # Mark the task as done
                    self.urls_queue.task_done()
                    
                except queue.Empty:
                    # Check if we're done
                    with self.lock:
                        if self.active_threads == 1 and self.urls_queue.empty():
                            self.crawl_complete.set()
                            break
                
                except Exception as e:
                    logger.error(f"Error in worker thread: {str(e)}")
        
        finally:
            with self.lock:
                self.active_threads -= 1
    
    def crawl(self) -> None:
        """Start the crawling process"""
        logger.info(f"Starting crawl from {self.start_url} with max depth {self.max_depth}")
        
        # Initialize robots.txt parser if needed
        if self.respect_robots:
            robots_url = f"{self.scheme}://{self.domain}/robots.txt"
            self.robots_parser.fetch(robots_url)
        
        # Create and start worker threads
        threads = []
        for _ in range(self.threads):
            thread = threading.Thread(target=self._worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        logger.info(f"Crawl complete. Visited {len(self.visited_urls)} URLs.")
    
    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the crawling results
        
        Returns:
            dict: Crawling results
        """
        return self.url_data
    
    def get_errors(self) -> Dict[str, str]:
        """
        Get the crawling errors
        
        Returns:
            dict: Crawling errors
        """
        return self.errors
    
    def save_results(self, format: str = "json") -> str:
        """
        Save the crawling results to a file
        
        Args:
            format: Output format ("json", "csv", or "sqlite")
            
        Returns:
            str: Path to the saved file
        """
        return self.data_storage.save(self.url_data, format)
    
    def generate_sitemap(self, format: str = "xml") -> str:
        """
        Generate a sitemap from the crawling results
        
        Args:
            format: Sitemap format ("xml" or "txt")
            
        Returns:
            str: Path to the generated sitemap
        """
        sitemap_data = {url: data.get("timestamp", time.time()) for url, data in self.url_data.items()}
        return self.data_storage.generate_sitemap(sitemap_data, format)
    
    def close(self) -> None:
        """Clean up resources"""
        self.session.close()


if __name__ == "__main__":
    # Simple test if run directly
    crawler = WebCrawler("https://example.com", max_depth=1)
    crawler.crawl()
    results = crawler.get_results()
    print(f"Crawled {len(results)} pages") 