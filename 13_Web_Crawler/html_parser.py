#!/usr/bin/env python3
"""
HTML Parser - Extracts data from HTML content
"""

import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, Tag


class HTMLParser:
    """HTML Parser class for extracting data from web pages"""
    
    def __init__(self):
        """Initialize the HTML parser"""
        # Common patterns for extracting data
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b')
    
    def parse(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract useful data
        
        Args:
            soup: BeautifulSoup object of the HTML content
            url: URL of the page
            
        Returns:
            dict: Extracted data
        """
        data = {
            "url": url,
            "title": self._extract_title(soup),
            "description": self._extract_description(soup),
            "links": self._extract_links(soup),
            "images": self._extract_images(soup),
            "headers": self._extract_headers(soup),
            "text_content": self._extract_text_content(soup),
            "emails": self._extract_emails(soup),
            "phones": self._extract_phones(soup),
            "metadata": self._extract_metadata(soup),
            "structured_data": self._extract_structured_data(soup),
        }
        
        return data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title"""
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Try to find h1 if title is not available
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.string:
            return h1_tag.string.strip()
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract the page description"""
        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
        
        # Try Open Graph description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()
        
        # Try Twitter description
        twitter_desc = soup.find("meta", attrs={"name": "twitter:description"})
        if twitter_desc and twitter_desc.get("content"):
            return twitter_desc["content"].strip()
        
        # Try to get the first paragraph
        first_p = soup.find("p")
        if first_p and first_p.string:
            return first_p.string.strip()
        
        return ""
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract links from the page"""
        links = []
        
        for a_tag in soup.find_all("a", href=True):
            link_data = {
                "url": a_tag["href"],
                "text": a_tag.get_text(strip=True),
                "title": a_tag.get("title", ""),
                "rel": a_tag.get("rel", ""),
            }
            links.append(link_data)
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract image URLs from the page"""
        images = []
        
        for img_tag in soup.find_all("img", src=True):
            src = img_tag["src"]
            if src:
                images.append(src)
        
        return images
    
    def _extract_headers(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract headers from the page"""
        headers = {
            "h1": [],
            "h2": [],
            "h3": [],
            "h4": [],
            "h5": [],
            "h6": []
        }
        
        for level in range(1, 7):
            tag_name = f"h{level}"
            for header in soup.find_all(tag_name):
                text = header.get_text(strip=True)
                if text:
                    headers[tag_name].append(text)
        
        return headers
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract the main text content from the page"""
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "noscript", "iframe", "head"]):
            script_or_style.extract()
        
        # Get the text content
        text = soup.get_text(separator="\n", strip=True)
        
        # Remove extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract email addresses from the page"""
        # Get all text content
        text_content = self._extract_text_content(soup)
        
        # Find all email addresses
        emails = set(self.email_pattern.findall(text_content))
        
        # Also check mailto links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("mailto:"):
                email = href[7:]  # Remove "mailto:"
                if "@" in email:
                    emails.add(email.split("?")[0])  # Remove any parameters
        
        return list(emails)
    
    def _extract_phones(self, soup: BeautifulSoup) -> List[str]:
        """Extract phone numbers from the page"""
        # Get all text content
        text_content = self._extract_text_content(soup)
        
        # Find all phone numbers
        phones = set(self.phone_pattern.findall(text_content))
        
        # Also check tel links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("tel:"):
                phone = href[4:]  # Remove "tel:"
                phones.add(phone)
        
        return list(phones)
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the page"""
        metadata = {}
        
        # Extract all meta tags
        for meta in soup.find_all("meta"):
            # Get the name or property
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD) from the page"""
        structured_data = []
        
        # Find all script tags with type="application/ld+json"
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string:
                try:
                    import json
                    data = json.loads(script.string)
                    structured_data.append(data)
                except json.JSONDecodeError:
                    pass
        
        return structured_data
    
    def extract_table_data(self, soup: BeautifulSoup) -> List[Dict[str, List[str]]]:
        """
        Extract data from HTML tables
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            list: List of dictionaries containing table data
        """
        tables_data = []
        
        for table_idx, table in enumerate(soup.find_all("table")):
            table_data = {"headers": [], "rows": []}
            
            # Extract headers
            thead = table.find("thead")
            if thead:
                headers = thead.find_all("th")
                if headers:
                    table_data["headers"] = [header.get_text(strip=True) for header in headers]
            
            # If no headers found in thead, try the first row
            if not table_data["headers"]:
                first_row = table.find("tr")
                if first_row:
                    headers = first_row.find_all(["th", "td"])
                    if headers:
                        table_data["headers"] = [header.get_text(strip=True) for header in headers]
            
            # Extract rows
            for row in table.find_all("tr")[1:] if table_data["headers"] else table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table_data["rows"].append(row_data)
            
            tables_data.append(table_data)
        
        return tables_data
    
    def extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract form data from the page
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            list: List of dictionaries containing form data
        """
        forms_data = []
        
        for form_idx, form in enumerate(soup.find_all("form")):
            form_data = {
                "action": form.get("action", ""),
                "method": form.get("method", "get").upper(),
                "id": form.get("id", f"form_{form_idx}"),
                "fields": []
            }
            
            # Extract form fields
            for input_field in form.find_all(["input", "textarea", "select"]):
                field_type = input_field.name
                
                if field_type == "input":
                    field_type = input_field.get("type", "text")
                
                field_data = {
                    "type": field_type,
                    "name": input_field.get("name", ""),
                    "id": input_field.get("id", ""),
                    "required": input_field.has_attr("required"),
                    "placeholder": input_field.get("placeholder", ""),
                }
                
                form_data["fields"].append(field_data)
            
            forms_data.append(form_data)
        
        return forms_data 