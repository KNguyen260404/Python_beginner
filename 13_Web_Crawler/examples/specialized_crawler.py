#!/usr/bin/env python3
"""
Specialized Crawler Example - Demonstrates how to extend the web crawler for specific use cases
"""

import os
import sys
import time
import json
from typing import Dict, Any, List, Set

# Add parent directory to path to import web_crawler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web_crawler import WebCrawler
from html_parser import HTMLParser
from bs4 import BeautifulSoup


class BlogCrawler(WebCrawler):
    """Specialized crawler for blogs that extracts article content and metadata"""
    
    def __init__(self, start_url: str, **kwargs):
        """Initialize the blog crawler"""
        # Call the parent constructor
        super().__init__(start_url, **kwargs)
        
        # Initialize blog-specific data structures
        self.articles: Dict[str, Dict[str, Any]] = {}
        self.categories: Set[str] = set()
        self.tags: Set[str] = set()
        self.authors: Set[str] = set()
        
        # Create a specialized HTML parser
        self.blog_parser = BlogHTMLParser()
    
    def _process_url(self, url: str, depth: int) -> None:
        """Override the _process_url method to add blog-specific processing"""
        # Call the parent method to do the basic processing
        super()._process_url(url, depth)
        
        # Check if this URL was successfully processed
        if url in self.url_data:
            # Get the HTML content
            content, _ = self._fetch_url(url)
            
            if content:
                # Parse the HTML
                soup = BeautifulSoup(content, "lxml")
                
                # Extract blog-specific data
                article_data = self.blog_parser.parse_article(soup, url)
                
                if article_data:
                    # Store the article data
                    self.articles[url] = article_data
                    
                    # Update categories, tags, and authors
                    if "categories" in article_data:
                        self.categories.update(article_data["categories"])
                    
                    if "tags" in article_data:
                        self.tags.update(article_data["tags"])
                    
                    if "author" in article_data and article_data["author"]:
                        self.authors.add(article_data["author"])
    
    def get_articles(self) -> Dict[str, Dict[str, Any]]:
        """Get the extracted articles"""
        return self.articles
    
    def get_categories(self) -> List[str]:
        """Get the extracted categories"""
        return sorted(list(self.categories))
    
    def get_tags(self) -> List[str]:
        """Get the extracted tags"""
        return sorted(list(self.tags))
    
    def get_authors(self) -> List[str]:
        """Get the extracted authors"""
        return sorted(list(self.authors))
    
    def save_articles(self, output_file: str) -> None:
        """Save the extracted articles to a JSON file"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "articles": list(self.articles.values()),
                "categories": self.get_categories(),
                "tags": self.get_tags(),
                "authors": self.get_authors()
            }, f, indent=2, ensure_ascii=False)


class BlogHTMLParser(HTMLParser):
    """Specialized HTML parser for blog articles"""
    
    def parse_article(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Parse a blog article
        
        Args:
            soup: BeautifulSoup object of the HTML content
            url: URL of the page
            
        Returns:
            dict: Extracted article data
        """
        # Get basic data from the parent class
        basic_data = self.parse(soup, url)
        
        # Check if this is an article page
        if not self._is_article_page(soup):
            return {}
        
        # Extract article-specific data
        article_data = {
            "url": url,
            "title": basic_data.get("title", ""),
            "description": basic_data.get("description", ""),
            "content": self._extract_article_content(soup),
            "date_published": self._extract_date_published(soup),
            "date_modified": self._extract_date_modified(soup),
            "author": self._extract_author(soup),
            "categories": self._extract_categories(soup),
            "tags": self._extract_tags(soup),
            "comments_count": self._extract_comments_count(soup),
            "featured_image": self._extract_featured_image(soup),
            "reading_time": self._extract_reading_time(soup)
        }
        
        return article_data
    
    def _is_article_page(self, soup: BeautifulSoup) -> bool:
        """Check if the page is an article page"""
        # Check for common article indicators
        article_indicators = [
            soup.find("article"),
            soup.find(class_=lambda c: c and "article" in c.lower()),
            soup.find(class_=lambda c: c and "post" in c.lower()),
            soup.find(class_=lambda c: c and "entry" in c.lower()),
            soup.find(attrs={"itemtype": "http://schema.org/BlogPosting"}),
            soup.find(attrs={"itemtype": "http://schema.org/Article"})
        ]
        
        return any(article_indicators)
    
    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        """Extract the main article content"""
        # Try common article content selectors
        content_selectors = [
            "article .entry-content",
            "article .post-content",
            ".post-content",
            ".entry-content",
            "article .content",
            ".article-content",
            "article"
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove unwanted elements
                for unwanted in content_element.select(".sharedaddy, .post-navigation, .author-bio, .related-posts, .comments, script, style"):
                    unwanted.extract()
                
                # Get the text content
                return content_element.get_text(separator="\n", strip=True)
        
        return ""
    
    def _extract_date_published(self, soup: BeautifulSoup) -> str:
        """Extract the publication date"""
        # Try meta tags first
        meta_published = soup.find("meta", property="article:published_time")
        if meta_published and meta_published.get("content"):
            return meta_published["content"]
        
        # Try common date selectors
        date_selectors = [
            ".entry-date",
            ".published",
            ".post-date",
            ".date",
            "time"
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                # Check for datetime attribute
                if date_element.get("datetime"):
                    return date_element["datetime"]
                
                # Otherwise use text content
                return date_element.get_text(strip=True)
        
        return ""
    
    def _extract_date_modified(self, soup: BeautifulSoup) -> str:
        """Extract the modification date"""
        # Try meta tags first
        meta_modified = soup.find("meta", property="article:modified_time")
        if meta_modified and meta_modified.get("content"):
            return meta_modified["content"]
        
        # Try common date selectors
        date_selectors = [
            ".updated",
            ".modified",
            ".post-modified-date"
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                # Check for datetime attribute
                if date_element.get("datetime"):
                    return date_element["datetime"]
                
                # Otherwise use text content
                return date_element.get_text(strip=True)
        
        return ""
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract the author name"""
        # Try meta tags first
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            return meta_author["content"]
        
        # Try common author selectors
        author_selectors = [
            ".author-name",
            ".author a",
            ".author",
            ".byline"
        ]
        
        for selector in author_selectors:
            author_element = soup.select_one(selector)
            if author_element:
                return author_element.get_text(strip=True)
        
        return ""
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract article categories"""
        categories = []
        
        # Try common category selectors
        category_selectors = [
            ".category",
            ".categories a",
            ".post-categories a"
        ]
        
        for selector in category_selectors:
            category_elements = soup.select(selector)
            if category_elements:
                for element in category_elements:
                    category = element.get_text(strip=True)
                    if category:
                        categories.append(category)
        
        return categories
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract article tags"""
        tags = []
        
        # Try common tag selectors
        tag_selectors = [
            ".tags a",
            ".post-tags a",
            ".tag-links a"
        ]
        
        for selector in tag_selectors:
            tag_elements = soup.select(selector)
            if tag_elements:
                for element in tag_elements:
                    tag = element.get_text(strip=True)
                    if tag:
                        tags.append(tag)
        
        return tags
    
    def _extract_comments_count(self, soup: BeautifulSoup) -> int:
        """Extract the number of comments"""
        # Try common comment count selectors
        comment_selectors = [
            ".comments-count",
            ".comment-count"
        ]
        
        for selector in comment_selectors:
            comment_element = soup.select_one(selector)
            if comment_element:
                # Try to extract the number
                text = comment_element.get_text(strip=True)
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
        
        # Count comment elements
        comments = soup.select(".comment, .commentlist li")
        if comments:
            return len(comments)
        
        return 0
    
    def _extract_featured_image(self, soup: BeautifulSoup) -> str:
        """Extract the featured image URL"""
        # Try meta tags first
        meta_image = soup.find("meta", property="og:image")
        if meta_image and meta_image.get("content"):
            return meta_image["content"]
        
        # Try common featured image selectors
        image_selectors = [
            ".post-thumbnail img",
            ".featured-image img",
            "article img:first-of-type"
        ]
        
        for selector in image_selectors:
            image_element = soup.select_one(selector)
            if image_element and image_element.get("src"):
                return image_element["src"]
        
        return ""
    
    def _extract_reading_time(self, soup: BeautifulSoup) -> int:
        """Extract or estimate the reading time in minutes"""
        # Try to find an explicit reading time
        reading_time_selectors = [
            ".reading-time",
            ".post-reading-time"
        ]
        
        for selector in reading_time_selectors:
            time_element = soup.select_one(selector)
            if time_element:
                # Try to extract the number
                text = time_element.get_text(strip=True)
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
        
        # If no explicit reading time, estimate based on word count
        content = self._extract_article_content(soup)
        if content:
            word_count = len(content.split())
            # Assume average reading speed of 200 words per minute
            reading_time = max(1, round(word_count / 200))
            return reading_time
        
        return 0


def main() -> None:
    """Main function for the specialized crawler example"""
    print("Specialized Blog Crawler Example")
    print("-" * 30)
    
    # Create a blog crawler instance
    blog_url = "https://realpython.com/blog/"  # Example blog URL
    crawler = BlogCrawler(
        start_url=blog_url,
        max_depth=2,
        max_urls=10,
        delay=1.0,
        threads=1,
        same_domain=True,
        respect_robots=True,
        user_agent="PythonBlogCrawler/1.0 (Example)",
        output_dir="blog_output"
    )
    
    # Record start time
    start_time = time.time()
    
    print(f"Starting blog crawl from {blog_url}")
    print(f"Max depth: 2, Max URLs: 10")
    print()
    
    # Start crawling
    crawler.crawl()
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Get results
    articles = crawler.get_articles()
    categories = crawler.get_categories()
    tags = crawler.get_tags()
    authors = crawler.get_authors()
    
    # Print summary
    print("\nCrawling Summary:")
    print(f"  URLs crawled: {len(crawler.get_results())}")
    print(f"  Articles found: {len(articles)}")
    print(f"  Categories found: {len(categories)}")
    print(f"  Tags found: {len(tags)}")
    print(f"  Authors found: {len(authors)}")
    print(f"  Time taken: {elapsed_time:.2f} seconds")
    
    # Print article titles
    if articles:
        print("\nArticles found:")
        for i, (url, article) in enumerate(articles.items(), 1):
            print(f"  {i}. {article.get('title', 'No title')}")
            print(f"     Author: {article.get('author', 'Unknown')}")
            print(f"     Date: {article.get('date_published', 'Unknown')}")
            print(f"     Reading time: {article.get('reading_time', 0)} min")
    
    # Save articles to JSON
    output_file = os.path.join(crawler.output_dir, "blog_articles.json")
    crawler.save_articles(output_file)
    print(f"\nArticles saved to: {output_file}")
    
    # Clean up
    crawler.close()


if __name__ == "__main__":
    main() 