#!/usr/bin/env python3
"""
DNS Records - Manages DNS records and provides a database interface

This module provides functionality for managing DNS records and
a simple database interface for storing and retrieving records.
"""

import os
import json
import ipaddress
import logging
import threading
import socket
from typing import Dict, List, Tuple, Optional, Any, Union

from dns_message import DNSResourceRecord, DNSType, DNSClass

# Configure logging
logger = logging.getLogger(__name__)


class DNSRecordDB:
    """Database for DNS records"""
    
    def __init__(self, db_file: Optional[str] = None):
        """
        Initialize the DNS record database
        
        Args:
            db_file: Path to the database file (default: None, in-memory only)
        """
        self.db_file = db_file
        self.records: Dict[str, Dict[str, List[DNSResourceRecord]]] = {}
        self.lock = threading.RLock()
        
        # Load records from file if provided
        if db_file and os.path.exists(db_file):
            self.load_from_file(db_file)
    
    def add_record(self, domain: str, record_type: Union[DNSType, str], record_data: str, 
                  ttl: int = 3600, record_class: Union[DNSClass, str] = DNSClass.IN) -> bool:
        """
        Add a DNS record to the database
        
        Args:
            domain: Domain name
            record_type: Record type (DNSType or string)
            record_data: Record data (string format)
            ttl: Time to live in seconds (default: 3600)
            record_class: Record class (default: IN)
            
        Returns:
            bool: True if the record was added successfully, False otherwise
        """
        with self.lock:
            # Normalize the domain name
            domain = domain.lower()
            if domain.endswith('.'):
                domain = domain[:-1]
            
            # Convert string record type to DNSType
            if isinstance(record_type, str):
                try:
                    record_type = DNSType[record_type]
                except KeyError:
                    logger.error(f"Invalid record type: {record_type}")
                    return False
            
            # Convert string record class to DNSClass
            if isinstance(record_class, str):
                try:
                    record_class = DNSClass[record_class]
                except KeyError:
                    logger.error(f"Invalid record class: {record_class}")
                    return False
            
            # Create the record
            record = self._create_record(domain, record_type, record_data, ttl, record_class)
            if not record:
                return False
            
            # Add the record to the database
            if domain not in self.records:
                self.records[domain] = {}
            
            type_key = record_type.name
            if type_key not in self.records[domain]:
                self.records[domain][type_key] = []
            
            # Check if the record already exists
            for existing_record in self.records[domain][type_key]:
                if existing_record.rdata == record.rdata:
                    # Update the TTL if the record already exists
                    existing_record.ttl = ttl
                    logger.debug(f"Updated TTL for {domain} {type_key} record")
                    return True
            
            # Add the new record
            self.records[domain][type_key].append(record)
            logger.debug(f"Added {domain} {type_key} record: {record_data}")
            
            # Save to file if a file path was provided
            if self.db_file:
                self.save_to_file(self.db_file)
            
            return True
    
    def remove_record(self, domain: str, record_type: Union[DNSType, str], 
                     record_data: Optional[str] = None) -> bool:
        """
        Remove a DNS record from the database
        
        Args:
            domain: Domain name
            record_type: Record type (DNSType or string)
            record_data: Record data to match (default: None, removes all records of the type)
            
        Returns:
            bool: True if the record was removed successfully, False otherwise
        """
        with self.lock:
            # Normalize the domain name
            domain = domain.lower()
            if domain.endswith('.'):
                domain = domain[:-1]
            
            # Convert string record type to DNSType
            if isinstance(record_type, str):
                try:
                    record_type = DNSType[record_type]
                except KeyError:
                    logger.error(f"Invalid record type: {record_type}")
                    return False
            
            # Check if the domain exists
            if domain not in self.records:
                logger.warning(f"Domain not found: {domain}")
                return False
            
            # Check if the record type exists
            type_key = record_type.name
            if type_key not in self.records[domain]:
                logger.warning(f"Record type not found: {domain} {type_key}")
                return False
            
            # If no record data is provided, remove all records of the type
            if record_data is None:
                del self.records[domain][type_key]
                logger.debug(f"Removed all {domain} {type_key} records")
                
                # Remove the domain if it has no more records
                if not self.records[domain]:
                    del self.records[domain]
                
                # Save to file if a file path was provided
                if self.db_file:
                    self.save_to_file(self.db_file)
                
                return True
            
            # Find and remove the matching record
            for i, record in enumerate(self.records[domain][type_key]):
                if record.rdata_text == record_data:
                    del self.records[domain][type_key][i]
                    logger.debug(f"Removed {domain} {type_key} record: {record_data}")
                    
                    # Remove the record type if it has no more records
                    if not self.records[domain][type_key]:
                        del self.records[domain][type_key]
                    
                    # Remove the domain if it has no more records
                    if not self.records[domain]:
                        del self.records[domain]
                    
                    # Save to file if a file path was provided
                    if self.db_file:
                        self.save_to_file(self.db_file)
                    
                    return True
            
            logger.warning(f"Record not found: {domain} {type_key} {record_data}")
            return False
    
    def lookup(self, domain: str, record_type: Union[DNSType, str] = DNSType.A, 
              record_class: Union[DNSClass, str] = DNSClass.IN) -> List[DNSResourceRecord]:
        """
        Look up DNS records in the database
        
        Args:
            domain: Domain name
            record_type: Record type (default: A)
            record_class: Record class (default: IN)
            
        Returns:
            list: List of matching DNSResourceRecord objects
        """
        with self.lock:
            # Normalize the domain name
            domain = domain.lower()
            if domain.endswith('.'):
                domain = domain[:-1]
            
            # Convert string record type to DNSType
            if isinstance(record_type, str):
                try:
                    record_type = DNSType[record_type]
                except KeyError:
                    logger.error(f"Invalid record type: {record_type}")
                    return []
            
            # Convert string record class to DNSClass
            if isinstance(record_class, str):
                try:
                    record_class = DNSClass[record_class]
                except KeyError:
                    logger.error(f"Invalid record class: {record_class}")
                    return []
            
            # Check if the domain exists
            if domain not in self.records:
                return []
            
            # Check if the record type exists
            type_key = record_type.name
            
            # Handle ANY query type
            if record_type == DNSType.ANY:
                # Return all records for the domain
                all_records = []
                for type_records in self.records[domain].values():
                    all_records.extend(type_records)
                return all_records
            
            # Return the matching records
            if type_key in self.records[domain]:
                # Filter by record class if needed
                if record_class == DNSClass.ANY:
                    return self.records[domain][type_key]
                else:
                    return [r for r in self.records[domain][type_key] if r.rclass == record_class]
            
            # Check for CNAME records
            if DNSType.CNAME.name in self.records[domain]:
                # Return the CNAME records
                cname_records = self.records[domain][DNSType.CNAME.name]
                
                # Filter by record class if needed
                if record_class != DNSClass.ANY:
                    cname_records = [r for r in cname_records if r.rclass == record_class]
                
                # If we have CNAME records, follow them
                if cname_records:
                    # Get the target domain
                    target_domain = cname_records[0].rdata_text
                    
                    # Look up records for the target domain
                    target_records = self.lookup(target_domain, record_type, record_class)
                    
                    # Return both the CNAME record and the target records
                    return cname_records + target_records
            
            # No matching records found
            return []
    
    def get_all_records(self) -> Dict[str, Dict[str, List[DNSResourceRecord]]]:
        """
        Get all records in the database
        
        Returns:
            dict: All records in the database
        """
        with self.lock:
            return self.records.copy()
    
    def clear(self) -> None:
        """Clear all records from the database"""
        with self.lock:
            self.records.clear()
            logger.debug("Cleared all records from the database")
            
            # Save to file if a file path was provided
            if self.db_file:
                self.save_to_file(self.db_file)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load records from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if the records were loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing records
            self.records.clear()
            
            # Process the records
            for domain, domain_records in data.items():
                for record_type, records in domain_records.items():
                    for record_data in records:
                        # Extract TTL and class if provided
                        ttl = record_data.get('ttl', 3600)
                        record_class = record_data.get('class', 'IN')
                        
                        # Add the record
                        self.add_record(domain, record_type, record_data['data'], ttl, record_class)
            
            logger.info(f"Loaded records from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading records from {file_path}: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save records to a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if the records were saved successfully, False otherwise
        """
        try:
            # Convert records to a serializable format
            data = {}
            
            for domain, domain_records in self.records.items():
                data[domain] = {}
                
                for record_type, records in domain_records.items():
                    data[domain][record_type] = []
                    
                    for record in records:
                        data[domain][record_type].append({
                            'data': record.rdata_text,
                            'ttl': record.ttl,
                            'class': record.rclass.name
                        })
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Write to the file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved records to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving records to {file_path}: {e}")
            return False
    
    def _create_record(self, domain: str, record_type: DNSType, record_data: str, 
                      ttl: int, record_class: DNSClass) -> Optional[DNSResourceRecord]:
        """
        Create a DNS resource record
        
        Args:
            domain: Domain name
            record_type: Record type
            record_data: Record data (string format)
            ttl: Time to live in seconds
            record_class: Record class
            
        Returns:
            Optional[DNSResourceRecord]: The created record, or None if invalid
        """
        try:
            record = DNSResourceRecord()
            record.name = domain
            record.rtype = record_type
            record.rclass = record_class
            record.ttl = ttl
            
            # Encode the record data based on the record type
            if record_type == DNSType.A:
                # A record (IPv4 address)
                try:
                    ip = ipaddress.IPv4Address(record_data)
                    record.rdata = ip.packed
                    record.rdata_text = str(ip)
                except ValueError:
                    logger.error(f"Invalid IPv4 address: {record_data}")
                    return None
                
            elif record_type == DNSType.AAAA:
                # AAAA record (IPv6 address)
                try:
                    ip = ipaddress.IPv6Address(record_data)
                    record.rdata = ip.packed
                    record.rdata_text = str(ip)
                except ValueError:
                    logger.error(f"Invalid IPv6 address: {record_data}")
                    return None
                
            elif record_type in (DNSType.NS, DNSType.CNAME, DNSType.PTR):
                # NS, CNAME, PTR records (domain name)
                from dns_message import encode_domain_name
                record.rdata = encode_domain_name(record_data)
                record.rdata_text = record_data
                
            elif record_type == DNSType.MX:
                # MX record (preference + domain name)
                try:
                    parts = record_data.split(' ', 1)
                    preference = int(parts[0])
                    exchange = parts[1]
                    
                    from dns_message import encode_domain_name
                    import struct
                    record.rdata = struct.pack('!H', preference) + encode_domain_name(exchange)
                    record.rdata_text = record_data
                except (ValueError, IndexError):
                    logger.error(f"Invalid MX record: {record_data}")
                    return None
                
            elif record_type == DNSType.TXT:
                # TXT record (text string)
                # Remove quotes if present
                if record_data.startswith('"') and record_data.endswith('"'):
                    record_data = record_data[1:-1]
                
                # Encode as length-prefixed string
                encoded = bytes([len(record_data)]) + record_data.encode('ascii')
                record.rdata = encoded
                record.rdata_text = f'"{record_data}"'
                
            elif record_type == DNSType.SOA:
                # SOA record (mname, rname, serial, refresh, retry, expire, minimum)
                try:
                    parts = record_data.split(' ')
                    if len(parts) != 7:
                        raise ValueError("SOA record must have 7 parts")
                    
                    mname = parts[0]
                    rname = parts[1]
                    serial = int(parts[2])
                    refresh = int(parts[3])
                    retry = int(parts[4])
                    expire = int(parts[5])
                    minimum = int(parts[6])
                    
                    from dns_message import encode_domain_name
                    import struct
                    record.rdata = (
                        encode_domain_name(mname) +
                        encode_domain_name(rname) +
                        struct.pack('!IIIII', serial, refresh, retry, expire, minimum)
                    )
                    record.rdata_text = record_data
                except (ValueError, IndexError) as e:
                    logger.error(f"Invalid SOA record: {record_data} - {e}")
                    return None
                
            elif record_type == DNSType.SRV:
                # SRV record (priority, weight, port, target)
                try:
                    parts = record_data.split(' ')
                    if len(parts) != 4:
                        raise ValueError("SRV record must have 4 parts")
                    
                    priority = int(parts[0])
                    weight = int(parts[1])
                    port = int(parts[2])
                    target = parts[3]
                    
                    from dns_message import encode_domain_name
                    import struct
                    record.rdata = struct.pack('!HHH', priority, weight, port) + encode_domain_name(target)
                    record.rdata_text = record_data
                except (ValueError, IndexError) as e:
                    logger.error(f"Invalid SRV record: {record_data} - {e}")
                    return None
                
            else:
                # Unsupported record type
                logger.error(f"Unsupported record type: {record_type}")
                return None
            
            return record
            
        except Exception as e:
            logger.error(f"Error creating record: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    from dns_message import DNSType, DNSClass
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create a record database
    db = DNSRecordDB()
    
    # Add some test records
    db.add_record("example.com", DNSType.A, "93.184.216.34")
    db.add_record("example.com", DNSType.AAAA, "2606:2800:220:1:248:1893:25c8:1946")
    db.add_record("example.com", DNSType.MX, "10 mail.example.com")
    db.add_record("mail.example.com", DNSType.A, "93.184.216.35")
    db.add_record("example.com", DNSType.TXT, "v=spf1 -all")
    db.add_record("example.com", DNSType.NS, "ns1.example.com")
    db.add_record("example.com", DNSType.NS, "ns2.example.com")
    db.add_record("ns1.example.com", DNSType.A, "93.184.216.36")
    db.add_record("ns2.example.com", DNSType.A, "93.184.216.37")
    
    # Look up records
    print("A records for example.com:")
    for record in db.lookup("example.com", DNSType.A):
        print(f"  {record}")
    
    print("\nMX records for example.com:")
    for record in db.lookup("example.com", DNSType.MX):
        print(f"  {record}")
    
    print("\nAll records for example.com:")
    for record in db.lookup("example.com", DNSType.ANY):
        print(f"  {record}")
    
    # Save to a file
    db.save_to_file("data/records.json")
    
    # Clear the database
    db.clear()
    
    # Load from the file
    db.load_from_file("data/records.json")
    
    print("\nAfter loading from file, A records for example.com:")
    for record in db.lookup("example.com", DNSType.A):
        print(f"  {record}") 