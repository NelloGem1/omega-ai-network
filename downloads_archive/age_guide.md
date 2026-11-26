# age — Beginner's Guide to Modern File Encryption

**age** is a simple, modern file-encryption tool created by Filippo Valsorda.
It has small explicit keys, no config options, and UNIX-style composability
(it reads stdin, writes stdout, works in pipes).

- Installed version: **v1.3.2** (via `winget install FiloSottile.age`)
- Binaries: `age.exe`, `age-keygen.exe`, `age-inspect.exe`, plus plugins
  (`age-plugin-pq.exe`, `age-plugin-tag.exe`, `age-plugin-tagpq.exe`,
  `age-plugin-batchpass.exe`) in
  `C:\Users\neilh\AppData\Local\Microsoft\WinGet\Packages\FiloSottile.age_Microsoft.Winget.Source_8wekyb3d8bbwe\age\`
- Winget also added `age`, `age-keygen`, `age-inspect` command-line aliases —
  they should work in any **new** terminal (restart your shell if not).
- Spec: https://age-encryption.org/v1
- Alternative Rust implementation: **rage** (interoperable — same format, same files).

## Two encryption modes

age supports two ways to encrypt:

1. **Recipient mode (asymmetric, recommended)** — the encrypted file can only be
   decrypted by whoever holds the matching secret key (identity). Anyone with
   the *public* key can encrypt, but cannot decrypt. Good for sending files to
   someone else or encrypting to "future you".
2. **Passphrase mode (`-p`)** — symmetric encryption protected by a passphrase
   you choose. Anyone with the passphrase can decrypt. Simple, but the
   passphrase is the only secret — use a long, unique one (a password manager
   passphrase is ideal).

## Step 1: Generate a keypair

```powershell
age-keygen -o C:\Users\neilh\age\key.txt
```

Output looks like:

```
Public key: age1e6r9et947y3g09f8w9thjmwfejn007n7hal576qzdpwmsau5p4xswftc6a
# created: 2026-11-25T12:57:07+08:00
# public key: age1e6r9et947y3g09f8w9thjmwfejn007n7hal576qzdpwmsau5p4xswftc6a
AGE-SECRET-KEY-1KTT5Y9G8DXFV4GPJY3FKM7KT792G6KPJGTTUSR6RQSE3ZR3Q022QG0JN29
```

- The file `key.txt` contains your **secret key** (`AGE-SECRET-KEY-1...`).
  Guard it like a password — anyone with it can decrypt everything encrypted
  to the matching public key. Back it up safely (offline/encrypted storage).
- The **public key** (`age1...`) is safe to share. Encrypt to it.

> Tip: v1.3.0+ supports post-quantum keys: `age-keygen -pq`.

## Step 2a: Encrypt to a recipient (public key)

```powershell
# Encrypt a file to your public key (or anyone else's)
age -r age1e6r9et947y3g09f8w9thjmwfejn007n7hal576qzdpwmsau5p4xswftc6a -o secret.txt.age secret.txt

# Encrypt a whole directory's tarball, streaming
age -r age1... < backup.tar > backup.tar.age

# Encrypt ASCII-armored output (safe to paste into email/chat)
age -r age1... -a -o secret.txt.age secret.txt
```

Multiple recipients can be added with repeated `-r` flags — anyone of them can decrypt.
You can also store recipients in a file (`-R recipients.txt`, one per line).

## Step 2b: Encrypt with a passphrase

```powershell
age -p -o secret.txt.age secret.txt
# prompts for passphrase twice

# or pipe stdin -> stdout
Get-Content secret.txt | age -p > secret.txt.age
```

No key file needed — just remember the passphrase.

## Step 3: Decrypt

```powershell
# Decrypt with your secret key file
age -d -i C:\Users\neilh\age\key.txt -o secret.txt secret.txt.age

# Decrypt a passphrase-encrypted file (prompts for passphrase)
age -d -o secret.txt secret.txt.age

# Inspect a .age file without decrypting (header info)
age-inspect secret.txt.age
```

## Comparison: `.age` vs `folder_lock.py` `.enc` files

| | **age `.age` files** | **`folder_lock.py` `.enc` files** |
|---|---|---|
| Format | **Open standard** ([age-encryption.org/v1](https://age-encryption.org/v1)) — spec is public, anyone can implement a decryptor | **Custom/proprietary** — only `folder_lock.py` can read them |
| Interoperability | Decryptable by age, rage (Rust), Typage (TypeScript/browser), plugins, many OS integrations | Locked to that one script; if it's lost or broken, data may be unrecoverable |
| Keys | Real keypairs (`age1...` public / `AGE-SECRET-KEY-1...` secret), passphrase mode, post-quantum option | Whatever the script implements |
| Auditability | Format and crypto (X25519/ChaCha20-Poly5, post-quantum ML-KEM in v1.3) are reviewed by the community | You must trust the script's implementation |
| Use case | Sharing files with others, long-term archives, anything that must outlive the tool | Quick local obfuscation/encryption of a folder on one machine |

**Bottom line:** `.age` files are a portable, standardized format that any
conforming tool can open. Custom `.enc` files from `folder_lock.py` only work
with that script — fine for casual local use, risky as your only copy of data.
If you want maximum safety, prefer age (or keep `folder_lock.py` *and* a
standard-format copy).

## Practical tips

- `age` works in pipes: `type bigfile.zip | age -r age1... > bigfile.zip.age`
- Armored (`-a`) output is base64-like text — good for email/chat, slightly larger.
- Decrypted output goes to stdout by default; use `-o` to write a file.
- Keep `key.txt` offline/backed-up. Losing the secret key = losing the data.
- Verify integrity: age uses authenticated encryption (ChaCha20-Poly1305), so
  tampering is detected on decrypt.
