# Hashcat Guide — Password Audit Tool

**Installed:** `C:\Users\neilh\hashcat\hashcat.exe` (v8.0.0)

## What it does
Tests password hashes against wordlists or brute-force — the standard tool for **auditing YOUR OWN** password strength and recovering forgotten passwords on systems you own.

## ⚠️ Legal — only audit what you own
Using hashcat on systems/hashes you don't own or have permission to test is **illegal** in most countries.

## Quick concepts
- A **hash** = one-way fingerprint of a password (can't reverse it — only guess-and-check)
- **Mode (-m)** = hash type: `-m 0` MD5, `-m 1000` NTLM (Windows), `-m 1800` sha512crypt (Linux)
- **Attack** = wordlist (`-a 0`) or brute-force (`-a 3`)

## Your first test — crack a hash YOU create
```powershell
cd C:\Users\neilh\hashcat
# See example hashes for every mode:
hashcat.exe --example-hashes

# Crack an MD5 hash you make yourself:
# 1. Hash "password123" → 02d8e4c5b0d4f7aabbccddeeff001122 (example)
# 2. Run:
hashcat.exe -m 0 -a 0 02d8e4c5b0d4f7aabbccddeeff001122 wordlists\rockyou.txt
```

## Wordlists
Download `rockyou.txt` (14M real passwords) — the classic audit list:
- Place in `C:\Users\neilh\hashcat\wordlists\`
- Or generate rules-based mutations with `-r rules\best64.rule`

## GPU acceleration
Hashcat uses your GPU — NVIDIA/AMD cards crack 100-1000× faster than CPU. Check backends: `hashcat.exe -I`

## The lesson for YOU
Run hashcat against **your own** password hashes (export from KeePassXC/Bitwarden or hash your own passwords) — if it cracks in seconds, that password is weak. That's the defensive use.
