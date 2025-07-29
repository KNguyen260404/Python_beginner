# Advanced Cryptography Suite

A comprehensive cryptography toolkit that implements modern encryption algorithms, digital signatures, key exchange protocols, and advanced cryptographic primitives.

## Features

- **Modern Encryption**: AES-256, ChaCha20-Poly1305, RSA encryption
- **Digital Signatures**: RSA-PSS, ECDSA with multiple curves
- **Key Exchange**: ECDH, Diffie-Hellman protocols
- **Hash Functions**: SHA-256, SHA-3, BLAKE2b with HMAC support
- **Key Derivation**: PBKDF2, Scrypt, HKDF implementations
- **Zero-Knowledge Proofs**: Schnorr proofs and commitments
- **Homomorphic Encryption**: Paillier cryptosystem for privacy-preserving computation
- **Post-Quantum Ready**: Extensible architecture for quantum-resistant algorithms

## Requirements

- Python 3.7+
- cryptography
- sympy
- numpy
- matplotlib

## Installation

1. Install the required packages:

```bash
pip install -r requirements_cryptography.txt
```

## Usage

### Command Line Interface

**Generate symmetric key:**
```bash
python 29_advanced_cryptography_suite.py generate --type symmetric --algorithm AES_256_GCM
```

**Generate asymmetric key pair:**
```bash
python 29_advanced_cryptography_suite.py generate --type asymmetric --algorithm RSA_2048
```

**Encrypt data:**
```bash
python 29_advanced_cryptography_suite.py encrypt --input message.txt --key-id sym_key_1 --output encrypted.dat
```

**Decrypt data:**
```bash
python 29_advanced_cryptography_suite.py decrypt --input encrypted.dat --key-id sym_key_1 --output decrypted.txt
```

**Sign data:**
```bash
python 29_advanced_cryptography_suite.py sign --input document.pdf --key-id private_key_1
```

**Verify signature:**
```bash
python 29_advanced_cryptography_suite.py verify --input document.pdf --signature signature.sig --key-id public_key_1
```

**Hash data:**
```bash
python 29_advanced_cryptography_suite.py hash --input data.txt --algorithm SHA256
```

### Supported Algorithms

#### Symmetric Encryption
- **AES-256-GCM**: Authenticated encryption with 256-bit keys
- **AES-256-CBC**: Block cipher with PKCS7 padding
- **ChaCha20-Poly1305**: Stream cipher with authentication

#### Asymmetric Encryption
- **RSA-2048/4096**: Public key encryption and signatures
- **ECDSA-P256/P384**: Elliptic curve digital signatures
- **ECDH-P256/P384**: Elliptic curve key exchange

#### Hash Functions
- **SHA-256**: Secure Hash Algorithm 256-bit
- **SHA3-256**: Keccak-based hash function
- **BLAKE2b**: High-speed cryptographic hash

## Advanced Features

### Zero-Knowledge Proofs
```python
from cryptography_suite import CryptographySuite

suite = CryptographySuite()

# Generate Schnorr proof
proof = suite.zkp.generate_schnorr_proof(secret=12345, generator=2, modulus=2**256-189)

# Verify proof
is_valid = suite.zkp.verify_schnorr_proof(proof)
```

### Homomorphic Encryption
```python
# Generate Paillier keys
public_key, private_key = suite.homomorphic.generate_keys()

# Encrypt numbers
encrypted_5 = suite.homomorphic.encrypt(5, public_key)
encrypted_3 = suite.homomorphic.encrypt(3, public_key)

# Add encrypted numbers (homomorphic property)
encrypted_sum = suite.homomorphic.add_encrypted(encrypted_5, encrypted_3, public_key)

# Decrypt result
result = suite.homomorphic.decrypt(encrypted_sum, private_key)  # Should be 8
```

### Key Derivation
```python
# PBKDF2 key derivation
password = b"secure_password"
salt = secrets.token_bytes(32)
derived_key = suite.key_derivation.derive_key_pbkdf2(password, salt, iterations=100000)

# Scrypt key derivation (memory-hard)
scrypt_key = suite.key_derivation.derive_key_scrypt(password, salt)

# HKDF for key expansion
expanded_key = suite.key_derivation.derive_key_hkdf(master_key, salt, info=b"application_context")
```

