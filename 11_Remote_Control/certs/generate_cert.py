#!/usr/bin/env python3
"""
Certificate Generator

This script generates self-signed SSL certificates for the Remote Control application.
"""

import argparse
import datetime
import os
import socket
from typing import Tuple

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography module not installed.")
    print("Please install it using: pip install cryptography")
    exit(1)

def generate_key_pair(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """
    Generate an RSA key pair.
    
    Args:
        key_size: Size of the key in bits
        
    Returns:
        RSA private key
    """
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

def generate_self_signed_cert(
    private_key: rsa.RSAPrivateKey,
    common_name: str,
    country: str = "US",
    state: str = "State",
    locality: str = "City",
    organization: str = "Organization",
    organizational_unit: str = "IT",
    email: str = "admin@example.com",
    validity_days: int = 365
) -> x509.Certificate:
    """
    Generate a self-signed certificate.
    
    Args:
        private_key: RSA private key
        common_name: Common name for the certificate
        country: Country code
        state: State or province
        locality: City or locality
        organization: Organization name
        organizational_unit: Organizational unit
        email: Email address
        validity_days: Validity period in days
        
    Returns:
        Self-signed certificate
    """
    # Get public key
    public_key = private_key.public_key()
    
    # Create a builder for the certificate
    builder = x509.CertificateBuilder()
    
    # Set subject and issuer (same for self-signed)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, organizational_unit),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
    ])
    
    # Set certificate fields
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer)
    builder = builder.not_valid_before(datetime.datetime.utcnow())
    builder = builder.not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    )
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    
    # Add extensions
    builder = builder.add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
            x509.DNSName(socket.gethostname()),
            x509.DNSName("localhost"),
            x509.IPAddress(socket.inet_aton("127.0.0.1"))
        ]),
        critical=False
    )
    
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True
    )
    
    # Sign the certificate with the private key
    certificate = builder.sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )
    
    return certificate

def save_key_and_cert(
    private_key: rsa.RSAPrivateKey,
    certificate: x509.Certificate,
    key_path: str,
    cert_path: str,
    password: str = None
) -> None:
    """
    Save private key and certificate to files.
    
    Args:
        private_key: RSA private key
        certificate: X.509 certificate
        key_path: Path to save the private key
        cert_path: Path to save the certificate
        password: Optional password to encrypt the private key
    """
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(key_path)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(cert_path)), exist_ok=True)
    
    # Serialize private key
    if password:
        encryption = serialization.BestAvailableEncryption(password.encode())
    else:
        encryption = serialization.NoEncryption()
        
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )
    
    # Serialize certificate
    cert_bytes = certificate.public_bytes(serialization.Encoding.PEM)
    
    # Write to files
    with open(key_path, "wb") as f:
        f.write(private_key_bytes)
        
    with open(cert_path, "wb") as f:
        f.write(cert_bytes)
        
    # Set permissions on private key (Unix-like systems only)
    if os.name != "nt":
        os.chmod(key_path, 0o600)
        
    print(f"Private key saved to: {key_path}")
    print(f"Certificate saved to: {cert_path}")

def generate_cert_and_key(
    common_name: str,
    key_path: str,
    cert_path: str,
    key_size: int = 2048,
    validity_days: int = 365,
    password: str = None
) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
    """
    Generate and save a self-signed certificate and private key.
    
    Args:
        common_name: Common name for the certificate
        key_path: Path to save the private key
        cert_path: Path to save the certificate
        key_size: Size of the key in bits
        validity_days: Validity period in days
        password: Optional password to encrypt the private key
        
    Returns:
        Tuple of (private_key, certificate)
    """
    print(f"Generating {key_size}-bit RSA key pair...")
    private_key = generate_key_pair(key_size)
    
    print(f"Generating self-signed certificate for '{common_name}'...")
    certificate = generate_self_signed_cert(
        private_key,
        common_name,
        validity_days=validity_days
    )
    
    print("Saving key and certificate...")
    save_key_and_cert(private_key, certificate, key_path, cert_path, password)
    
    return private_key, certificate

def main():
    """Main function to parse arguments and generate certificates."""
    parser = argparse.ArgumentParser(description="Generate SSL certificates")
    parser.add_argument("--common-name", default=socket.gethostname(),
                       help="Common name for the certificate")
    parser.add_argument("--key", default="../certs/server.key",
                       help="Path to save the private key")
    parser.add_argument("--cert", default="../certs/server.crt",
                       help="Path to save the certificate")
    parser.add_argument("--key-size", type=int, default=2048,
                       help="Size of the key in bits")
    parser.add_argument("--validity", type=int, default=365,
                       help="Validity period in days")
    parser.add_argument("--password", help="Password to encrypt the private key")
    
    args = parser.parse_args()
    
    # Make paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(script_dir, args.key)
    cert_path = os.path.join(script_dir, args.cert)
    
    # Generate certificate and key
    generate_cert_and_key(
        args.common_name,
        key_path,
        cert_path,
        args.key_size,
        args.validity,
        args.password
    )
    
    print("Certificate generation complete!")

if __name__ == "__main__":
    main() 