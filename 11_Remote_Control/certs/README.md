# SSL/TLS Certificates for Remote Control

This directory contains the SSL/TLS certificates used for secure communication between the remote control client and server.

## Certificate Generation

To generate a self-signed certificate and private key, run the following command:

```bash
python generate_cert.py
```

This will create:
- `server.key` - The private key file
- `server.crt` - The certificate file

## Command-Line Options

The certificate generator supports the following options:

```
usage: generate_cert.py [-h] [--common-name COMMON_NAME] [--key KEY]
                        [--cert CERT] [--key-size KEY_SIZE]
                        [--validity VALIDITY] [--password PASSWORD]

Generate SSL certificates

optional arguments:
  -h, --help            show this help message and exit
  --common-name COMMON_NAME
                        Common name for the certificate
  --key KEY             Path to save the private key
  --cert CERT           Path to save the certificate
  --key-size KEY_SIZE   Size of the key in bits
  --validity VALIDITY   Validity period in days
  --password PASSWORD   Password to encrypt the private key
```

## Security Considerations

- Keep your private key secure and do not share it.
- The default certificate is self-signed, which means it will generate browser warnings.
- For production use, consider using certificates from a trusted Certificate Authority.
- Self-signed certificates are sufficient for testing and personal use.

## Certificate Details

The generated certificate includes:
- The hostname as the Common Name
- Alternative names for localhost and 127.0.0.1
- 1-year validity by default
- 2048-bit RSA key by default 