## Project Structure

- `SymmetricCrypto`: AES, ChaCha20 encryption/decryption
- `AsymmetricCrypto`: RSA, ECDSA key generation and operations
- `HashFunctions`: SHA, BLAKE2, HMAC implementations
- `KeyDerivation`: PBKDF2, Scrypt, HKDF functions
- `ZeroKnowledgeProof`: Schnorr proofs and verification
- `HomomorphicEncryption`: Paillier cryptosystem
- `CryptographySuite`: Main integration class

## Security Best Practices

### Key Management
- Generate keys using cryptographically secure random number generators
- Store private keys securely with proper access controls
- Use key derivation functions for password-based encryption
- Implement key rotation policies

### Encryption
- Always use authenticated encryption (GCM mode) when possible
- Use unique IVs/nonces for each encryption operation
- Verify authentication tags before decrypting
- Use appropriate key sizes (256-bit for symmetric, 2048+ for RSA)

### Digital Signatures
- Hash messages before signing for efficiency and security
- Use PSS padding for RSA signatures
- Verify signatures before trusting signed data
- Use elliptic curve signatures for better performance

## Performance Optimization

- **Hardware Acceleration**: Leverages AES-NI and other CPU instructions
- **Memory Management**: Secure memory handling for sensitive data
- **Batch Operations**: Efficient processing of multiple operations
- **Key Caching**: Optimized key storage and retrieval

## Examples

### Complete Encryption Workflow
```python
from cryptography_suite import CryptographySuite, CryptoAlgorithm

suite = CryptographySuite()

# Generate keys
sym_key_id = suite.generate_symmetric_key(CryptoAlgorithm.AES_256_GCM)
priv_key_id, pub_key_id = suite.generate_asymmetric_keypair(CryptoAlgorithm.RSA_2048)

# Encrypt data
message = b"Secret message"
encrypted = suite.encrypt_data(message, sym_key_id)

# Sign encrypted data
signature = suite.sign_data(encrypted.encode(), priv_key_id)

# Verify and decrypt
is_valid = suite.verify_signature(encrypted.encode(), signature, pub_key_id)
if is_valid:
    decrypted = suite.decrypt_data(encrypted, sym_key_id)
    print(f"Decrypted: {decrypted.decode()}")
```

### Secure Communication Protocol
```python
# Alice generates keys
alice_priv, alice_pub = suite.generate_asymmetric_keypair(CryptoAlgorithm.ECDH_P256)

# Bob generates keys
bob_priv, bob_pub = suite.generate_asymmetric_keypair(CryptoAlgorithm.ECDH_P256)

# Derive shared secret (simplified ECDH)
# In practice, you'd use proper ECDH key exchange
shared_secret = suite.key_derivation.derive_key_hkdf(
    input_key=b"shared_material",  # Would be actual ECDH result
    info=b"secure_channel"
)

# Use shared secret for symmetric encryption
message = b"Confidential data"
encrypted = suite.encrypt_data(message, shared_secret)
```

## Testing and Validation

### Cryptographic Test Vectors
- NIST test vectors for AES, SHA algorithms
- RFC test vectors for key derivation functions
- Cross-validation with other cryptographic libraries

### Security Analysis
- Constant-time implementations where applicable
- Side-channel attack resistance
- Memory safety and secure cleanup

## Compliance and Standards

- **FIPS 140-2**: Federal Information Processing Standards
- **Common Criteria**: International security evaluation standard
- **NIST Guidelines**: Following latest cryptographic recommendations
- **RFC Standards**: Implementation of standardized protocols

## Troubleshooting

- **Key not found**: Ensure keys are generated and stored properly
- **Decryption failures**: Verify correct key and algorithm pairing
- **Signature verification fails**: Check key types and data integrity
- **Performance issues**: Consider hardware acceleration options

## Future Enhancements

- **Post-Quantum Algorithms**: CRYSTALS-Kyber, CRYSTALS-Dilithium
- **Threshold Cryptography**: Multi-party computation schemes
- **Attribute-Based Encryption**: Fine-grained access control
- **Hardware Security Module**: HSM integration support

## License

This project is open source and available under the MIT License. 