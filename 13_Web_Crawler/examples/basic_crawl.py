#!/usr/bin/env python3
"""
Basic Crawl Example - Demonstrates basic usage of the web crawler
"""

import os
import sys
import time

# Add parent directory to path to import web_crawler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web_crawler import WebCrawler


def main():
    """Main function for the basic crawl example"""
    print("Basic Web Crawler Example")
    print("-" * 30)
    
    # Create a crawler instance
    crawler = WebCrawler(
        start_url="https://example.com",
        max_depth=2,
        max_urls=10,
        delay=1.0,
        threads=1,
        same_domain=True,
        respect_robots=True,
        user_agent="PythonWebCrawler/1.0 (Example)",
        output_dir="output"
    )
    
    # Record start time
    start_time = time.time()
    
    print(f"Starting crawl from https://example.com")
    print(f"Max depth: 2, Max URLs: 10")
    print()
    
    # Start crawling
    crawler.crawl()
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Get results
    results = crawler.get_results()
    errors = crawler.get_errors()
    
    # Print summary
    print("\nCrawling Summary:")
    print(f"  URLs crawled: {len(results)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Time taken: {elapsed_time:.2f} seconds")
    
    # Save results to JSON
    output_file = crawler.save_results("json")
    print(f"  Results saved to: {output_file}")
    
    # Generate sitemap
    sitemap_file = crawler.generate_sitemap("xml")
    print(f"  Sitemap generated: {sitemap_file}")
    
    # Print crawled URLs
    print("\nCrawled URLs:")
    for i, (url, data) in enumerate(results.items(), 1):
        print(f"  {i}. {url} - {data.get('title', 'No title')}")
    
    # Clean up
    crawler.close()


if __name__ == "__main__":
    main() 