# Cryptomator — Beginner's Guide

> Install date: installed via winget — **Cryptomator 1.19.7**
> Location: `C:\Program Files\Cryptomator\Cryptomator.exe`
> Java: **bundled** (Java 26 + JavaFX runtime in `C:\Program Files\Cryptomator\runtime` — no separate JRE needed)
> WinFsp 2.2 installed as the virtual filesystem driver (enables real drive-letter mounting; without it Cryptomator falls back to slower WebDAV).

## What Cryptomator Does

Cryptomator creates an **encrypted vault** — a folder of ciphertext files that you place *inside* an existing cloud-synced folder (Dropbox, Google Drive, OneDrive, etc.). The cloud syncs the encrypted files; only you can decrypt them. Unlike VeraCrypt, there is **no giant container file** — each vault file is individually encrypted, so cloud sync and backup tools work file-by-file and there's no single-point-of-failure container to corrupt.

## How the Encryption Works (simple version)

- **File contents**: AES-GCM encryption, split into ~32 KiB chunks, each with a random nonce. A random file-content key per file is stored in an encrypted file header.
- **File names & metadata**: AES-SIV (RFC 5297) — directory and file names are encrypted deterministically, so the cloud sees opaque ciphertext names. Because SIV is deterministic, identical filenames produce identical ciphertext (a known, accepted trade-off).
- **Keys**: derived from your vault password using **scrypt** (memory-hard KDF). The master key unlocks everything.
- **Vault format**: version 8, `vault.cryptomator` config file (a JWT) at the vault root stores format version and algorithm metadata — it contains *no secrets*.
- This is **client-side encryption**: the cloud provider only ever sees ciphertext. Even if their servers are breached, your files are safe as long as your password is strong.

## Creating a Vault

1. Open `Cryptomator.exe` (Windows Start menu → Cryptomator).
2. Click **"Create a vault"**.
3. **Vault location**: browse into your synced folder, e.g. `C:\Users\<you>\Dropbox\` or `...\Google Drive\`. Give the vault a name (e.g. `private`). Cryptomator creates a folder with that name inside your cloud folder.
4. **Vault password**: choose a strong, unique password (this is the *only* thing protecting your files). Re-enter to confirm. Optionally tick **"Use recovery key"** — Cryptomator will show a one-time recovery key (a list of words). **Write it down and store it somewhere safe**; it can unlock the vault if you forget the password. You can also choose *"I will store the password in my password manager"* for convenience.
5. Click **Create Vault**. The vault appears in the Cryptomator window.

## Unlocking and Mounting

1. In the Cryptomator window, select your vault and click **Unlock**.
2. Enter your password (or unlock with the recovery key).
3. Cryptomator mounts a **virtual drive** — with WinFsp installed this appears as a real drive letter (e.g. `X:\`). You can then open, edit, add, and delete files like any normal folder; everything is transparently encrypted/decrypted on the fly.
4. To lock: click the lock icon / **Lock** button, or just close Cryptomator. Files in the cloud folder remain encrypted at rest.
5. The vault folder itself (in your cloud directory) contains files like `d/` (directory metadata) and `C/` (encrypted contents) plus `vault.cryptomator` — all ciphertext.

> Tip: Windows may prompt to install the **WinFsp** driver certificate on first mount — accept it (it's already installed via winget).

## What the Cloud Sees

- File **contents**: fully encrypted (AES-GCM).
- File and folder **names**: encrypted (AES-SIV) — filenames, directory structure, and sizes leak almost nothing. (File *sizes* can slightly leak through ciphertext length — a known limitation of any sync-friendly encryption.)
- The cloud sees only opaque blobs like `1/XXXX/XXXXXXXX.vault` being created/changed.

## Mobile Companion App

Cryptomator also has apps for **iOS** and **Android** (App Store / Google Play, free/donationware). To access the same vault on mobile:

1. In the desktop app, select the vault → click the **hub/sync icon** or use **"Unlock & reveal vault location"** — mobile apps can open a vault directly from a synced folder (e.g. open Cryptomator mobile → "Add vault" → pick the vault folder inside your cloud drive app).
2. Alternatively, use **Cryptomator Hub** to share vaults between devices via a share link/QR code.
3. Mobile app also offers camera-based features like viewing encrypted images/PDFs and **WebDAV/WebRTC streaming** (protected media playback).

## Cryptomator vs. VeraCrypt vs. folder_lock.py

| | **Cryptomator** | **VeraCrypt** | **folder_lock.py** (script) |
|---|---|---|---|
| Model | Per-file encryption inside a cloud-synced folder | Single encrypted container file | Encrypts files in-place inside a folder |
| Cloud sync friendly | ✅ Excellent — files sync individually | ⚠️ Poor — container is one huge file; syncing mid-write corrupts it, and the container itself is a suspicious giant blob | ⚠️ Okay if sync paused during locking; risk of partial sync |
| Mounting | Virtual drive letter (WinFsp) or WebDAV | Drive letter / partition | Usually manual decrypt step |
| Use case | "My cloud folder should only ever hold ciphertext" | Encrypting a whole disk/partition or a portable container you carry around | Quick local folder obfuscation without installing an app |
| Strengths | Metadata hiding, seamless sync, cross-platform, mobile app | Mature, very strong, can do full-disk | Zero dependencies beyond Python |

**When to use which:**
- Files that live in Dropbox/Google Drive/OneDrive → **Cryptomator** (designed exactly for this).
- A portable encrypted volume you carry on USB, or full-disk encryption → **VeraCrypt**.
- A quick, ad-hoc encrypted folder on a single machine with no install → **folder_lock.py**.

## Tips & Best Practices

- **Strong vault password** — it is the *only* key. Use a password manager or the built-in recovery key.
- Keep the `vault.cryptomator` file and directory structure intact; deleting ciphertext files deletes your data.
- The vault folder can sit *inside* any synced folder — subfolders of the cloud root work too.
- Lock the vault when not in use; closing the app auto-locks.
- Keep local backups of critical files too — encryption protects confidentiality, not against deletion.
- Updates: Cryptomator auto-checks; reinstall via `winget upgrade Cryptomator.Cryptomator`.

## Useful Commands

```powershell
# Reinstall / upgrade
winget upgrade Cryptomator.Cryptomator

# Launch
& "C:\Program Files\Cryptomator\Cryptomator.exe"
```

## References

- Docs: https://docs.cryptomator.org/ (vault cryptography, architecture)
- Releases: https://github.com/cryptomator/cryptomator/releases
- WinFsp: https://winfsp.dev/
