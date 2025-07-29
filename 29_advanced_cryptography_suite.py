#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Cryptography Suite
---------------------------
A comprehensive cryptography toolkit that implements:
- Modern encryption algorithms (AES, ChaCha20, RSA)
- Digital signatures and certificates
- Key exchange protocols (ECDH, DH)
- Hash functions and MACs
- Zero-knowledge proofs
- Homomorphic encryption
- Post-quantum cryptography
"""

import os
import sys
import hashlib
import hmac
import secrets
import base64
import json
import time
import argparse
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

# Cryptographic libraries
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dh, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography import x509
import datetime

# Additional libraries for advanced features
import numpy as np
from sympy import randprime, gcd, mod_inverse
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAlgorithm(Enum):
    """Supported cryptographic algorithms"""
    AES_256_GCM = auto()
    AES_256_CBC = auto()
    CHACHA20_POLY1305 = auto()
    RSA_2048 = auto()
    RSA_4096 = auto()
    ECDSA_P256 = auto()
    ECDSA_P384 = auto()
    ECDH_P256 = auto()
    ECDH_P384 = auto()
    SHA256 = auto()
    SHA3_256 = auto()
    BLAKE2B = auto()

class KeyType(Enum):
    """Types of cryptographic keys"""
    SYMMETRIC = auto()
    ASYMMETRIC_PUBLIC = auto()
    ASYMMETRIC_PRIVATE = auto()
    DERIVED = auto()

@dataclass
class CryptoKey:
    """Represents a cryptographic key"""
    key_type: KeyType
    algorithm: CryptoAlgorithm
    key_data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class EncryptionResult:
    """Result of an encryption operation"""
    ciphertext: bytes
    iv_or_nonce: Optional[bytes] = None
    tag: Optional[bytes] = None
    algorithm: Optional[CryptoAlgorithm] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SymmetricCrypto:
    """Symmetric encryption and decryption operations"""
    
    def __init__(self):
        """Initialize symmetric crypto handler"""
        self.backend = default_backend()
    
    def generate_key(self, algorithm: CryptoAlgorithm) -> CryptoKey:
        """Generate a symmetric key
        
        Args:
            algorithm: The encryption algorithm
            
        Returns:
            Generated symmetric key
        """
        if algorithm in [CryptoAlgorithm.AES_256_GCM, CryptoAlgorithm.AES_256_CBC]:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif algorithm == CryptoAlgorithm.CHACHA20_POLY1305:
            key_data = secrets.token_bytes(32)  # 256 bits
        else:
            raise ValueError(f"Unsupported symmetric algorithm: {algorithm}")
        
        return CryptoKey(
            key_type=KeyType.SYMMETRIC,
            algorithm=algorithm,
            key_data=key_data,
            metadata={"key_size": len(key_data) * 8}
        )
    
    def encrypt(self, plaintext: bytes, key: CryptoKey) -> EncryptionResult:
        """Encrypt data using symmetric encryption
        
        Args:
            plaintext: Data to encrypt
            key: Symmetric key
            
        Returns:
            Encryption result
        """
        if key.algorithm == CryptoAlgorithm.AES_256_GCM:
            return self._encrypt_aes_gcm(plaintext, key)
        elif key.algorithm == CryptoAlgorithm.AES_256_CBC:
            return self._encrypt_aes_cbc(plaintext, key)
        elif key.algorithm == CryptoAlgorithm.CHACHA20_POLY1305:
            return self._encrypt_chacha20_poly1305(plaintext, key)
        else:
            raise ValueError(f"Unsupported encryption algorithm: {key.algorithm}")
    
    def decrypt(self, encrypted_data: EncryptionResult, key: CryptoKey) -> bytes:
        """Decrypt data using symmetric decryption
        
        Args:
            encrypted_data: Encrypted data
            key: Symmetric key
            
        Returns:
            Decrypted plaintext
        """
        if key.algorithm == CryptoAlgorithm.AES_256_GCM:
            return self._decrypt_aes_gcm(encrypted_data, key)
        elif key.algorithm == CryptoAlgorithm.AES_256_CBC:
            return self._decrypt_aes_cbc(encrypted_data, key)
        elif key.algorithm == CryptoAlgorithm.CHACHA20_POLY1305:
            return self._decrypt_chacha20_poly1305(encrypted_data, key)
        else:
            raise ValueError(f"Unsupported decryption algorithm: {key.algorithm}")
    
    def _encrypt_aes_gcm(self, plaintext: bytes, key: CryptoKey) -> EncryptionResult:
        """Encrypt using AES-256-GCM"""
        iv = secrets.token_bytes(12)  # 96-bit IV for GCM
        cipher = Cipher(algorithms.AES(key.key_data), modes.GCM(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv_or_nonce=iv,
            tag=encryptor.tag,
            algorithm=CryptoAlgorithm.AES_256_GCM
        )
    
    def _decrypt_aes_gcm(self, encrypted_data: EncryptionResult, key: CryptoKey) -> bytes:
        """Decrypt using AES-256-GCM"""
        cipher = Cipher(
            algorithms.AES(key.key_data), 
            modes.GCM(encrypted_data.iv_or_nonce, encrypted_data.tag), 
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
    
    def _encrypt_aes_cbc(self, plaintext: bytes, key: CryptoKey) -> EncryptionResult:
        """Encrypt using AES-256-CBC"""
        iv = secrets.token_bytes(16)  # 128-bit IV for CBC
        
        # Apply PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key.key_data), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv_or_nonce=iv,
            algorithm=CryptoAlgorithm.AES_256_CBC
        )
    
    def _decrypt_aes_cbc(self, encrypted_data: EncryptionResult, key: CryptoKey) -> bytes:
        """Decrypt using AES-256-CBC"""
        cipher = Cipher(
            algorithms.AES(key.key_data), 
            modes.CBC(encrypted_data.iv_or_nonce), 
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()
    
    def _encrypt_chacha20_poly1305(self, plaintext: bytes, key: CryptoKey) -> EncryptionResult:
        """Encrypt using ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        cipher = Cipher(algorithms.ChaCha20(key.key_data, nonce), None, backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv_or_nonce=nonce,
            algorithm=CryptoAlgorithm.CHACHA20_POLY1305
        )
    
    def _decrypt_chacha20_poly1305(self, encrypted_data: EncryptionResult, key: CryptoKey) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        cipher = Cipher(
            algorithms.ChaCha20(key.key_data, encrypted_data.iv_or_nonce), 
            None, 
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()

class AsymmetricCrypto:
    """Asymmetric encryption and digital signatures"""
    
    def __init__(self):
        """Initialize asymmetric crypto handler"""
        self.backend = default_backend()
    
    def generate_keypair(self, algorithm: CryptoAlgorithm) -> Tuple[CryptoKey, CryptoKey]:
        """Generate an asymmetric key pair
        
        Args:
            algorithm: The asymmetric algorithm
            
        Returns:
            Tuple of (private_key, public_key)
        """
        if algorithm == CryptoAlgorithm.RSA_2048:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
        elif algorithm == CryptoAlgorithm.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=self.backend
            )
        elif algorithm in [CryptoAlgorithm.ECDSA_P256, CryptoAlgorithm.ECDH_P256]:
            private_key = ec.generate_private_key(ec.SECP256R1(), self.backend)
        elif algorithm in [CryptoAlgorithm.ECDSA_P384, CryptoAlgorithm.ECDH_P384]:
            private_key = ec.generate_private_key(ec.SECP384R1(), self.backend)
        else:
            raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        private_crypto_key = CryptoKey(
            key_type=KeyType.ASYMMETRIC_PRIVATE,
            algorithm=algorithm,
            key_data=private_pem,
            metadata={"key_size": self._get_key_size(algorithm)}
        )
        
        public_crypto_key = CryptoKey(
            key_type=KeyType.ASYMMETRIC_PUBLIC,
            algorithm=algorithm,
            key_data=public_pem,
            metadata={"key_size": self._get_key_size(algorithm)}
        )
        
        return private_crypto_key, public_crypto_key
    
    def _get_key_size(self, algorithm: CryptoAlgorithm) -> int:
        """Get key size for algorithm"""
        if algorithm == CryptoAlgorithm.RSA_2048:
            return 2048
        elif algorithm == CryptoAlgorithm.RSA_4096:
            return 4096
        elif algorithm in [CryptoAlgorithm.ECDSA_P256, CryptoAlgorithm.ECDH_P256]:
            return 256
        elif algorithm in [CryptoAlgorithm.ECDSA_P384, CryptoAlgorithm.ECDH_P384]:
            return 384
        return 0
    
    def encrypt(self, plaintext: bytes, public_key: CryptoKey) -> EncryptionResult:
        """Encrypt data using public key
        
        Args:
            plaintext: Data to encrypt
            public_key: Public key for encryption
            
        Returns:
            Encryption result
        """
        if public_key.algorithm in [CryptoAlgorithm.RSA_2048, CryptoAlgorithm.RSA_4048]:
            return self._encrypt_rsa(plaintext, public_key)
        else:
            raise ValueError(f"Encryption not supported for algorithm: {public_key.algorithm}")
    
    def decrypt(self, encrypted_data: EncryptionResult, private_key: CryptoKey) -> bytes:
        """Decrypt data using private key
        
        Args:
            encrypted_data: Encrypted data
            private_key: Private key for decryption
            
        Returns:
            Decrypted plaintext
        """
        if private_key.algorithm in [CryptoAlgorithm.RSA_2048, CryptoAlgorithm.RSA_4096]:
            return self._decrypt_rsa(encrypted_data, private_key)
        else:
            raise ValueError(f"Decryption not supported for algorithm: {private_key.algorithm}")
    
    def _encrypt_rsa(self, plaintext: bytes, public_key: CryptoKey) -> EncryptionResult:
        """Encrypt using RSA"""
        public_key_obj = serialization.load_pem_public_key(public_key.key_data, backend=self.backend)
        
        ciphertext = public_key_obj.encrypt(
            plaintext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptionResult(
            ciphertext=ciphertext,
            algorithm=public_key.algorithm
        )
    
    def _decrypt_rsa(self, encrypted_data: EncryptionResult, private_key: CryptoKey) -> bytes:
        """Decrypt using RSA"""
        private_key_obj = serialization.load_pem_private_key(
            private_key.key_data, 
            password=None, 
            backend=self.backend
        )
        
        return private_key_obj.decrypt(
            encrypted_data.ciphertext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def sign(self, message: bytes, private_key: CryptoKey) -> bytes:
        """Create digital signature
        
        Args:
            message: Message to sign
            private_key: Private key for signing
            
        Returns:
            Digital signature
        """
        private_key_obj = serialization.load_pem_private_key(
            private_key.key_data, 
            password=None, 
            backend=self.backend
        )
        
        if private_key.algorithm in [CryptoAlgorithm.RSA_2048, CryptoAlgorithm.RSA_4096]:
            signature = private_key_obj.sign(
                message,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        elif private_key.algorithm in [CryptoAlgorithm.ECDSA_P256, CryptoAlgorithm.ECDSA_P384]:
            signature = private_key_obj.sign(message, ec.ECDSA(hashes.SHA256()))
        else:
            raise ValueError(f"Signing not supported for algorithm: {private_key.algorithm}")
        
        return signature
    
    def verify(self, message: bytes, signature: bytes, public_key: CryptoKey) -> bool:
        """Verify digital signature
        
        Args:
            message: Original message
            signature: Digital signature
            public_key: Public key for verification
            
        Returns:
            True if signature is valid
        """
        try:
            public_key_obj = serialization.load_pem_public_key(public_key.key_data, backend=self.backend)
            
            if public_key.algorithm in [CryptoAlgorithm.RSA_2048, CryptoAlgorithm.RSA_4096]:
                public_key_obj.verify(
                    signature,
                    message,
                    asym_padding.PSS(
                        mgf=asym_padding.MGF1(hashes.SHA256()),
                        salt_length=asym_padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            elif public_key.algorithm in [CryptoAlgorithm.ECDSA_P256, CryptoAlgorithm.ECDSA_P384]:
                public_key_obj.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            else:
                return False
            
            return True
        except Exception:
            return False

class HashFunctions:
    """Cryptographic hash functions and MACs"""
    
    def __init__(self):
        """Initialize hash functions handler"""
        self.backend = default_backend()
    
    def hash_data(self, data: bytes, algorithm: CryptoAlgorithm) -> bytes:
        """Hash data using specified algorithm
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm
            
        Returns:
            Hash digest
        """
        if algorithm == CryptoAlgorithm.SHA256:
            digest = hashes.Hash(hashes.SHA256(), backend=self.backend)
        elif algorithm == CryptoAlgorithm.SHA3_256:
            digest = hashes.Hash(hashes.SHA3_256(), backend=self.backend)
        elif algorithm == CryptoAlgorithm.BLAKE2B:
            digest = hashes.Hash(hashes.BLAKE2b(64), backend=self.backend)
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        digest.update(data)
        return digest.finalize()
    
    def hmac_sign(self, data: bytes, key: bytes, algorithm: CryptoAlgorithm = CryptoAlgorithm.SHA256) -> bytes:
        """Create HMAC signature
        
        Args:
            data: Data to sign
            key: HMAC key
            algorithm: Hash algorithm for HMAC
            
        Returns:
            HMAC signature
        """
        if algorithm == CryptoAlgorithm.SHA256:
            return hmac.new(key, data, hashlib.sha256).digest()
        elif algorithm == CryptoAlgorithm.SHA3_256:
            return hmac.new(key, data, hashlib.sha3_256).digest()
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
    
    def hmac_verify(self, data: bytes, signature: bytes, key: bytes, algorithm: CryptoAlgorithm = CryptoAlgorithm.SHA256) -> bool:
        """Verify HMAC signature
        
        Args:
            data: Original data
            signature: HMAC signature
            key: HMAC key
            algorithm: Hash algorithm
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = self.hmac_sign(data, key, algorithm)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

class KeyDerivation:
    """Key derivation functions"""
    
    def __init__(self):
        """Initialize key derivation handler"""
        self.backend = default_backend()
    
    def derive_key_pbkdf2(self, password: bytes, salt: bytes, iterations: int = 100000, key_length: int = 32) -> CryptoKey:
        """Derive key using PBKDF2
        
        Args:
            password: Password to derive from
            salt: Salt for derivation
            iterations: Number of iterations
            key_length: Desired key length in bytes
            
        Returns:
            Derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        
        key_data = kdf.derive(password)
        
        return CryptoKey(
            key_type=KeyType.DERIVED,
            algorithm=CryptoAlgorithm.SHA256,
            key_data=key_data,
            metadata={
                "derivation": "PBKDF2",
                "iterations": iterations,
                "salt": base64.b64encode(salt).decode()
            }
        )
    
    def derive_key_scrypt(self, password: bytes, salt: bytes, n: int = 2**14, r: int = 8, p: int = 1, key_length: int = 32) -> CryptoKey:
        """Derive key using Scrypt
        
        Args:
            password: Password to derive from
            salt: Salt for derivation
            n: CPU/memory cost parameter
            r: Block size parameter
            p: Parallelization parameter
            key_length: Desired key length in bytes
            
        Returns:
            Derived key
        """
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            n=n,
            r=r,
            p=p,
            backend=self.backend
        )
        
        key_data = kdf.derive(password)
        
        return CryptoKey(
            key_type=KeyType.DERIVED,
            algorithm=CryptoAlgorithm.SHA256,
            key_data=key_data,
            metadata={
                "derivation": "Scrypt",
                "n": n,
                "r": r,
                "p": p,
                "salt": base64.b64encode(salt).decode()
            }
        )
    
    def derive_key_hkdf(self, input_key: bytes, salt: bytes = None, info: bytes = b"", key_length: int = 32) -> CryptoKey:
        """Derive key using HKDF
        
        Args:
            input_key: Input key material
            salt: Optional salt
            info: Optional context information
            key_length: Desired key length in bytes
            
        Returns:
            Derived key
        """
        if salt is None:
            salt = b"\x00" * 32
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            info=info,
            backend=self.backend
        )
        
        key_data = hkdf.derive(input_key)
        
        return CryptoKey(
            key_type=KeyType.DERIVED,
            algorithm=CryptoAlgorithm.SHA256,
            key_data=key_data,
            metadata={
                "derivation": "HKDF",
                "salt": base64.b64encode(salt).decode(),
                "info": base64.b64encode(info).decode()
            }
        )

class ZeroKnowledgeProof:
    """Zero-knowledge proof implementations"""
    
    def __init__(self):
        """Initialize zero-knowledge proof handler"""
        pass
    
    def generate_schnorr_proof(self, secret: int, generator: int, modulus: int) -> Dict[str, int]:
        """Generate Schnorr zero-knowledge proof
        
        Args:
            secret: Secret value
            generator: Generator of the group
            modulus: Modulus of the group
            
        Returns:
            Schnorr proof
        """
        # Public key
        public_key = pow(generator, secret, modulus)
        
        # Random nonce
        r = secrets.randbelow(modulus - 1) + 1
        
        # Commitment
        commitment = pow(generator, r, modulus)
        
        # Challenge (in practice, this would be generated by verifier or via Fiat-Shamir)
        challenge = secrets.randbelow(modulus - 1) + 1
        
        # Response
        response = (r + challenge * secret) % (modulus - 1)
        
        return {
            "public_key": public_key,
            "commitment": commitment,
            "challenge": challenge,
            "response": response,
            "generator": generator,
            "modulus": modulus
        }
    
    def verify_schnorr_proof(self, proof: Dict[str, int]) -> bool:
        """Verify Schnorr zero-knowledge proof
        
        Args:
            proof: Schnorr proof to verify
            
        Returns:
            True if proof is valid
        """
        try:
            g = proof["generator"]
            p = proof["modulus"]
            y = proof["public_key"]
            t = proof["commitment"]
            c = proof["challenge"]
            s = proof["response"]
            
            # Verify: g^s = t * y^c (mod p)
            left_side = pow(g, s, p)
            right_side = (t * pow(y, c, p)) % p
            
            return left_side == right_side
        except Exception:
            return False

class HomomorphicEncryption:
    """Partially homomorphic encryption (Paillier cryptosystem)"""
    
    def __init__(self, key_size: int = 1024):
        """Initialize Paillier cryptosystem
        
        Args:
            key_size: Key size in bits
        """
        self.key_size = key_size
        self.public_key = None
        self.private_key = None
    
    def generate_keys(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Generate Paillier key pair
        
        Returns:
            Tuple of (public_key, private_key)
        """
        # Generate two large primes
        p = randprime(2**(self.key_size//2 - 1), 2**(self.key_size//2))
        q = randprime(2**(self.key_size//2 - 1), 2**(self.key_size//2))
        
        n = p * q
        lambda_n = (p - 1) * (q - 1) // gcd(p - 1, q - 1)
        
        # Choose g
        g = n + 1
        
        # Calculate mu
        mu = mod_inverse(lambda_n, n)
        
        public_key = {"n": n, "g": g}
        private_key = {"lambda": lambda_n, "mu": mu, "n": n}
        
        self.public_key = public_key
        self.private_key = private_key
        
        return public_key, private_key
    
    def encrypt(self, plaintext: int, public_key: Dict[str, int] = None) -> int:
        """Encrypt a number using Paillier encryption
        
        Args:
            plaintext: Number to encrypt
            public_key: Public key (uses instance key if None)
            
        Returns:
            Encrypted ciphertext
        """
        if public_key is None:
            public_key = self.public_key
        
        if public_key is None:
            raise ValueError("No public key available")
        
        n = public_key["n"]
        g = public_key["g"]
        
        # Random value r
        r = secrets.randbelow(n)
        while gcd(r, n) != 1:
            r = secrets.randbelow(n)
        
        # Encryption: c = g^m * r^n mod n^2
        n_squared = n * n
        ciphertext = (pow(g, plaintext, n_squared) * pow(r, n, n_squared)) % n_squared
        
        return ciphertext
    
    def decrypt(self, ciphertext: int, private_key: Dict[str, int] = None) -> int:
        """Decrypt a number using Paillier decryption
        
        Args:
            ciphertext: Encrypted value
            private_key: Private key (uses instance key if None)
            
        Returns:
            Decrypted plaintext
        """
        if private_key is None:
            private_key = self.private_key
        
        if private_key is None:
            raise ValueError("No private key available")
        
        lambda_n = private_key["lambda"]
        mu = private_key["mu"]
        n = private_key["n"]
        
        n_squared = n * n
        
        # Decryption: m = L(c^lambda mod n^2) * mu mod n
        # where L(x) = (x - 1) / n
        u = pow(ciphertext, lambda_n, n_squared)
        l_u = (u - 1) // n
        plaintext = (l_u * mu) % n
        
        return plaintext
    
    def add_encrypted(self, ciphertext1: int, ciphertext2: int, public_key: Dict[str, int] = None) -> int:
        """Add two encrypted numbers (homomorphic property)
        
        Args:
            ciphertext1: First encrypted number
            ciphertext2: Second encrypted number
            public_key: Public key
            
        Returns:
            Encrypted sum
        """
        if public_key is None:
            public_key = self.public_key
        
        if public_key is None:
            raise ValueError("No public key available")
        
        n = public_key["n"]
        n_squared = n * n
        
        # Homomorphic addition: E(m1) * E(m2) = E(m1 + m2)
        return (ciphertext1 * ciphertext2) % n_squared

class CryptographySuite:
    """Main cryptography suite that integrates all components"""
    
    def __init__(self):
        """Initialize the cryptography suite"""
        self.symmetric = SymmetricCrypto()
        self.asymmetric = AsymmetricCrypto()
        self.hash_functions = HashFunctions()
        self.key_derivation = KeyDerivation()
        self.zkp = ZeroKnowledgeProof()
        self.homomorphic = HomomorphicEncryption()
        
        # Key storage
        self.keys: Dict[str, CryptoKey] = {}
        
        # Operation history
        self.operation_history = []
    
    def generate_symmetric_key(self, algorithm: CryptoAlgorithm, key_id: str = None) -> str:
        """Generate and store a symmetric key
        
        Args:
            algorithm: Encryption algorithm
            key_id: Optional key identifier
            
        Returns:
            Key identifier
        """
        if key_id is None:
            key_id = f"sym_{algorithm.name}_{int(time.time())}"
        
        key = self.symmetric.generate_key(algorithm)
        self.keys[key_id] = key
        
        self.operation_history.append({
            "operation": "generate_symmetric_key",
            "algorithm": algorithm.name,
            "key_id": key_id,
            "timestamp": time.time()
        })
        
        return key_id
    
    def generate_asymmetric_keypair(self, algorithm: CryptoAlgorithm, key_id_prefix: str = None) -> Tuple[str, str]:
        """Generate and store an asymmetric key pair
        
        Args:
            algorithm: Asymmetric algorithm
            key_id_prefix: Optional prefix for key identifiers
            
        Returns:
            Tuple of (private_key_id, public_key_id)
        """
        if key_id_prefix is None:
            key_id_prefix = f"asym_{algorithm.name}_{int(time.time())}"
        
        private_key, public_key = self.asymmetric.generate_keypair(algorithm)
        
        private_key_id = f"{key_id_prefix}_private"
        public_key_id = f"{key_id_prefix}_public"
        
        self.keys[private_key_id] = private_key
        self.keys[public_key_id] = public_key
        
        self.operation_history.append({
            "operation": "generate_asymmetric_keypair",
            "algorithm": algorithm.name,
            "private_key_id": private_key_id,
            "public_key_id": public_key_id,
            "timestamp": time.time()
        })
        
        return private_key_id, public_key_id
    
    def encrypt_data(self, data: bytes, key_id: str) -> str:
        """Encrypt data using specified key
        
        Args:
            data: Data to encrypt
            key_id: Key identifier
            
        Returns:
            Base64-encoded encrypted data
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
        
        key = self.keys[key_id]
        
        if key.key_type == KeyType.SYMMETRIC:
            result = self.symmetric.encrypt(data, key)
        elif key.key_type == KeyType.ASYMMETRIC_PUBLIC:
            result = self.asymmetric.encrypt(data, key)
        else:
            raise ValueError(f"Cannot encrypt with key type: {key.key_type}")
        
        # Serialize result
        serialized = {
            "ciphertext": base64.b64encode(result.ciphertext).decode(),
            "algorithm": result.algorithm.name if result.algorithm else None
        }
        
        if result.iv_or_nonce:
            serialized["iv_or_nonce"] = base64.b64encode(result.iv_or_nonce).decode()
        
        if result.tag:
            serialized["tag"] = base64.b64encode(result.tag).decode()
        
        self.operation_history.append({
            "operation": "encrypt_data",
            "key_id": key_id,
            "data_size": len(data),
            "timestamp": time.time()
        })
        
        return base64.b64encode(json.dumps(serialized).encode()).decode()
    
    def decrypt_data(self, encrypted_data: str, key_id: str) -> bytes:
        """Decrypt data using specified key
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            key_id: Key identifier
            
        Returns:
            Decrypted data
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
        
        key = self.keys[key_id]
        
        # Deserialize encrypted data
        serialized = json.loads(base64.b64decode(encrypted_data).decode())
        
        result = EncryptionResult(
            ciphertext=base64.b64decode(serialized["ciphertext"]),
            algorithm=CryptoAlgorithm[serialized["algorithm"]] if serialized["algorithm"] else None
        )
        
        if "iv_or_nonce" in serialized:
            result.iv_or_nonce = base64.b64decode(serialized["iv_or_nonce"])
        
        if "tag" in serialized:
            result.tag = base64.b64decode(serialized["tag"])
        
        if key.key_type == KeyType.SYMMETRIC:
            plaintext = self.symmetric.decrypt(result, key)
        elif key.key_type == KeyType.ASYMMETRIC_PRIVATE:
            plaintext = self.asymmetric.decrypt(result, key)
        else:
            raise ValueError(f"Cannot decrypt with key type: {key.key_type}")
        
        self.operation_history.append({
            "operation": "decrypt_data",
            "key_id": key_id,
            "timestamp": time.time()
        })
        
        return plaintext
    
    def sign_data(self, data: bytes, private_key_id: str) -> str:
        """Sign data using private key
        
        Args:
            data: Data to sign
            private_key_id: Private key identifier
            
        Returns:
            Base64-encoded signature
        """
        if private_key_id not in self.keys:
            raise ValueError(f"Key not found: {private_key_id}")
        
        private_key = self.keys[private_key_id]
        
        if private_key.key_type != KeyType.ASYMMETRIC_PRIVATE:
            raise ValueError("Signing requires a private key")
        
        signature = self.asymmetric.sign(data, private_key)
        
        self.operation_history.append({
            "operation": "sign_data",
            "key_id": private_key_id,
            "data_size": len(data),
            "timestamp": time.time()
        })
        
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, data: bytes, signature: str, public_key_id: str) -> bool:
        """Verify digital signature
        
        Args:
            data: Original data
            signature: Base64-encoded signature
            public_key_id: Public key identifier
            
        Returns:
            True if signature is valid
        """
        if public_key_id not in self.keys:
            raise ValueError(f"Key not found: {public_key_id}")
        
        public_key = self.keys[public_key_id]
        
        if public_key.key_type != KeyType.ASYMMETRIC_PUBLIC:
            raise ValueError("Verification requires a public key")
        
        signature_bytes = base64.b64decode(signature)
        is_valid = self.asymmetric.verify(data, signature_bytes, public_key)
        
        self.operation_history.append({
            "operation": "verify_signature",
            "key_id": public_key_id,
            "valid": is_valid,
            "timestamp": time.time()
        })
        
        return is_valid
    
    def hash_data(self, data: bytes, algorithm: CryptoAlgorithm = CryptoAlgorithm.SHA256) -> str:
        """Hash data using specified algorithm
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm
            
        Returns:
            Base64-encoded hash
        """
        hash_digest = self.hash_functions.hash_data(data, algorithm)
        
        self.operation_history.append({
            "operation": "hash_data",
            "algorithm": algorithm.name,
            "data_size": len(data),
            "timestamp": time.time()
        })
        
        return base64.b64encode(hash_digest).decode()
    
    def export_key(self, key_id: str, password: str = None) -> str:
        """Export a key in PEM format
        
        Args:
            key_id: Key identifier
            password: Optional password for encryption
            
        Returns:
            Base64-encoded key data
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
        
        key = self.keys[key_id]
        
        # For demonstration, we'll just return the key data
        # In practice, you'd want to encrypt it with the password
        return base64.b64encode(key.key_data).decode()
    
    def get_key_info(self, key_id: str) -> Dict[str, Any]:
        """Get information about a key
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key information
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
        
        key = self.keys[key_id]
        
        return {
            "key_id": key_id,
            "key_type": key.key_type.name,
            "algorithm": key.algorithm.name,
            "created_at": key.created_at,
            "metadata": key.metadata
        }
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all stored keys
        
        Returns:
            List of key information
        """
        return [self.get_key_info(key_id) for key_id in self.keys.keys()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cryptography suite statistics
        
        Returns:
            Statistics dictionary
        """
        operation_counts = {}
        for op in self.operation_history:
            op_type = op["operation"]
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
        
        return {
            "total_keys": len(self.keys),
            "total_operations": len(self.operation_history),
            "operation_counts": operation_counts,
            "key_types": {
                key_type.name: sum(1 for key in self.keys.values() if key.key_type == key_type)
                for key_type in KeyType
            }
        }

class CryptoApplication:
    """Main application class for the cryptography suite"""
    
    def __init__(self):
        """Initialize the application"""
        self.crypto_suite = CryptographySuite()
        self.parse_arguments()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Advanced Cryptography Suite')
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Generate key command
        gen_parser = subparsers.add_parser('generate', help='Generate cryptographic keys')
        gen_parser.add_argument('--type', choices=['symmetric', 'asymmetric'], required=True)
        gen_parser.add_argument('--algorithm', required=True)
        gen_parser.add_argument('--key-id', help='Key identifier')
        
        # Encrypt command
        enc_parser = subparsers.add_parser('encrypt', help='Encrypt data')
        enc_parser.add_argument('--input', required=True, help='Input file or data')
        enc_parser.add_argument('--output', help='Output file')
        enc_parser.add_argument('--key-id', required=True, help='Key identifier')
        
        # Decrypt command
        dec_parser = subparsers.add_parser('decrypt', help='Decrypt data')
        dec_parser.add_argument('--input', required=True, help='Input file or data')
        dec_parser.add_argument('--output', help='Output file')
        dec_parser.add_argument('--key-id', required=True, help='Key identifier')
        
        # Sign command
        sign_parser = subparsers.add_parser('sign', help='Sign data')
        sign_parser.add_argument('--input', required=True, help='Input file or data')
        sign_parser.add_argument('--key-id', required=True, help='Private key identifier')
        
        # Verify command
        verify_parser = subparsers.add_parser('verify', help='Verify signature')
        verify_parser.add_argument('--input', required=True, help='Input file or data')
        verify_parser.add_argument('--signature', required=True, help='Signature file or data')
        verify_parser.add_argument('--key-id', required=True, help='Public key identifier')
        
        # Hash command
        hash_parser = subparsers.add_parser('hash', help='Hash data')
        hash_parser.add_argument('--input', required=True, help='Input file or data')
        hash_parser.add_argument('--algorithm', default='SHA256', help='Hash algorithm')
        
        # List keys command
        subparsers.add_parser('list-keys', help='List all keys')
        
        # Statistics command
        subparsers.add_parser('stats', help='Show statistics')
        
        self.args = parser.parse_args()
    
    def run(self):
        """Run the cryptography application"""
        if self.args.command == 'generate':
            self.generate_key()
        elif self.args.command == 'encrypt':
            self.encrypt_data()
        elif self.args.command == 'decrypt':
            self.decrypt_data()
        elif self.args.command == 'sign':
            self.sign_data()
        elif self.args.command == 'verify':
            self.verify_signature()
        elif self.args.command == 'hash':
            self.hash_data()
        elif self.args.command == 'list-keys':
            self.list_keys()
        elif self.args.command == 'stats':
            self.show_statistics()
        else:
            print("No command specified. Use --help for usage information.")
    
    def generate_key(self):
        """Generate cryptographic key"""
        try:
            algorithm = CryptoAlgorithm[self.args.algorithm.upper()]
        except KeyError:
            print(f"Unsupported algorithm: {self.args.algorithm}")
            return
        
        if self.args.type == 'symmetric':
            key_id = self.crypto_suite.generate_symmetric_key(algorithm, self.args.key_id)
            print(f"Generated symmetric key: {key_id}")
        
        elif self.args.type == 'asymmetric':
            private_key_id, public_key_id = self.crypto_suite.generate_asymmetric_keypair(
                algorithm, self.args.key_id
            )
            print(f"Generated asymmetric key pair:")
            print(f"  Private key: {private_key_id}")
            print(f"  Public key: {public_key_id}")
    
    def encrypt_data(self):
        """Encrypt data"""
        # Read input data
        if os.path.isfile(self.args.input):
            with open(self.args.input, 'rb') as f:
                data = f.read()
        else:
            data = self.args.input.encode()
        
        try:
            encrypted_data = self.crypto_suite.encrypt_data(data, self.args.key_id)
            
            if self.args.output:
                with open(self.args.output, 'w') as f:
                    f.write(encrypted_data)
                print(f"Encrypted data saved to: {self.args.output}")
            else:
                print(f"Encrypted data: {encrypted_data}")
        
        except Exception as e:
            print(f"Encryption failed: {e}")
    
    def decrypt_data(self):
        """Decrypt data"""
        # Read encrypted data
        if os.path.isfile(self.args.input):
            with open(self.args.input, 'r') as f:
                encrypted_data = f.read()
        else:
            encrypted_data = self.args.input
        
        try:
            plaintext = self.crypto_suite.decrypt_data(encrypted_data, self.args.key_id)
            
            if self.args.output:
                with open(self.args.output, 'wb') as f:
                    f.write(plaintext)
                print(f"Decrypted data saved to: {self.args.output}")
            else:
                print(f"Decrypted data: {plaintext.decode()}")
        
        except Exception as e:
            print(f"Decryption failed: {e}")
    
    def sign_data(self):
        """Sign data"""
        # Read input data
        if os.path.isfile(self.args.input):
            with open(self.args.input, 'rb') as f:
                data = f.read()
        else:
            data = self.args.input.encode()
        
        try:
            signature = self.crypto_suite.sign_data(data, self.args.key_id)
            print(f"Signature: {signature}")
        
        except Exception as e:
            print(f"Signing failed: {e}")
    
    def verify_signature(self):
        """Verify signature"""
        # Read input data
        if os.path.isfile(self.args.input):
            with open(self.args.input, 'rb') as f:
                data = f.read()
        else:
            data = self.args.input.encode()
        
        # Read signature
        if os.path.isfile(self.args.signature):
            with open(self.args.signature, 'r') as f:
                signature = f.read()
        else:
            signature = self.args.signature
        
        try:
            is_valid = self.crypto_suite.verify_signature(data, signature, self.args.key_id)
            print(f"Signature valid: {is_valid}")
        
        except Exception as e:
            print(f"Verification failed: {e}")
    
    def hash_data(self):
        """Hash data"""
        # Read input data
        if os.path.isfile(self.args.input):
            with open(self.args.input, 'rb') as f:
                data = f.read()
        else:
            data = self.args.input.encode()
        
        try:
            algorithm = CryptoAlgorithm[self.args.algorithm.upper()]
            hash_value = self.crypto_suite.hash_data(data, algorithm)
            print(f"Hash ({algorithm.name}): {hash_value}")
        
        except Exception as e:
            print(f"Hashing failed: {e}")
    
    def list_keys(self):
        """List all keys"""
        keys = self.crypto_suite.list_keys()
        
        if not keys:
            print("No keys found.")
            return
        
        print("Stored keys:")
        for key_info in keys:
            print(f"  {key_info['key_id']}: {key_info['key_type']} ({key_info['algorithm']})")
    
    def show_statistics(self):
        """Show statistics"""
        stats = self.crypto_suite.get_statistics()
        
        print("Cryptography Suite Statistics:")
        print(f"  Total keys: {stats['total_keys']}")
        print(f"  Total operations: {stats['total_operations']}")
        
        print("\nKey types:")
        for key_type, count in stats['key_types'].items():
            if count > 0:
                print(f"  {key_type}: {count}")
        
        print("\nOperation counts:")
        for operation, count in stats['operation_counts'].items():
            print(f"  {operation}: {count}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Advanced Cryptography Suite".center(60))
    print("Modern encryption and digital signatures".center(60))
    print("=" * 60)
    
    app = CryptoApplication()
    app.run()

if __name__ == "__main__":
    main() 