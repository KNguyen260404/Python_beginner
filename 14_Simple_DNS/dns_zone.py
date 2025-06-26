#!/usr/bin/env python3
"""
DNS Zone - Manages DNS zones and zone files

This module provides functionality for managing DNS zones and
loading zone files in standard zone file format.
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Set

from dns_message import DNSType, DNSClass
from dns_records import DNSRecordDB

# Configure logging
logger = logging.getLogger(__name__)


class DNSZone:
    """DNS zone representation"""
    
    def __init__(self, domain: str):
        """
        Initialize a DNS zone
        
        Args:
            domain: Zone domain name
        """
        self.domain = domain.lower()
        if self.domain.endswith('.'):
            self.domain = self.domain[:-1]
        
        self.records: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.soa_record: Optional[Dict[str, Any]] = None
        self.default_ttl = 3600
    
    def add_record(self, name: str, record_type: str, record_data: str, ttl: Optional[int] = None) -> bool:
        """
        Add a record to the zone
        
        Args:
            name: Record name (relative to zone domain)
            record_type: Record type (A, AAAA, MX, etc.)
            record_data: Record data
            ttl: Time to live in seconds (default: None, use zone default)
            
        Returns:
            bool: True if the record was added successfully, False otherwise
        """
        try:
            # Normalize the name
            name = name.lower()
            if name.endswith('.'):
                name = name[:-1]
            
            # If the name is @ or empty, use the zone domain
            if name == '@' or not name:
                name = self.domain
            # Otherwise, append the zone domain if it's not already a FQDN
            elif not name.endswith(self.domain) and '.' not in name:
                name = f"{name}.{self.domain}"
            
            # Normalize the record type
            record_type = record_type.upper()
            
            # Use the zone default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Create the record
            record = {
                'data': record_data,
                'ttl': ttl
            }
            
            # Add the record to the zone
            if name not in self.records:
                self.records[name] = {}
            
            if record_type not in self.records[name]:
                self.records[name][record_type] = []
            
            # Check if the record already exists
            for existing_record in self.records[name][record_type]:
                if existing_record['data'] == record_data:
                    # Update the TTL if the record already exists
                    existing_record['ttl'] = ttl
                    return True
            
            # Add the new record
            self.records[name][record_type].append(record)
            
            # If this is an SOA record for the zone domain, store it separately
            if record_type == 'SOA' and name == self.domain:
                self.soa_record = record
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding record to zone {self.domain}: {e}")
            return False
    
    def remove_record(self, name: str, record_type: str, record_data: Optional[str] = None) -> bool:
        """
        Remove a record from the zone
        
        Args:
            name: Record name (relative to zone domain)
            record_type: Record type (A, AAAA, MX, etc.)
            record_data: Record data to match (default: None, removes all records of the type)
            
        Returns:
            bool: True if the record was removed successfully, False otherwise
        """
        try:
            # Normalize the name
            name = name.lower()
            if name.endswith('.'):
                name = name[:-1]
            
            # If the name is @ or empty, use the zone domain
            if name == '@' or not name:
                name = self.domain
            # Otherwise, append the zone domain if it's not already a FQDN
            elif not name.endswith(self.domain) and '.' not in name:
                name = f"{name}.{self.domain}"
            
            # Normalize the record type
            record_type = record_type.upper()
            
            # Check if the name exists
            if name not in self.records:
                logger.warning(f"Name not found in zone {self.domain}: {name}")
                return False
            
            # Check if the record type exists
            if record_type not in self.records[name]:
                logger.warning(f"Record type not found in zone {self.domain}: {name} {record_type}")
                return False
            
            # If no record data is provided, remove all records of the type
            if record_data is None:
                del self.records[name][record_type]
                
                # Remove the name if it has no more records
                if not self.records[name]:
                    del self.records[name]
                
                # If this was the SOA record for the zone domain, clear it
                if record_type == 'SOA' and name == self.domain:
                    self.soa_record = None
                
                return True
            
            # Find and remove the matching record
            for i, record in enumerate(self.records[name][record_type]):
                if record['data'] == record_data:
                    del self.records[name][record_type][i]
                    
                    # Remove the record type if it has no more records
                    if not self.records[name][record_type]:
                        del self.records[name][record_type]
                    
                    # Remove the name if it has no more records
                    if not self.records[name]:
                        del self.records[name]
                    
                    # If this was the SOA record for the zone domain, clear it
                    if record_type == 'SOA' and name == self.domain:
                        self.soa_record = None
                    
                    return True
            
            logger.warning(f"Record not found in zone {self.domain}: {name} {record_type} {record_data}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing record from zone {self.domain}: {e}")
            return False
    
    def get_records(self, name: str, record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get records from the zone
        
        Args:
            name: Record name (relative to zone domain)
            record_type: Record type (default: None, returns all types)
            
        Returns:
            list: List of matching records
        """
        # Normalize the name
        name = name.lower()
        if name.endswith('.'):
            name = name[:-1]
        
        # If the name is @ or empty, use the zone domain
        if name == '@' or not name:
            name = self.domain
        # Otherwise, append the zone domain if it's not already a FQDN
        elif not name.endswith(self.domain) and '.' not in name:
            name = f"{name}.{self.domain}"
        
        # Check if the name exists
        if name not in self.records:
            return []
        
        # If no record type is specified, return all records for the name
        if record_type is None:
            all_records = []
            for type_records in self.records[name].values():
                all_records.extend(type_records)
            return all_records
        
        # Normalize the record type
        record_type = record_type.upper()
        
        # Return the matching records
        if record_type in self.records[name]:
            return self.records[name][record_type]
        
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the zone to a dictionary
        
        Returns:
            dict: Zone as a dictionary
        """
        return {
            'domain': self.domain,
            'records': self.records,
            'default_ttl': self.default_ttl
        }
    
    def to_zone_file(self) -> str:
        """
        Convert the zone to a zone file format
        
        Returns:
            str: Zone file content
        """
        lines = []
        
        # Add the SOA record
        if self.soa_record:
            lines.append(f"$ORIGIN {self.domain}.")
            lines.append(f"$TTL {self.default_ttl}")
            lines.append(f"@ IN SOA {self.soa_record['data']}")
            lines.append("")
        
        # Add the other records
        for name, type_records in self.records.items():
            for record_type, records in type_records.items():
                # Skip the SOA record, we already added it
                if name == self.domain and record_type == 'SOA':
                    continue
                
                for record in records:
                    # Convert the name to a relative name if possible
                    if name == self.domain:
                        relative_name = '@'
                    elif name.endswith(f".{self.domain}"):
                        relative_name = name[:-len(f".{self.domain}")]
                    else:
                        relative_name = name
                    
                    # Add the record
                    lines.append(f"{relative_name} {record['ttl']} IN {record_type} {record['data']}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_zone_file(cls, file_path: str) -> Optional['DNSZone']:
        """
        Load a zone from a zone file
        
        Args:
            file_path: Path to the zone file
            
        Returns:
            Optional[DNSZone]: The loaded zone, or None if loading failed
        """
        try:
            # Extract the domain name from the file name
            domain = os.path.basename(file_path).split('.')[0]
            
            # Create a new zone
            zone = cls(domain)
            
            # Read the zone file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the zone file
            origin = domain
            current_ttl = 3600
            
            # Process each line
            for line in content.splitlines():
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                
                # Handle directives
                if line.startswith('$'):
                    parts = line.split(None, 1)
                    directive = parts[0].upper()
                    
                    if directive == '$ORIGIN' and len(parts) > 1:
                        origin = parts[1].rstrip('.')
                    elif directive == '$TTL' and len(parts) > 1:
                        try:
                            current_ttl = int(parts[1])
                            zone.default_ttl = current_ttl
                        except ValueError:
                            logger.warning(f"Invalid TTL in zone file {file_path}: {parts[1]}")
                    
                    continue
                
                # Parse the record
                try:
                    # Split the line into parts
                    parts = line.split()
                    if len(parts) < 4:
                        logger.warning(f"Invalid record in zone file {file_path}: {line}")
                        continue
                    
                    # Extract the record fields
                    name = parts[0]
                    ttl = None
                    record_class = None
                    record_type = None
                    record_data = []
                    
                    # Parse the record fields
                    i = 1
                    while i < len(parts):
                        # Check if this is a TTL
                        if ttl is None and parts[i].isdigit():
                            ttl = int(parts[i])
                            i += 1
                            continue
                        
                        # Check if this is a record class
                        if record_class is None and parts[i].upper() in ('IN', 'CS', 'CH', 'HS'):
                            record_class = parts[i].upper()
                            i += 1
                            continue
                        
                        # Check if this is a record type
                        if record_type is None:
                            record_type = parts[i].upper()
                            i += 1
                            continue
                        
                        # The rest is record data
                        record_data = parts[i:]
                        break
                    
                    # Skip if we don't have a record type
                    if not record_type:
                        logger.warning(f"Missing record type in zone file {file_path}: {line}")
                        continue
                    
                    # Use default TTL if not specified
                    if ttl is None:
                        ttl = current_ttl
                    
                    # Convert the name to a FQDN if it's not already
                    if name == '@':
                        name = origin
                    elif not name.endswith('.'):
                        name = f"{name}.{origin}"
                    else:
                        name = name.rstrip('.')
                    
                    # Add the record to the zone
                    zone.add_record(name, record_type, ' '.join(record_data), ttl)
                    
                except Exception as e:
                    logger.warning(f"Error parsing record in zone file {file_path}: {line} - {e}")
                    continue
            
            return zone
            
        except Exception as e:
            logger.error(f"Error loading zone from file {file_path}: {e}")
            return None


class ZoneManager:
    """Manager for DNS zones"""
    
    def __init__(self, zone_dir: str, record_db: DNSRecordDB):
        """
        Initialize the zone manager
        
        Args:
            zone_dir: Directory containing zone files
            record_db: DNS record database
        """
        self.zone_dir = zone_dir
        self.record_db = record_db
        self.zones: Dict[str, DNSZone] = {}
        
        # Create the zone directory if it doesn't exist
        os.makedirs(zone_dir, exist_ok=True)
    
    def load_zones(self) -> bool:
        """
        Load all zones from the zone directory
        
        Returns:
            bool: True if all zones were loaded successfully, False otherwise
        """
        try:
            # Clear existing zones
            self.zones.clear()
            
            # Find all zone files
            zone_files = []
            for file in os.listdir(self.zone_dir):
                if file.endswith('.zone'):
                    zone_files.append(os.path.join(self.zone_dir, file))
            
            # Load each zone
            for file_path in zone_files:
                zone = DNSZone.from_zone_file(file_path)
                if zone:
                    self.zones[zone.domain] = zone
                    logger.info(f"Loaded zone {zone.domain} from {file_path}")
            
            # Update the record database
            self._update_record_db()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading zones: {e}")
            return False
    
    def save_zones(self) -> bool:
        """
        Save all zones to the zone directory
        
        Returns:
            bool: True if all zones were saved successfully, False otherwise
        """
        try:
            # Save each zone
            for domain, zone in self.zones.items():
                file_path = os.path.join(self.zone_dir, f"{domain}.zone")
                
                # Create the zone file
                with open(file_path, 'w') as f:
                    f.write(zone.to_zone_file())
                
                logger.info(f"Saved zone {domain} to {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving zones: {e}")
            return False
    
    def add_zone(self, domain: str, soa_data: Optional[str] = None) -> bool:
        """
        Add a new zone
        
        Args:
            domain: Zone domain name
            soa_data: SOA record data (default: None, creates a default SOA record)
            
        Returns:
            bool: True if the zone was added successfully, False otherwise
        """
        try:
            # Normalize the domain name
            domain = domain.lower()
            if domain.endswith('.'):
                domain = domain[:-1]
            
            # Check if the zone already exists
            if domain in self.zones:
                logger.warning(f"Zone already exists: {domain}")
                return False
            
            # Create a new zone
            zone = DNSZone(domain)
            
            # Add a default SOA record if not provided
            if soa_data is None:
                soa_data = f"ns1.{domain}. admin.{domain}. 1 3600 1800 604800 86400"
            
            # Add the SOA record
            zone.add_record(domain, 'SOA', soa_data)
            
            # Add default NS records
            zone.add_record(domain, 'NS', f"ns1.{domain}.")
            zone.add_record(domain, 'NS', f"ns2.{domain}.")
            
            # Add default A records for the nameservers
            zone.add_record(f"ns1.{domain}", 'A', "127.0.0.1")
            zone.add_record(f"ns2.{domain}", 'A', "127.0.0.2")
            
            # Add the zone to the manager
            self.zones[domain] = zone
            
            # Save the zone
            file_path = os.path.join(self.zone_dir, f"{domain}.zone")
            with open(file_path, 'w') as f:
                f.write(zone.to_zone_file())
            
            # Update the record database
            self._update_record_db()
            
            logger.info(f"Added zone {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding zone {domain}: {e}")
            return False
    
    def remove_zone(self, domain: str) -> bool:
        """
        Remove a zone
        
        Args:
            domain: Zone domain name
            
        Returns:
            bool: True if the zone was removed successfully, False otherwise
        """
        try:
            # Normalize the domain name
            domain = domain.lower()
            if domain.endswith('.'):
                domain = domain[:-1]
            
            # Check if the zone exists
            if domain not in self.zones:
                logger.warning(f"Zone not found: {domain}")
                return False
            
            # Remove the zone
            del self.zones[domain]
            
            # Remove the zone file
            file_path = os.path.join(self.zone_dir, f"{domain}.zone")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update the record database
            self._update_record_db()
            
            logger.info(f"Removed zone {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing zone {domain}: {e}")
            return False
    
    def get_zone(self, domain: str) -> Optional[DNSZone]:
        """
        Get a zone
        
        Args:
            domain: Zone domain name
            
        Returns:
            Optional[DNSZone]: The zone, or None if not found
        """
        # Normalize the domain name
        domain = domain.lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        
        # Return the zone if it exists
        return self.zones.get(domain)
    
    def add_record(self, domain: str, name: str, record_type: str, record_data: str, ttl: Optional[int] = None) -> bool:
        """
        Add a record to a zone
        
        Args:
            domain: Zone domain name
            name: Record name (relative to zone domain)
            record_type: Record type (A, AAAA, MX, etc.)
            record_data: Record data
            ttl: Time to live in seconds (default: None, use zone default)
            
        Returns:
            bool: True if the record was added successfully, False otherwise
        """
        # Normalize the domain name
        domain = domain.lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        
        # Check if the zone exists
        zone = self.get_zone(domain)
        if not zone:
            logger.warning(f"Zone not found: {domain}")
            return False
        
        # Add the record to the zone
        result = zone.add_record(name, record_type, record_data, ttl)
        
        # Save the zone
        if result:
            file_path = os.path.join(self.zone_dir, f"{domain}.zone")
            with open(file_path, 'w') as f:
                f.write(zone.to_zone_file())
            
            # Update the record database
            self._update_record_db()
        
        return result
    
    def remove_record(self, domain: str, name: str, record_type: str, record_data: Optional[str] = None) -> bool:
        """
        Remove a record from a zone
        
        Args:
            domain: Zone domain name
            name: Record name (relative to zone domain)
            record_type: Record type (A, AAAA, MX, etc.)
            record_data: Record data to match (default: None, removes all records of the type)
            
        Returns:
            bool: True if the record was removed successfully, False otherwise
        """
        # Normalize the domain name
        domain = domain.lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        
        # Check if the zone exists
        zone = self.get_zone(domain)
        if not zone:
            logger.warning(f"Zone not found: {domain}")
            return False
        
        # Remove the record from the zone
        result = zone.remove_record(name, record_type, record_data)
        
        # Save the zone
        if result:
            file_path = os.path.join(self.zone_dir, f"{domain}.zone")
            with open(file_path, 'w') as f:
                f.write(zone.to_zone_file())
            
            # Update the record database
            self._update_record_db()
        
        return result
    
    def _update_record_db(self) -> None:
        """Update the record database with all zone records"""
        # Clear the record database
        self.record_db.clear()
        
        # Add all zone records to the database
        for domain, zone in self.zones.items():
            for name, type_records in zone.records.items():
                for record_type, records in type_records.items():
                    for record in records:
                        self.record_db.add_record(name, record_type, record['data'], record['ttl'])


if __name__ == "__main__":
    # Example usage
    from dns_records import DNSRecordDB
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create a record database
    record_db = DNSRecordDB()
    
    # Create a zone manager
    zone_manager = ZoneManager("data/zones", record_db)
    
    # Add a zone
    zone_manager.add_zone("example.com")
    
    # Add some records
    zone_manager.add_record("example.com", "www", "A", "93.184.216.34")
    zone_manager.add_record("example.com", "mail", "A", "93.184.216.35")
    zone_manager.add_record("example.com", "@", "MX", "10 mail.example.com.")
    
    # Save the zones
    zone_manager.save_zones()
    
    # Load the zones
    zone_manager.load_zones()
    
    # Get a zone
    zone = zone_manager.get_zone("example.com")
    if zone:
        print(zone.to_zone_file()) 