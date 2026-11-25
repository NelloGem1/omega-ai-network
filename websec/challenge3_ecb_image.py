import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(32)
w = 64
stripe_w = w * 3          # 192 bytes per row
black = b'\x00' * stripe_w
gray  = b'\x80' * stripe_w
# 32 rows: 4 identical stripes of (black*8 + gray*8)
rows = []
for s in range(4):
    rows += [black]*8 + [gray]*8
raw = b''.join(rows)
pad = (16 - len(raw) % 16) % 16
raw += b'\x00' * pad
enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
ct = enc.update(raw) + enc.finalize()
chunk = (stripe_w*16) // 16 * 16  # one stripe = 16 rows = 3072 bytes
ident = all(ct[i*chunk:(i+1)*chunk] == ct[0:chunk] for i in range(4))
print(f'ECB-encrypted 4 identical horizontal stripes: all ciphertext stripes identical? {ident}')
print('=> the penguin outline survives encryption under ECB (the famous Tux demo).')
print('Fix: use CBC/GCM/CTR with random IV, never ECB.')
