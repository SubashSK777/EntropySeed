# Requires: pip install cryptography
import struct
import os
import hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------- helpers ----------
def coords_to_bytes(coords, precision=6):
    b = bytearray()
    scale = 10**precision
    for x, y in coords:
        xi = int(round(x * scale))
        yi = int(round(y * scale))
        b += struct.pack("!q", xi)
        b += struct.pack("!q", yi)
    return bytes(b)

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

# ---------- key derivation ----------
def derive_keys(seed: bytes, info: bytes = b"coords-kdf", length=32):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=info,
    )
    return hkdf.derive(seed)

# ---------- encrypt/decrypt ----------
def encrypt_with_coords(coords, plaintext: bytes, associated_data: bytes = b""):
    coord_b = coords_to_bytes(coords, precision=6)
    salt = os.urandom(16)
    nonce = os.urandom(12)
    seed = sha256(coord_b + salt)
    aes_key = derive_keys(seed, info=b"coords->aes256", length=32)
    aesgcm = AESGCM(aes_key)
    ct = aesgcm.encrypt(nonce, plaintext, associated_data)
    return salt + nonce + ct

def decrypt_with_coords(coords, packaged: bytes, associated_data: bytes = b""):
    salt = packaged[:16]
    nonce = packaged[16:28]
    ct = packaged[28:]
    coord_b = coords_to_bytes(coords, precision=6)
    seed = sha256(coord_b + salt)
    aes_key = derive_keys(seed, info=b"coords->aes256", length=32)
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ct, associated_data)

# ---------- main ----------
if __name__ == "__main__":
    coords = [
        (12.9715987, 77.594566),
        (12.9716000, 77.594560)
    ]

    user_input = input("Enter text to encrypt: ").encode()

    packaged = encrypt_with_coords(coords, user_input, associated_data=b"header")
    recovered = decrypt_with_coords(coords, packaged, associated_data=b"header")

    print("\nEncrypted (hex):", packaged.hex())
    print("Decrypted text:", recovered.decode())
