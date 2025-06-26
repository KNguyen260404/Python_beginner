#!/usr/bin/env python3
"""
DNS Message - DNS protocol message encoding and decoding

This module implements the DNS message format as defined in RFC 1035.
It provides functionality to encode and decode DNS messages for both
client and server operations.
"""

import struct
import random
from enum import IntEnum, auto
from typing import List, Dict, Tuple, Optional, Union, Any


class DNSType(IntEnum):
    """DNS Resource Record Types"""
    A = 1          # IPv4 address
    NS = 2         # Nameserver
    CNAME = 5      # Canonical name
    SOA = 6        # Start of Authority
    PTR = 12       # Pointer record
    MX = 15        # Mail exchange
    TXT = 16       # Text record
    AAAA = 28      # IPv6 address
    SRV = 33       # Service record
    ANY = 255      # Any record type


class DNSClass(IntEnum):
    """DNS Resource Record Classes"""
    IN = 1         # Internet
    CS = 2         # CSNET
    CH = 3         # CHAOS
    HS = 4         # Hesiod
    ANY = 255      # Any class


class DNSOpcode(IntEnum):
    """DNS Message Opcodes"""
    QUERY = 0      # Standard query
    IQUERY = 1     # Inverse query
    STATUS = 2     # Server status request
    NOTIFY = 4     # Zone change notification
    UPDATE = 5     # Dynamic update


class DNSResponseCode(IntEnum):
    """DNS Response Codes"""
    NOERROR = 0    # No error
    FORMERR = 1    # Format error
    SERVFAIL = 2   # Server failure
    NXDOMAIN = 3   # Non-existent domain
    NOTIMP = 4     # Not implemented
    REFUSED = 5    # Query refused
    YXDOMAIN = 6   # Name exists when it should not
    YXRRSET = 7    # RR set exists when it should not
    NXRRSET = 8    # RR set that should exist does not
    NOTAUTH = 9    # Server not authoritative
    NOTZONE = 10   # Name not contained in zone


