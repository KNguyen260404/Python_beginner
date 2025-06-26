#!/usr/bin/env python3
"""
Data Storage - Handles saving crawl results to different formats
"""

import os
import json
import csv
import time
import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles saving crawl results to different formats"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the data storage
        
        Args:
            output_dir: Directory to save output files (default: output)
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save(self, data: Dict[str, Dict[str, Any]], format: str = "json") -> str:
        """
        Save crawl results to a file
        
        Args:
            data: Crawl results data
            format: Output format ("json", "csv", or "sqlite")
            
        Returns:
            str: Path to the saved file
        """
        if format == "json":
            return self._save_json(data)
        elif format == "csv":
            return self._save_csv(data)
        elif format == "sqlite":
            return self._save_sqlite(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_json(self, data: Dict[str, Dict[str, Any]]) -> str:
        """
        Save crawl results to a JSON file
        
        Args:
            data: Crawl results data
            
        Returns:
            str: Path to the saved file
        """
        # Create the output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crawl_results_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert data to a list for better JSON serialization
        data_list = list(data.values())
        
        # Save the data to a JSON file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved crawl results to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving JSON file: {str(e)}")
            return ""
    
    def _save_csv(self, data: Dict[str, Dict[str, Any]]) -> str:
        """
        Save crawl results to a CSV file
        
        Args:
            data: Crawl results data
            
        Returns:
            str: Path to the saved file
        """
        # Create the output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crawl_results_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert data to a list for CSV serialization
        data_list = list(data.values())
        
        # Skip if no data
        if not data_list:
            logger.warning("No data to save to CSV")
            return ""
        
        try:
            # Get the fieldnames from the first item
            # We need to flatten the data for CSV
            fieldnames = ["url", "title", "description", "text_content", "timestamp"]
            
            # Save the data to a CSV file
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data_list:
                    # Create a flattened version of the item
                    flattened = {
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "text_content": item.get("text_content", "")[:1000],  # Limit text content
                        "timestamp": item.get("timestamp", ""),
                    }
                    writer.writerow(flattened)
            
            logger.info(f"Saved crawl results to {filepath}")
            
            # Also save links and images to separate CSV files
            self._save_links_csv(data_list, timestamp)
            self._save_images_csv(data_list, timestamp)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving CSV file: {str(e)}")
            return ""
    
    def _save_links_csv(self, data_list: List[Dict[str, Any]], timestamp: str) -> str:
        """
        Save links to a separate CSV file
        
        Args:
            data_list: List of crawl results
            timestamp: Timestamp string
            
        Returns:
            str: Path to the saved file
        """
        # Create the output filename
        filename = f"crawl_links_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Save the links to a CSV file
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["source_url", "target_url", "text", "title"])
                
                for item in data_list:
                    source_url = item.get("url", "")
                    links = item.get("links", [])
                    
                    for link in links:
                        writer.writerow([
                            source_url,
                            link.get("url", ""),
                            link.get("text", ""),
                            link.get("title", "")
                        ])
            
            logger.info(f"Saved links to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving links CSV file: {str(e)}")
            return ""
    
    def _save_images_csv(self, data_list: List[Dict[str, Any]], timestamp: str) -> str:
        """
        Save images to a separate CSV file
        
        Args:
            data_list: List of crawl results
            timestamp: Timestamp string
            
        Returns:
            str: Path to the saved file
        """
        # Create the output filename
        filename = f"crawl_images_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Save the images to a CSV file
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["source_url", "image_url"])
                
                for item in data_list:
                    source_url = item.get("url", "")
                    images = item.get("images", [])
                    
                    for image in images:
                        writer.writerow([source_url, image])
            
            logger.info(f"Saved images to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving images CSV file: {str(e)}")
            return ""
    
    def _save_sqlite(self, data: Dict[str, Dict[str, Any]]) -> str:
        """
        Save crawl results to a SQLite database
        
        Args:
            data: Crawl results data
            
        Returns:
            str: Path to the saved file
        """
        # Create the output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crawl_results_{timestamp}.db"
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert data to a list
        data_list = list(data.values())
        
        try:
            # Create a connection to the SQLite database
            conn = sqlite3.connect(filepath)
            cursor = conn.cursor()
            
            # Create the pages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    text_content TEXT,
                    depth INTEGER,
                    timestamp REAL
                )
            ''')
            
            # Create the links table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT,
                    target_url TEXT,
                    text TEXT,
                    title TEXT,
                    FOREIGN KEY (source_url) REFERENCES pages (url)
                )
            ''')
            
            # Create the images table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT,
                    image_url TEXT,
                    FOREIGN KEY (source_url) REFERENCES pages (url)
                )
            ''')
            
            # Insert data into the pages table
            for item in data_list:
                cursor.execute(
                    "INSERT OR IGNORE INTO pages (url, title, description, text_content, depth, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        item.get("url", ""),
                        item.get("title", ""),
                        item.get("description", ""),
                        item.get("text_content", ""),
                        item.get("depth", 0),
                        item.get("timestamp", time.time())
                    )
                )
                
                # Insert links
                source_url = item.get("url", "")
                for link in item.get("links", []):
                    cursor.execute(
                        "INSERT INTO links (source_url, target_url, text, title) VALUES (?, ?, ?, ?)",
                        (
                            source_url,
                            link.get("url", ""),
                            link.get("text", ""),
                            link.get("title", "")
                        )
                    )
                
                # Insert images
                for image in item.get("images", []):
                    cursor.execute(
                        "INSERT INTO images (source_url, image_url) VALUES (?, ?)",
                        (source_url, image)
                    )
            
            # Commit the changes and close the connection
            conn.commit()
            conn.close()
            
            logger.info(f"Saved crawl results to SQLite database: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving SQLite database: {str(e)}")
            return ""
    
    def generate_sitemap(self, urls: Dict[str, float], format: str = "xml") -> str:
        """
        Generate a sitemap from the crawl results
        
        Args:
            urls: Dictionary of URLs and their timestamps
            format: Sitemap format ("xml" or "txt")
            
        Returns:
            str: Path to the generated sitemap
        """
        if format == "xml":
            return self._generate_xml_sitemap(urls)
        elif format == "txt":
            return self._generate_txt_sitemap(urls)
        else:
            raise ValueError(f"Unsupported sitemap format: {format}")
    
    def _generate_xml_sitemap(self, urls: Dict[str, float]) -> str:
        """
        Generate an XML sitemap
        
        Args:
            urls: Dictionary of URLs and their timestamps
            
        Returns:
            str: Path to the generated sitemap
        """
        # Create the output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sitemap_{timestamp}.xml"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Generate the XML sitemap
            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                
                for url, timestamp in urls.items():
                    # Convert timestamp to ISO format
                    date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                    
                    f.write('  <url>\n')
                    f.write(f'    <loc>{url}</loc>\n')
                    f.write(f'    <lastmod>{date}</lastmod>\n')
                    f.write('  </url>\n')
                
                f.write('</urlset>\n')
            
            logger.info(f"Generated XML sitemap: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating XML sitemap: {str(e)}")
            return ""
    
    def _generate_txt_sitemap(self, urls: Dict[str, float]) -> str:
        """
        Generate a text sitemap
        
        Args:
            urls: Dictionary of URLs and their timestamps
            
        Returns:
            str: Path to the generated sitemap
        """
        # Create the output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sitemap_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Generate the text sitemap
            with open(filepath, "w", encoding="utf-8") as f:
                for url in urls.keys():
                    f.write(f"{url}\n")
            
            logger.info(f"Generated text sitemap: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating text sitemap: {str(e)}")
            return "" 