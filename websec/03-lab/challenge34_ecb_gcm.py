import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

print('=== CHALLENGE 3: AES-ECB pattern leakage ===')
key = os.urandom(32)
# 64-byte block of repeated pattern -> classic "penguin" effect at block level
pt = b'\xff\x00\x00\xff' * 16          # 64 bytes = 4 AES blocks, repeating
enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
ct = enc.update(pt) + enc.finalize()
print('plaintext blocks (16B each):')
for i in range(0, len(pt), 16):
    print(f'  pt[{i}:{i+16}] = {pt[i:i+16].hex()}')
print('ciphertext blocks:')
for i in range(0, len(ct), 16):
    print(f'  ct[{i}:{i+16}] = {ct[i:i+16].hex()}')
same = all(ct[i:i+16] == ct[16:32] for i in range(0, 64, 16))
print(f'All 4 ciphertext blocks identical? {same}  <- ECB leaks structure!')

# Bonus: encrypt a small "image-like" BMP-ish pattern to show penguin effect
w, h = 64, 64
raw = b''.join(b'\x00' * w * 3 if (y // 8) % 2 == 0 else b'\xff' * w * 3 for y in range(h))
pad = (16 - len(raw) % 16) % 16
raw += b'\x00' * pad
enc2 = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
ct2 = enc2.update(raw) + enc2.finalize()
# show that row-pairs that repeat plaintext produce repeating ciphertext rows
row = 64 * 3  # 192 bytes = 12 blocks per row
rows_identical = sum(1 for r in range(0, h, 16) if ct2[r*row:(r+8)*row] == ct2[(r+8)*row:(r+16)*row])
print(f'ECB on 64x64 striped "image": {rows_identical} pairs of 8-row stripes produce identical ciphertext -> outlines survive!')

print()
print('=== CHALLENGE 4: AES-GCM nonce reuse ===')
key2 = os.urandom(32)
nonce = os.urandom(12)   # SAME nonce used twice = catastrophic
m1 = b'Attack at dawn!'
m2 = b'Attack at noon!'
c1 = AESGCM(key2).encrypt(nonce, m1, None)
c2 = AESGCM(key2).encrypt(nonce, m2, None)
ct1, tag1 = c1[:-16], c1[-16:]
ct2, tag2 = c2[:-16], c2[-16:]
print(f'msg1 = {m1!r}')
print(f'msg2 = {m2!r}')
print(f'ct1  = {ct1.hex()}')
print(f'ct2  = {ct2.hex()}')
print(f'ct1 XOR ct2 = {bytes(a^b for a,b in zip(ct1,ct2)).hex()}')
print(f'msg1 XOR msg2 = {bytes(a^b for a,b in zip(m1,m2)).hex()}')
print('GCM ciphertext = plaintext XOR keystream(nonce,key). Same nonce -> same keystream.')
print('So ct1 XOR ct2 == m1 XOR m2: attacker recovers XOR of plaintexts, and with known plaintext recovers the OTHER message entirely.')
print('In practice (e.g. nonce-misuse in TLS/IoT), full plaintext recovery + forged tags follow.')