class DNSHeader:
    """DNS Message Header"""
    
    def __init__(self):
        """Initialize a DNS header with default values"""
        self.id = random.randint(0, 65535)  # Random ID
        self.is_response = False            # QR flag (Query/Response)
        self.opcode = DNSOpcode.QUERY       # Operation code
        self.is_authoritative = False       # AA flag (Authoritative Answer)
        self.is_truncated = False           # TC flag (Truncated)
        self.recursion_desired = True       # RD flag (Recursion Desired)
        self.recursion_available = False    # RA flag (Recursion Available)
        self.z = 0                          # Reserved for future use
        self.response_code = DNSResponseCode.NOERROR  # Response code
        self.question_count = 0             # Number of questions
        self.answer_count = 0               # Number of answers
        self.authority_count = 0            # Number of authority records
        self.additional_count = 0           # Number of additional records
    
    def pack(self) -> bytes:
        """
        Pack the DNS header into bytes
        
        Returns:
            bytes: The packed DNS header
        """
        # Construct the flags field
        flags = 0
        if self.is_response:
            flags |= (1 << 15)  # QR bit
        flags |= (self.opcode << 11)  # Opcode
        if self.is_authoritative:
            flags |= (1 << 10)  # AA bit
        if self.is_truncated:
            flags |= (1 << 9)   # TC bit
        if self.recursion_desired:
            flags |= (1 << 8)   # RD bit
        if self.recursion_available:
            flags |= (1 << 7)   # RA bit
        flags |= (self.z << 4)  # Z bits
        flags |= self.response_code  # RCODE
        
        # Pack the header fields
        return struct.pack(
            "!HHHHHH",
            self.id,
            flags,
            self.question_count,
            self.answer_count,
            self.authority_count,
            self.additional_count
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> Tuple['DNSHeader', bytes]:
        """
        Unpack a DNS header from bytes
        
        Args:
            data: The bytes to unpack
            
        Returns:
            tuple: (DNSHeader, remaining_data)
        """
        if len(data) < 12:
            raise ValueError("DNS header data too short")
        
        # Unpack the header fields
        header_data = struct.unpack("!HHHHHH", data[:12])
        remaining_data = data[12:]
        
        # Create and populate the header object
        header = cls()
        header.id = header_data[0]
        
        # Parse flags
        flags = header_data[1]
        header.is_response = bool(flags & (1 << 15))
        header.opcode = (flags >> 11) & 0xF
        header.is_authoritative = bool(flags & (1 << 10))
        header.is_truncated = bool(flags & (1 << 9))
        header.recursion_desired = bool(flags & (1 << 8))
        header.recursion_available = bool(flags & (1 << 7))
        header.z = (flags >> 4) & 0x7
        header.response_code = flags & 0xF
        
        # Set counts
        header.question_count = header_data[2]
        header.answer_count = header_data[3]
        header.authority_count = header_data[4]
        header.additional_count = header_data[5]
        
        return header, remaining_data
    
    def __str__(self) -> str:
        """String representation of the DNS header"""
        return (
            f"ID: {self.id}, "
            f"{'Response' if self.is_response else 'Query'}, "
            f"Opcode: {self.opcode.name}, "
            f"Status: {self.response_code.name}, "
            f"Flags: "
            f"{'AA ' if self.is_authoritative else ''}"
            f"{'TC ' if self.is_truncated else ''}"
            f"{'RD ' if self.recursion_desired else ''}"
            f"{'RA ' if self.recursion_available else ''}, "
            f"Questions: {self.question_count}, "
            f"Answers: {self.answer_count}, "
            f"Authority: {self.authority_count}, "
            f"Additional: {self.additional_count}"
        )


class DNSQuestion:
    """DNS Question Section"""
    
    def __init__(self, name: str = "", qtype: DNSType = DNSType.A, qclass: DNSClass = DNSClass.IN):
        """
        Initialize a DNS question
        
        Args:
            name: The domain name to query
            qtype: The query type (default: A)
            qclass: The query class (default: IN)
        """
        self.name = name
        self.qtype = qtype
        self.qclass = qclass
    
    def pack(self) -> bytes:
        """
        Pack the DNS question into bytes
        
        Returns:
            bytes: The packed DNS question
        """
        # Pack the domain name
        name_bytes = encode_domain_name(self.name)
        
        # Pack the type and class
        type_class_bytes = struct.pack("!HH", self.qtype, self.qclass)
        
        return name_bytes + type_class_bytes
    
    @classmethod
    def unpack(cls, data: bytes) -> Tuple['DNSQuestion', bytes]:
        """
        Unpack a DNS question from bytes
        
        Args:
            data: The bytes to unpack
            
        Returns:
            tuple: (DNSQuestion, remaining_data)
        """
        # Decode the domain name
        name, remaining = decode_domain_name(data)
        
        # Ensure we have enough data for type and class
        if len(remaining) < 4:
            raise ValueError("DNS question data too short")
        
        # Unpack the type and class
        qtype, qclass = struct.unpack("!HH", remaining[:4])
        remaining = remaining[4:]
        
        # Create and return the question
        question = cls(name, DNSType(qtype), DNSClass(qclass))
        return question, remaining
    
    def __str__(self) -> str:
        """String representation of the DNS question"""
        return f"{self.name} {self.qtype.name} {self.qclass.name}"


class DNSResourceRecord:
    """DNS Resource Record (Answer, Authority, or Additional)"""
    
    def __init__(self, name: str = "", rtype: DNSType = DNSType.A, rclass: DNSClass = DNSClass.IN,
                 ttl: int = 300, rdata: bytes = b''):
        """
        Initialize a DNS resource record
        
        Args:
            name: The domain name
            rtype: The record type
            rclass: The record class
            ttl: Time to live in seconds
            rdata: The record data
        """
        self.name = name
        self.rtype = rtype
        self.rclass = rclass
        self.ttl = ttl
        self.rdata = rdata
        self.rdata_text = ""  # Human-readable version of rdata
    
    def pack(self) -> bytes:
        """
        Pack the DNS resource record into bytes
        
        Returns:
            bytes: The packed DNS resource record
        """
        # Pack the domain name
        name_bytes = encode_domain_name(self.name)
        
        # Pack the record metadata
        metadata_bytes = struct.pack("!HHIH", self.rtype, self.rclass, self.ttl, len(self.rdata))
        
        # Combine all parts
        return name_bytes + metadata_bytes + self.rdata
    
    @classmethod
    def unpack(cls, data: bytes) -> Tuple['DNSResourceRecord', bytes]:
        """
        Unpack a DNS resource record from bytes
        
        Args:
            data: The bytes to unpack
            
        Returns:
            tuple: (DNSResourceRecord, remaining_data)
        """
        # Decode the domain name
        name, remaining = decode_domain_name(data)
        
        # Ensure we have enough data for the record metadata
        if len(remaining) < 10:
            raise ValueError("DNS resource record data too short")
        
        # Unpack the record metadata
        rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", remaining[:10])
        remaining = remaining[10:]
        
        # Ensure we have enough data for the record data
        if len(remaining) < rdlength:
            raise ValueError("DNS resource record data incomplete")
        
        # Extract the record data
        rdata = remaining[:rdlength]
        remaining = remaining[rdlength:]
        
        # Create the resource record
        record = cls(name, DNSType(rtype), DNSClass(rclass), ttl, rdata)
        
        # Parse the record data into a human-readable format
        record.rdata_text = parse_rdata(record)
        
        return record, remaining
    
    def __str__(self) -> str:
        """String representation of the DNS resource record"""
        return (
            f"{self.name} {self.ttl} {self.rclass.name} {self.rtype.name} {self.rdata_text}"
        )


class DNSMessage:
    """Complete DNS Message"""
    
    def __init__(self):
        """Initialize a DNS message with default values"""
        self.header = DNSHeader()
        self.questions: List[DNSQuestion] = []
        self.answers: List[DNSResourceRecord] = []
        self.authorities: List[DNSResourceRecord] = []
        self.additionals: List[DNSResourceRecord] = []
    
    def add_question(self, question: DNSQuestion) -> None:
        """
        Add a question to the DNS message
        
        Args:
            question: The question to add
        """
        self.questions.append(question)
        self.header.question_count = len(self.questions)
    
    def add_answer(self, answer: DNSResourceRecord) -> None:
        """
        Add an answer to the DNS message
        
        Args:
            answer: The answer to add
        """
        self.answers.append(answer)
        self.header.answer_count = len(self.answers)
    
    def add_authority(self, authority: DNSResourceRecord) -> None:
        """
        Add an authority record to the DNS message
        
        Args:
            authority: The authority record to add
        """
        self.authorities.append(authority)
        self.header.authority_count = len(self.authorities)
    
    def add_additional(self, additional: DNSResourceRecord) -> None:
        """
        Add an additional record to the DNS message
        
        Args:
            additional: The additional record to add
        """
        self.additionals.append(additional)
        self.header.additional_count = len(self.additionals)
    
    def pack(self) -> bytes:
        """
        Pack the DNS message into bytes
        
        Returns:
            bytes: The packed DNS message
        """
        # Pack the header
        result = self.header.pack()
        
        # Pack the questions
        for question in self.questions:
            result += question.pack()
        
        # Pack the answers
        for answer in self.answers:
            result += answer.pack()
        
        # Pack the authorities
        for authority in self.authorities:
            result += authority.pack()
        
        # Pack the additionals
        for additional in self.additionals:
            result += additional.pack()
        
        return result
    
    @classmethod
    def unpack(cls, data: bytes) -> 'DNSMessage':
        """
        Unpack a DNS message from bytes
        
        Args:
            data: The bytes to unpack
            
        Returns:
            DNSMessage: The unpacked DNS message
        """
        message = cls()
        
        # Unpack the header
        header, remaining = DNSHeader.unpack(data)
        message.header = header
        
        # Unpack the questions
        for _ in range(header.question_count):
            question, remaining = DNSQuestion.unpack(remaining)
            message.questions.append(question)
        
        # Unpack the answers
        for _ in range(header.answer_count):
            answer, remaining = DNSResourceRecord.unpack(remaining)
            message.answers.append(answer)
        
        # Unpack the authorities
        for _ in range(header.authority_count):
            authority, remaining = DNSResourceRecord.unpack(remaining)
            message.authorities.append(authority)
        
        # Unpack the additionals
        for _ in range(header.additional_count):
            additional, remaining = DNSResourceRecord.unpack(remaining)
            message.additionals.append(additional)
        
        return message
    
    def create_query(self, name: str, qtype: DNSType = DNSType.A, qclass: DNSClass = DNSClass.IN) -> None:
        """
        Create a DNS query message
        
        Args:
            name: The domain name to query
            qtype: The query type
            qclass: The query class
        """
        self.header = DNSHeader()
        self.header.id = random.randint(0, 65535)
        self.header.is_response = False
        self.header.opcode = DNSOpcode.QUERY
        self.header.recursion_desired = True
        
        self.questions = [DNSQuestion(name, qtype, qclass)]
        self.header.question_count = 1
        
        self.answers = []
        self.authorities = []
        self.additionals = []
        self.header.answer_count = 0
        self.header.authority_count = 0
        self.header.additional_count = 0
    
    def create_response(self, query: 'DNSMessage') -> None:
        """
        Create a DNS response message based on a query
        
        Args:
            query: The query message to respond to
        """
        self.header = DNSHeader()
        self.header.id = query.header.id
        self.header.is_response = True
        self.header.opcode = query.header.opcode
        self.header.recursion_desired = query.header.recursion_desired
        self.header.recursion_available = True
        
        self.questions = query.questions
        self.header.question_count = len(self.questions)
        
        self.answers = []
        self.authorities = []
        self.additionals = []
        self.header.answer_count = 0
        self.header.authority_count = 0
        self.header.additional_count = 0
    
    def __str__(self) -> str:
        """String representation of the DNS message"""
        result = [f"DNS Message: {self.header}"]
        
        if self.questions:
            result.append("Questions:")
            for i, q in enumerate(self.questions, 1):
                result.append(f"  {i}. {q}")
        
        if self.answers:
            result.append("Answers:")
            for i, a in enumerate(self.answers, 1):
                result.append(f"  {i}. {a}")
        
        if self.authorities:
            result.append("Authority:")
            for i, a in enumerate(self.authorities, 1):
                result.append(f"  {i}. {a}")
        
        if self.additionals:
            result.append("Additional:")
            for i, a in enumerate(self.additionals, 1):
                result.append(f"  {i}. {a}")
        
        return "\n".join(result)


def encode_domain_name(domain: str) -> bytes:
    """
    Encode a domain name in DNS format
    
    Args:
        domain: The domain name to encode
        
    Returns:
        bytes: The encoded domain name
    """
    if not domain or domain == '.':
        return b'\x00'
    
    result = b''
    for label in domain.split('.'):
        if label:  # Skip empty labels
            length = len(label)
            result += bytes([length]) + label.encode('ascii')
    
    # Add the terminating zero length label
    result += b'\x00'
    return result


def decode_domain_name(data: bytes, start_pos: int = 0) -> Tuple[str, bytes]:
    """
    Decode a domain name from DNS format
    
    Args:
        data: The data containing the encoded domain name
        start_pos: The starting position in the data
        
    Returns:
        tuple: (domain_name, remaining_data)
    """
    labels = []
    pos = start_pos
    
    while True:
        if pos >= len(data):
            raise ValueError("Incomplete domain name")
        
        length = data[pos]
        pos += 1
        
        # Check for message compression (RFC 1035 section 4.1.4)
        if length & 0xC0 == 0xC0:
            if pos >= len(data):
                raise ValueError("Incomplete compressed domain name")
            
            # Get the offset from the first 14 bits of the 2-byte pointer
            offset = ((length & 0x3F) << 8) | data[pos]
            pos += 1
            
            # Recursively decode the name at the offset
            pointed_name, _ = decode_domain_name(data, offset)
            labels.append(pointed_name)
            break
        
        # End of domain name
        if length == 0:
            break
        
        # Regular label
        if pos + length > len(data):
            raise ValueError("Incomplete domain name label")
        
        label = data[pos:pos + length].decode('ascii')
        labels.append(label)
        pos += length
    
    # Join all labels with dots
    domain = '.'.join(labels)
    
    # Return the domain name and the remaining data
    return domain, data[pos:]


def parse_rdata(record: DNSResourceRecord) -> str:
    """
    Parse the binary RDATA field into a human-readable format
    
    Args:
        record: The DNS resource record
        
    Returns:
        str: Human-readable representation of the record data
    """
    rtype = record.rtype
    rdata = record.rdata
    
    try:
        # A record (IPv4 address)
        if rtype == DNSType.A and len(rdata) == 4:
            return '.'.join(str(b) for b in rdata)
        
        # AAAA record (IPv6 address)
        elif rtype == DNSType.AAAA and len(rdata) == 16:
            # Format IPv6 address
            hex_groups = [f"{rdata[i*2]:02x}{rdata[i*2+1]:02x}" for i in range(8)]
            return ':'.join(hex_groups)
        
        # NS, CNAME, PTR records (domain name)
        elif rtype in (DNSType.NS, DNSType.CNAME, DNSType.PTR):
            name, _ = decode_domain_name(rdata, 0)
            return name
        
        # MX record (preference + domain name)
        elif rtype == DNSType.MX and len(rdata) >= 3:
            preference = struct.unpack("!H", rdata[:2])[0]
            name, _ = decode_domain_name(rdata, 2)
            return f"{preference} {name}"
        
        # TXT record (text string)
        elif rtype == DNSType.TXT:
            # TXT records can have multiple strings
            result = []
            pos = 0
            while pos < len(rdata):
                length = rdata[pos]
                pos += 1
                if pos + length <= len(rdata):
                    txt = rdata[pos:pos+length].decode('ascii', errors='replace')
                    result.append(f'"{txt}"')
                    pos += length
            return ' '.join(result)
        
        # SOA record
        elif rtype == DNSType.SOA:
            pos = 0
            mname, rdata_remaining = decode_domain_name(rdata, pos)
            rname, rdata_remaining = decode_domain_name(rdata_remaining, 0)
            
            if len(rdata_remaining) >= 20:
                serial, refresh, retry, expire, minimum = struct.unpack("!IIIII", rdata_remaining[:20])
                return f"{mname} {rname} {serial} {refresh} {retry} {expire} {minimum}"
        
        # SRV record
        elif rtype == DNSType.SRV and len(rdata) >= 7:
            priority, weight, port = struct.unpack("!HHH", rdata[:6])
            target, _ = decode_domain_name(rdata, 6)
            return f"{priority} {weight} {port} {target}"
        
        # Unknown or unimplemented record type
        return ' '.join(f"{b:02x}" for b in rdata)
    
    except Exception as e:
        # If parsing fails, return a hex representation
        return f"<Error parsing RDATA: {e}> " + ' '.join(f"{b:02x}" for b in rdata)


if __name__ == "__main__":
    # Example usage
    print("DNS Message Module - Example Usage")
    
    # Create a DNS query
    query = DNSMessage()
    query.create_query("example.com", DNSType.A)
    
    # Pack the query
    query_bytes = query.pack()
    print(f"Query bytes: {query_bytes.hex()}")
    
    # Unpack the query
    unpacked_query = DNSMessage.unpack(query_bytes)
    print("\nUnpacked Query:")
    print(unpacked_query)
    
    # Create a DNS response
    response = DNSMessage()
    response.create_response(query)
    
    # Add an answer
    answer = DNSResourceRecord()
    answer.name = "example.com"
    answer.rtype = DNSType.A
    answer.rclass = DNSClass.IN
    answer.ttl = 3600
    answer.rdata = bytes([93, 184, 216, 34])  # example.com IPv4 address
    answer.rdata_text = "93.184.216.34"
    response.add_answer(answer)
    
    # Pack the response
    response_bytes = response.pack()
    print(f"\nResponse bytes: {response_bytes.hex()}")
    
    # Unpack the response
    unpacked_response = DNSMessage.unpack(response_bytes)
    print("\nUnpacked Response:")
    print(unpacked_response) 