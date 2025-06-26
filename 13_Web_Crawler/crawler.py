#!/usr/bin/env python3
"""
Web Crawler - Command Line Interface
"""

import os
import sys
import argparse
import logging
import time
from typing import Dict, Any
import colorama
from tqdm import tqdm

from web_crawler import WebCrawler

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up the argument parser for the command-line interface
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Web Crawler - A tool for crawling websites and extracting information",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        "--url", "-u",
        required=True,
        help="URL to start crawling from"
    )
    
    # Crawling options
    crawling_group = parser.add_argument_group("Crawling Options")
    crawling_group.add_argument(
        "--depth", "-d",
        type=int,
        default=2,
        help="Maximum depth to crawl"
    )
    crawling_group.add_argument(
        "--max-urls", "-m",
        type=int,
        default=100,
        help="Maximum number of URLs to crawl"
    )
    crawling_group.add_argument(
        "--delay", "-w",
        type=float,
        default=0.5,
        help="Delay between requests in seconds"
    )
    crawling_group.add_argument(
        "--threads", "-t",
        type=int,
        default=1,
        help="Number of threads to use"
    )
    crawling_group.add_argument(
        "--same-domain", "-s",
        action="store_true",
        help="Stay on the same domain"
    )
    crawling_group.add_argument(
        "--respect-robots",
        action="store_true",
        help="Respect robots.txt"
    )
    crawling_group.add_argument(
        "--user-agent", "-a",
        default="PythonWebCrawler/1.0",
        help="User agent string to use"
    )
    crawling_group.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Directory to save output files"
    )
    output_group.add_argument(
        "--output-format", "-f",
        choices=["json", "csv", "sqlite"],
        default="json",
        help="Output format"
    )
    output_group.add_argument(
        "--sitemap",
        action="store_true",
        help="Generate a sitemap"
    )
    output_group.add_argument(
        "--sitemap-format",
        choices=["xml", "txt"],
        default="xml",
        help="Sitemap format"
    )
    
    # Download options
    download_group = parser.add_argument_group("Download Options")
    download_group.add_argument(
        "--images",
        action="store_true",
        help="Download images"
    )
    download_group.add_argument(
        "--files",
        action="store_true",
        help="Download files"
    )
    download_group.add_argument(
        "--file-extensions",
        default=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar,.tar,.gz",
        help="Comma-separated list of file extensions to download"
    )
    
    # Logging options
    logging_group = parser.add_argument_group("Logging Options")
    logging_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    logging_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Disable all output except errors"
    )
    logging_group.add_argument(
        "--log-file", "-l",
        help="Log file to write to"
    )
    
    return parser


def configure_logging(args: argparse.Namespace) -> None:
    """
    Configure logging based on command-line arguments
    
    Args:
        args: Command-line arguments
    """
    # Set log level
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Configure root logger
    logging.getLogger().setLevel(log_level)
    
    # Configure file logging if requested
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        logging.getLogger().addHandler(file_handler)


def print_banner() -> None:
    """Print a banner for the web crawler"""
    banner = f"""
{colorama.Fore.CYAN}╔═══════════════════════════════════════════════╗
║ {colorama.Fore.GREEN}Web Crawler {colorama.Fore.WHITE}v1.0                           {colorama.Fore.CYAN}║
║ {colorama.Fore.WHITE}A tool for crawling websites and extracting info {colorama.Fore.CYAN}║
╚═══════════════════════════════════════════════╝{colorama.Style.RESET_ALL}
    """
    print(banner)


def print_summary(crawler: WebCrawler, output_file: str, start_time: float) -> None:
    """
    Print a summary of the crawling results
    
    Args:
        crawler: WebCrawler instance
        output_file: Path to the output file
        start_time: Start time of the crawling process
    """
    elapsed_time = time.time() - start_time
    results = crawler.get_results()
    errors = crawler.get_errors()
    
    print(f"\n{colorama.Fore.GREEN}Crawling Summary:{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}URLs crawled: {colorama.Fore.YELLOW}{len(results)}{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Errors: {colorama.Fore.YELLOW}{len(errors)}{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Time taken: {colorama.Fore.YELLOW}{elapsed_time:.2f} seconds{colorama.Style.RESET_ALL}")
    print(f"  {colorama.Fore.WHITE}Output file: {colorama.Fore.YELLOW}{output_file}{colorama.Style.RESET_ALL}")


def main() -> None:
    """Main function for the command-line interface"""
    # Set up the argument parser
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(args)
    
    # Print banner
    print_banner()
    
    try:
        # Parse file extensions
        file_extensions = [ext.strip() for ext in args.file_extensions.split(",")]
        
        # Create the web crawler
        crawler = WebCrawler(
            start_url=args.url,
            max_depth=args.depth,
            delay=args.delay,
            max_urls=args.max_urls,
            respect_robots=args.respect_robots,
            same_domain=args.same_domain,
            threads=args.threads,
            user_agent=args.user_agent,
            timeout=args.timeout,
            output_dir=args.output_dir,
            download_images=args.images,
            download_files=args.files,
            file_extensions=file_extensions,
        )
        
        # Record start time
        start_time = time.time()
        
        # Start crawling
        print(f"{colorama.Fore.GREEN}Starting crawl from {colorama.Fore.YELLOW}{args.url}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}Max depth: {colorama.Fore.YELLOW}{args.depth}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}Max URLs: {colorama.Fore.YELLOW}{args.max_urls}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}Threads: {colorama.Fore.YELLOW}{args.threads}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}Respect robots.txt: {colorama.Fore.YELLOW}{args.respect_robots}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}Same domain only: {colorama.Fore.YELLOW}{args.same_domain}{colorama.Style.RESET_ALL}")
        print()
        
        # Create a progress bar
        with tqdm(total=args.max_urls, desc="Crawling", unit="URL") as pbar:
            # Update the progress bar periodically
            last_count = 0
            crawler.crawl()
            while not crawler.crawl_complete.is_set():
                current_count = len(crawler.visited_urls)
                pbar.update(current_count - last_count)
                last_count = current_count
                time.sleep(0.1)
            
            # Final update
            current_count = len(crawler.visited_urls)
            pbar.update(current_count - last_count)
        
        # Save the results
        output_file = crawler.save_results(args.output_format)
        
        # Generate a sitemap if requested
        if args.sitemap:
            sitemap_file = crawler.generate_sitemap(args.sitemap_format)
            print(f"{colorama.Fore.GREEN}Generated sitemap: {colorama.Fore.YELLOW}{sitemap_file}{colorama.Style.RESET_ALL}")
        
        # Print a summary
        print_summary(crawler, output_file, start_time)
        
        # Clean up
        crawler.close()
        
    except KeyboardInterrupt:
        print(f"\n{colorama.Fore.RED}Crawling interrupted by user{colorama.Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{colorama.Fore.RED}Error: {str(e)}{colorama.Style.RESET_ALL}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 