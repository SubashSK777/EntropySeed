
# Coordinate-Based Key Derivation: A Proof-of-Concept

This repository contains a Python proof-of-concept for turning geographic coordinates into cryptographic keys. It is intended for educational and experimental purposes only.

> ## ⚠️ Brutal Truth First: Do Not Use This in Production
>
> **Do not invent your own crypto for real security.** This repository is for prototyping and experimenting with coordinates as an entropy source. For anything serious, use standard, reviewed primitives like **SHA-2/3, HKDF, AES-GCM, and ChaCha20-Poly1305**.
>
> **Got it? Good.**

-----

## Concept: From GPS Coordinates to Encryption Keys

This proof-of-concept demonstrates how to transform a list of `(x, y)` coordinates into a symmetric encryption key. The process follows a standard cryptographic pipeline to ensure that small changes in input lead to completely different keys.

### The Plan: Simple, Hard, Useful

1.  **Quantize Coordinates**: Convert floating-point coordinates into a deterministic stream of bytes.
      * *Example*: Round to 6 decimal places and pack as fixed-point 64-bit integers.
2.  **Mix with Salt & Nonce**: Combine the coordinate bytes with a random salt and a nonce.
      * The **salt** prevents pre-computation attacks (e.g., rainbow tables).
      * The **nonce** (Number used once) prevents replay attacks and is required by ciphers like AES-GCM.
3.  **Hash the Blob**: Use a cryptographic hash function like SHA-256 to create a raw, fixed-size entropy source from the mixed data.
      * `seed = SHA256(coord_bytes || salt)`
4.  **Derive Keys**: Use a Key Derivation Function (KDF) like **HKDF** to securely "stretch" the hash output into a cryptographically strong key.
      * This is a critical step to ensure the resulting keys have good cryptographic properties.
5.  **Encrypt & Authenticate**: Use a modern, authenticated encryption with associated data (AEAD) cipher like **AES-GCM** or **ChaCha20-Poly1305**.
      * **Never roll your own encryption mode.**

-----

## Python Proof-of-Concept

This script implements the full pipeline: coordinates → bytes → hash → KDF → encryption/decryption.

### Prerequisites

This code requires the `cryptography` library. Install it via pip:

```sh
pip install cryptography
```

### How to Run

1.  Save the code to a Python file.
2.  Execute it from your terminal.
3.  Expected output:
    ```
    ciphertext (hex): <a long, random hex string will be printed here>
    plaintext: b'top secret message'
    bad coords failed as expected: InvalidTag
    ```

-----

## 🚨 Key Warnings & Threat Model (Read This Like Law)

The security of this scheme is **extremely fragile** and depends entirely on the unpredictability of the coordinates.

  * **If coordinates are predictable, the system is broken.** An attacker who can guess or find the coordinates can trivially recover the key.
      * *Real-world example*: Using a car’s GPS route as a key is a terrible idea. An attacker who sees the route can brute-force the keys. Public landmarks, GPS data from phone backups, and known trajectories are **not secret**.
  * **This scheme alone does not provide confidentiality.** For real security, you **must** mix in a high-entropy secret that an attacker cannot guess, such as a strong password or a device-specific key.
  * **Always use a fresh, cryptographically secure random salt and nonce for every single encryption.** Never reuse a nonce with the same key.
  * **Never claim this scheme is secure without a formal cryptographic review and extensive testing.** This is a toy, not a product.

-----

## ✅ Tests You Must Run

Before considering a similar scheme for any application, you must perform rigorous validation.

  * **Entropy Tests**: Run statistical test suites (e.g., NIST STS) on the derived seed to ensure it is indistinguishable from random noise.
  * **Collision Tests**: Verify that tiny changes in coordinates produce completely different keys (the avalanche effect).
  * **Brute-Force Simulation**: Define a set of possible coordinates an attacker might know. Can they brute-force the key in a feasible amount of time? If yes, the system is insecure.
      * *Real-world example*: I once saw a startup use timestamps + coarse location as keys. They were cracked by an attacker replaying old timestamps. **Don’t be that startup.**

-----

## 🚀 Next Moves

This proof-of-concept can be extended to explore related ideas. Which path do you want to explore?

1.  **SECRET**: Add a secret/password mixing step (using PBKDF2 or Argon2) to make this scheme more practical and robust.
2.  **PRNG**: Build a toy Pseudo-Random Number Generator (PRNG) seeded from coordinates for generating non-critical random data.
3.  **ATTACK**: Simulate an attack. Given a small set of plausible coordinates, write a script to brute-force the key and demonstrate the inherent weakness.
