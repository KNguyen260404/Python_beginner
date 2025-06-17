# 🔐 Cryptography - Mật mã học

> "Without cryptography, there is no privacy." — Bruce Schneier

## 📖 Giới thiệu

**Cryptography (Mật mã học)** là ngành khoa học nghiên cứu các phương pháp bảo mật thông tin bằng cách biến đổi dữ liệu để chỉ những người được ủy quyền mới có thể đọc và xử lý. Đây là nền tảng của bảo mật trong các hệ thống máy tính, internet, tài chính, và nhiều lĩnh vực công nghệ khác.

---

## 🔍 Phân loại chính

### 1. 📦 Mật mã đối xứng (Symmetric Cryptography)
- Sử dụng **cùng một khóa** cho mã hóa và giải mã.
- Hiệu quả cao, nhanh chóng, nhưng khó khăn khi trao đổi khóa bí mật.

#### Ví dụ:
- AES (Advanced Encryption Standard)
- ChaCha20
- DES / 3DES (lỗi thời)
- Ascon (chuẩn hóa cho thiết bị IoT - NIST 2023)

---

### 2. 🔑 Mật mã bất đối xứng (Asymmetric Cryptography)
- Sử dụng **cặp khóa công khai và khóa riêng**.
- Ứng dụng trong chữ ký số, trao đổi khóa, và xác thực.

#### Ví dụ:
- RSA
- ECC (Elliptic Curve Cryptography)
- ElGamal
- Diffie-Hellman

---

### 3. 🧠 Hàm băm mật mã (Cryptographic Hash Functions)
- Biến đổi dữ liệu đầu vào thành "dấu vân tay số".
- Không thể đảo ngược, dùng để xác minh toàn vẹn dữ liệu.

#### Ví dụ:
- SHA-2 (SHA-256, SHA-512)
- SHA-3 (Keccak)
- BLAKE2, BLAKE3
- MD5, SHA-1 (đã lỗi thời)

---

### 4. ✍️ Chữ ký số (Digital Signatures)
- Bảo đảm rằng thông điệp đến từ đúng người và không bị thay đổi.
- Kết hợp mật mã bất đối xứng và hàm băm.

#### Ví dụ:
- RSA Signature
- ECDSA (Elliptic Curve DSA)
- Ed25519
- Dilithium, Falcon (Post-Quantum)

---

### 5. 🚀 Mật mã hậu lượng tử (Post-Quantum Cryptography)
- Thiết kế để chống lại các cuộc tấn công từ máy tính lượng tử.
- Được nghiên cứu và chuẩn hóa bởi NIST (Mỹ).

#### Ví dụ:
- Kyber (mã hóa khóa)
- Dilithium, Falcon (chữ ký số)
- SPHINCS+, BIKE, NTRU

---

### 6. 🛡️ Mã hóa xác thực (Authenticated Encryption)
- Kết hợp mã hóa + xác thực trong một bước.
- Đảm bảo cả tính bí mật và toàn vẹn.

#### Ví dụ:
- AES-GCM
- ChaCha20-Poly1305
- Ascon-128a (AEAD)

---

## 🧠 Ứng dụng thực tế

- Bảo mật giao tiếp (TLS/HTTPS)
- Bảo vệ dữ liệu cá nhân và doanh nghiệp
- Xác thực người dùng và hệ thống (Digital Signature)
- Tiền mã hóa (Bitcoin, Ethereum)
- IoT và hệ thống nhúng

---

## 📚 Tài liệu tham khảo

- [NIST Cryptographic Standards](https://csrc.nist.gov/Projects/Cryptographic-Standards-and-Guidelines)
- [Crypto101.io](https://crypto101.io/)
- [Practical Cryptography for Developers](https://cryptobook.nakov.com/)
- Bruce Schneier – *Applied Cryptography*

---

## 💡 Ghi chú

Mật mã học không ngừng phát triển. Khi máy tính lượng tử xuất hiện, các thuật toán mật mã truyền thống như RSA và ECC có thể bị phá vỡ. Vì vậy, nghiên cứu và ứng dụng **Post-Quantum Cryptography** đang ngày càng quan trọng.

---

## © Bản quyền

Tài liệu này được tạo bởi [@KNguyen260404] cho mục đích học tập và chia sẻ kiến thức.
