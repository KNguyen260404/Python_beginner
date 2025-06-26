#!/usr/bin/env python3
"""
Advanced Crawl Example - Demonstrates advanced usage of the web crawler
"""

import os
import sys
import time
import argparse
from typing import Dict, Any
import colorama

# Add parent directory to path to import web_crawler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web_crawler import WebCrawler

# Initialize colorama
colorama.init()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Advanced Web Crawler Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--url", "-u",
        default="https://python.org",
        help="URL to start crawling from"
    )
    
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=2,
        help="Maximum depth to crawl"
    )
    
    parser.add_argument(
        "--max-urls", "-m",
        type=int,
        default=20,
        help="Maximum number of URLs to crawl"
    )
    
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=3,
        help="Number of threads to use"
    )
    
    parser.add_argument(
        "--output-format", "-f",
        choices=["json", "csv", "sqlite"],
        default="json",
        help="Output format"
    )
    
    return parser.parse_args()


def print_colored_summary(results: Dict[str, Dict[str, Any]], errors: Dict[str, str], elapsed_time: float) -> None:
    """Print a colored summary of the crawling results"""
    print(f"\n{colorama.Fore.GREEN}Crawling Summary:{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}URLs crawled: {colorama.Fore.YELLOW}{len(results)}{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Errors: {colorama.Fore.YELLOW}{len(errors)}{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Time taken: {colorama.Fore.YELLOW}{elapsed_time:.2f} seconds{colorama.Style.RESET_ALL}")
    
    # Print statistics
    total_links = sum(len(data.get("links", [])) for data in results.values())
    total_images = sum(len(data.get("images", [])) for data in results.values())
    
    print(f"\n{colorama.Fore.GREEN}Statistics:{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Total links found: {colorama.Fore.YELLOW}{total_links}{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Total images found: {colorama.Fore.YELLOW}{total_images}{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Average links per page: {colorama.Fore.YELLOW}{total_links / len(results) if results else 0:.2f}{colorama.Style.RESET_ALL}")
    
    # Print errors if any
    if errors:
        print(f"\n{colorama.Fore.RED}Errors:{colorama.Style.RESET_ALL}")
        for url, error in list(errors.items())[:5]:  # Show only first 5 errors
            print(f"  {colorama.Fore.WHITE}{url}: {colorama.Fore.RED}{error}{colorama.Style.RESET_ALL}")
        
        if len(errors) > 5:
            print(f"  {colorama.Fore.WHITE}... and {len(errors) - 5} more errors{colorama.Style.RESET_ALL}")


def print_crawled_urls(results: Dict[str, Dict[str, Any]]) -> None:
    """Print crawled URLs with titles"""
    print(f"\n{colorama.Fore.GREEN}Crawled URLs:{colorama.Style.RESET_ALL}")
    
    for i, (url, data) in enumerate(list(results.items())[:10], 1):  # Show only first 10 URLs
        title = data.get("title", "No title")
        print(f"  {colorama.Fore.WHITE}{i}. {colorama.Fore.CYAN}{url}{colorama.Style.RESET_ALL}")
        print(f"     {colorama.Fore.YELLOW}Title: {title}{colorama.Style.RESET_ALL}")
        print(f"     {colorama.Fore.YELLOW}Links: {len(data.get('links', []))}, Images: {len(data.get('images', []))}{colorama.Style.RESET_ALL}")
    
    if len(results) > 10:
        print(f"  {colorama.Fore.WHITE}... and {len(results) - 10} more URLs{colorama.Style.RESET_ALL}")


def main() -> None:
    """Main function for the advanced crawl example"""
    args = parse_arguments()
    
    print(f"{colorama.Fore.CYAN}Advanced Web Crawler Example{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}{'-' * 30}{colorama.Style.RESET_ALL}")
    
    # Create output directory
    output_dir = "advanced_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a crawler instance with advanced settings
    crawler = WebCrawler(
        start_url=args.url,
        max_depth=args.depth,
        max_urls=args.max_urls,
        delay=0.5,
        threads=args.threads,
        same_domain=True,
        respect_robots=True,
        user_agent="PythonWebCrawler/1.0 (Advanced Example)",
        output_dir=output_dir,
        download_images=True,
        download_files=True,
        file_extensions=['.pdf', '.doc', '.docx', '.xls', '.xlsx']
    )
    
    # Record start time
    start_time = time.time()
    
    print(f"{colorama.Fore.GREEN}Starting crawl from {colorama.Fore.YELLOW}{args.url}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN}Max depth: {colorama.Fore.YELLOW}{args.depth}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN}Max URLs: {colorama.Fore.YELLOW}{args.max_urls}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN}Threads: {colorama.Fore.YELLOW}{args.threads}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN}Downloading images and files: {colorama.Fore.YELLOW}Yes{colorama.Style.RESET_ALL}")
    print()
    
    # Start crawling with progress updates
    print(f"{colorama.Fore.GREEN}Crawling in progress...{colorama.Style.RESET_ALL}")
    crawler.crawl()
    
    # Print progress updates
    while not crawler.crawl_complete.is_set():
        current_count = len(crawler.visited_urls)
        queue_size = crawler.urls_queue.qsize()
        sys.stdout.write(f"\r{colorama.Fore.GREEN}Progress: {colorama.Fore.YELLOW}{current_count}/{args.max_urls} URLs crawled, {queue_size} in queue{colorama.Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.5)
    
    # Final progress update
    current_count = len(crawler.visited_urls)
    sys.stdout.write(f"\r{colorama.Fore.GREEN}Progress: {colorama.Fore.YELLOW}{current_count}/{args.max_urls} URLs crawled, 0 in queue{colorama.Style.RESET_ALL}\n")
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Get results
    results = crawler.get_results()
    errors = crawler.get_errors()
    
    # Print summary
    print_colored_summary(results, errors, elapsed_time)
    
    # Print crawled URLs
    print_crawled_urls(results)
    
    # Save results
    output_file = crawler.save_results(args.output_format)
    print(f"\n{colorama.Fore.GREEN}Results saved to: {colorama.Fore.YELLOW}{output_file}{colorama.Style.RESET_ALL}")
    
    # Generate sitemap
    sitemap_file = crawler.generate_sitemap("xml")
    print(f"{colorama.Fore.GREEN}Sitemap generated: {colorama.Fore.YELLOW}{sitemap_file}{colorama.Style.RESET_ALL}")
    
    # Clean up
    crawler.close()


if __name__ == "__main__":
    main() 