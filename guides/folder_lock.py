#!/usr/bin/env python3
"""folder_lock.py — Hybrid RSA+AES folder encryption (Nello Gem / prime-discovery).

RSA can't encrypt large data, so this uses hybrid encryption:
  - AES-256-GCM encrypts each file with a fresh random key + nonce
  - RSA-2048-OAEP wraps the AES key (the small thing RSA is good at)
  - A manifest file records all metadata so unlock can rebuild the tree

Commands:
  keygen                     -> writes ./folder_lock_pub.pem + ./folder_lock_priv.pem
  lock <folder>              -> encrypts every file in <folder> in place (.enc)
  unlock <folder>            -> restores files from .enc files

Keys are looked for in the current directory (or --keydir DIR).
"""
import argparse
import json
import os
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"FLOCK1\n"


def load_keys(keydir):
    with open(os.path.join(keydir, "folder_lock_priv.pem"), "rb") as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
    with open(os.path.join(keydir, "folder_lock_pub.pem"), "rb") as f:
        pub = serialization.load_pem_public_key(f.read())
    return priv, pub


def keygen(keydir):
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = priv.public_key()
    with open(os.path.join(keydir, "folder_lock_priv.pem"), "wb") as f:
        f.write(priv.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()))
    with open(os.path.join(keydir, "folder_lock_pub.pem"), "wb") as f:
        f.write(pub.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo))
    print("Keypair written to:")
    print("  folder_lock_pub.pem   (share this — the 'padlock')")
    print("  folder_lock_priv.pem  (KEEP SECRET — the only way in)")


def _iter_files(folder):
    for root, _dirs, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            if not name.endswith(".enc") and not name.endswith(".flock"):
                yield path


def lock(folder, keydir):
    _priv, pub = load_keys(keydir)

    aes_key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(aes_key)

    manifest = {"magic": MAGIC.decode().strip(), "files": []}
    for path in _iter_files(folder):
        rel = os.path.relpath(path, folder)
        nonce = os.urandom(12)
        with open(path, "rb") as f:
            data = f.read()
        ct = aes.encrypt(nonce, data, rel.encode())
        with open(path + ".enc", "wb") as f:
            f.write(nonce + ct)
        os.remove(path)
        manifest["files"].append(rel)
        print(f"  locked {rel}  ({len(data)} -> {len(ct)+12} bytes)")

    # RSA-wrap the AES key: 256 bytes -> 256 bytes ciphertext blob
    wrapped = pub.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None))

    mpath = os.path.join(folder, ".flock")
    with open(mpath, "wb") as f:
        f.write(json.dumps(manifest).encode() + b"\n" + MAGIC + wrapped)
    print(f"\nLocked {len(manifest['files'])} file(s). AES key wrapped with RSA.")
    print(f"Manifest: {mpath}")


def unlock(folder, keydir):
    priv, _pub = load_keys(keydir)
    mpath = os.path.join(folder, ".flock")
    if not os.path.exists(mpath):
        sys.exit("No .flock manifest found — is this folder locked?")

    raw = open(mpath, "rb").read()
    idx = raw.find(MAGIC)
    if idx < 0:
        sys.exit("Bad manifest: magic marker missing")
    manifest = json.loads(raw[:idx].decode().strip())
    wrapped = raw[idx + len(MAGIC):]

    aes_key = priv.decrypt(
        wrapped,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None))
    aes = AESGCM(aes_key)

    for rel in manifest["files"]:
        enc_path = os.path.join(folder, rel + ".enc")
        out_path = os.path.join(folder, rel)
        if not os.path.exists(enc_path):
            print(f"  WARN missing {enc_path}, skipping")
            continue
        blob = open(enc_path, "rb").read()
        nonce, ct = blob[:12], blob[12:]
        data = aes.decrypt(nonce, ct, rel.encode())
        os.makedirs(os.path.dirname(out_path) or folder, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
        os.remove(enc_path)
        print(f"  unlocked {rel}")

    os.remove(mpath)
    print(f"\nUnlocked {len(manifest['files'])} file(s). Folder restored.")


def main():
    ap = argparse.ArgumentParser(description="Hybrid RSA+AES folder lock")
    ap.add_argument("command", choices=["keygen", "lock", "unlock"])
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--keydir", default=".", help="dir holding the keypair")
    args = ap.parse_args()

    if args.command == "keygen":
        keygen(args.keydir)
    elif not args.folder:
        ap.error(f"{args.command} requires <folder>")
    elif args.command == "lock":
        lock(args.folder, args.keydir)
    else:
        unlock(args.folder, args.keydir)


if __name__ == "__main__":
    main()
