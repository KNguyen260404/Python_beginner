# Web Crawler Project

A comprehensive web crawler implementation in Python that can crawl websites, extract information, and save the results. This project demonstrates various web crawling techniques, HTML parsing, and data extraction.

## Features

- Basic web crawling with depth control
- URL filtering and domain restriction
- HTML content parsing and data extraction
- Image and file downloading
- Sitemap generation
- Respect for robots.txt
- Rate limiting to avoid overloading servers
- Multi-threaded crawling for better performance
- Data storage in various formats (JSON, CSV, SQLite)
- Command-line interface for easy usage

## Requirements

- Python 3.8+
- BeautifulSoup4
- Requests
- lxml
- urllib3
- tqdm
- colorama
- python-dateutil
- validators
- sqlalchemy

## Project Structure

- `crawler.py`: Main command-line interface
- `web_crawler.py`: Core crawler implementation
- `html_parser.py`: HTML parsing and data extraction
- `robots_parser.py`: Robots.txt parsing and handling
- `data_storage.py`: Data storage implementations
- `utils.py`: Utility functions
- `examples/`: Example usage scripts
  - `basic_crawl.py`: Simple crawling example
  - `advanced_crawl.py`: Advanced crawling with more features
  - `specialized_crawler.py`: Example of extending the crawler for specific use cases

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from web_crawler import WebCrawler

# Create a crawler instance
crawler = WebCrawler(start_url="https://example.com", max_depth=2)

# Start crawling
crawler.crawl()

# Get results
results = crawler.get_results()
print(f"Crawled {len(results)} pages")
```

### Command-line Interface

```bash
python crawler.py --url https://example.com --depth 2 --output-format json
```

### Advanced Options

```bash
python crawler.py --url https://example.com --depth 3 --threads 5 --delay 1 --respect-robots --images --files --output-format sqlite
```

## Extending the Crawler

The web crawler can be extended for specialized use cases by subclassing the `WebCrawler` class:

```python
from web_crawler import WebCrawler

class SpecializedCrawler(WebCrawler):
    def __init__(self, start_url, **kwargs):
        super().__init__(start_url, **kwargs)
        # Add custom initialization
        
    def _process_url(self, url, depth):
        # Call the parent method
        super()._process_url(url, depth)
        # Add custom processing
```

See the `examples/specialized_crawler.py` file for a complete example of extending the crawler.

## Output Formats

The crawler can save results in multiple formats:

- **JSON**: Detailed information in a structured format
- **CSV**: Simplified data in tabular format
- **SQLite**: Relational database with tables for pages, links, and images

## License

MIT License 