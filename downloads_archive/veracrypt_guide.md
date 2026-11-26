# VeraCrypt Beginner's Guide

**Installed version:** 1.26.31 (stable, released November 2, 2026)
**Install location:** `C:\Program Files\VeraCrypt\VeraCrypt.exe`
**Official site:** https://veracrypt.io

## What is VeraCrypt?

VeraCrypt is a free, open-source disk encryption tool (forked from TrueCrypt). It encrypts data using strong algorithms (AES, Serpent, Twofish, or combinations). It can encrypt:

- **Encrypted file containers** — a single file that acts like a virtual encrypted drive
- **Partitions or whole drives** — encrypt an entire volume (including the system disk)
- **Non-system partitions** — encrypt a data partition

> **Important:** VeraCrypt does NOT encrypt folders "in place" like Windows' built-in folder encryption or tools like our `folder_lock.py`. Instead, you create an encrypted *container file*, then *mount* it as a drive letter. Files are copied into that virtual drive.

## Core Concepts

| Term | Meaning |
|------|---------|
| **Container** | A single file (e.g., `myvault.vc`) that contains an encrypted filesystem |
| **Mount** | Decrypt the container on-the-fly and assign it a drive letter (e.g., `V:`) |
| **Dismount** | Lock the container and remove the drive letter |
| **Password / PIM** | Your decryption key. PIM = Personal Iterations Multiplier (optional, makes brute-force harder) |
| **Keyfile** | An extra secret file required to mount — security even if the password leaks |
| **Hibernation file / pagefile / temp** | While a container is mounted, data is decrypted in RAM — it is only written encrypted to disk inside the container |

## Creating an Encrypted Container (step by step)

1. Launch **VeraCrypt.exe**. Click **"Create Volume"**.
2. Choose volume type:
   - **"Create an encrypted file container"** ← pick this for a portable vault
   - "Encrypt a non-system partition/drive" or "Encrypt the system partition/drive" for whole-disk encryption
3. Click **Next**, then **"Standard VeraCrypt volume"** (hidden volumes are an advanced feature).
4. Choose where to save the container file, e.g., `D:\vaults\myvault.vc`. The file size = the container size.
5. Choose encryption algorithm: **AES + SHA-512** is the sensible default. Click **Next**.
6. Choose volume size (e.g., 1 GB). Click **Next**.
7. Choose a **strong password** (20+ characters recommended). Optionally set a **PIM**. Click **Next**.
   - Optional: **"Use keyfiles"** — click "Select Keyfiles" and pick one or more files. The password alone won't mount the volume without them.
8. Choose filesystem: **exFAT** (works everywhere) or **NTFS** (better permissions). Leave cluster size default. Click **Next**.
9. Move your mouse around the "Random Pool" area until the entropy bar is full — this generates the encryption key from real random data.
10. Click **"Format"** and wait. The container is now created and mounted.

## Mounting / Dismounting a Container

**Mount:**
1. In VeraCrypt, click **"Select File"** and pick your `.vc` container.
2. Choose an empty drive letter (e.g., `V:`).
3. Click **"Mount"**, enter your password (and provide keyfiles if you used them).
4. The container appears as a normal drive letter — copy files in/out as usual.

**Dismount:**
- Click **"Dismount"** or **"Dismount All"** in VeraCrypt (or right-click the drive letter in Explorer → VeraCrypt → Dismount).
- Data on the drive letter becomes unreadable immediately; only the encrypted `.vc` file remains on disk.

**Auto-mount:** VeraCrypt can mount containers at startup — use **System → Preferences → Auto-Mount Devices** or the built-in task scheduler integration.

## System Encryption (encrypting Windows itself)

VeraCrypt can encrypt the drive Windows boots from:

1. Click **"System" → "Encrypt System Partition/Drive"**.
2. Choose "Normal" or "Hidden" system encryption.
3. Follow the wizard: it encrypts in place, creates a VeraCrypt Boot Loader, and asks you to burn/print a **VeraCrypt Rescue Disk** — **do this**, it can recover a broken bootloader.
4. After encryption, the machine prompts for the VeraCrypt password **before Windows starts**.

⚠️ System encryption requires a BIOS that supports the needed boot modes; keep the rescue disk safe. Consider enabling it only if you understand the boot-time recovery process.

## Keyfiles

- A keyfile is just any file whose contents become part of your decryption key.
- Even with the correct password, the container **cannot** be mounted without the keyfile — great "second factor" protection.
- You can combine keyfiles with a password, or use keyfiles *instead* of a password (not recommended alone — keyfiles are often guessable patterns if weak).
- Best practice: use a file with high entropy (e.g., 1 KB of random data), not a photo or document.

## Other Useful Features

- **Hidden volumes** — a second encrypted volume hidden inside the outer container (plausible deniability; advanced).
- **VeraCrypt Traveler Disk** — run VeraCrypt from a USB stick.
- **Command-line tool** (`VeraCrypt Format.exe`, `VeraCrypt.exe /v /l V file.vc`) for scripting.
- **RAM encryption / secure desktop** — passwords are typed on an isolated secure desktop.

## Comparison: VeraCrypt Containers vs. our `folder_lock.py`

| | VeraCrypt | `folder_lock.py` (in-place lock) |
|---|---|---|
| Approach | Encrypted **container file** mounted as a drive | Encrypts files **in place** inside a real folder |
| Folder stays a normal folder? | No — files live inside a virtual drive | Yes |
| Plausibility | Anyone can see a `.vc` file exists | Original filenames/structure may still be visible |
| Cross-platform | Windows, macOS, Linux | Depends on script implementation |
| Strength | Battle-tested, audited lineage (TrueCrypt fork), AES | Depends on implementation quality |
| Best for | Large private data stores, portable vaults, whole-disk | Quick lock/unlock of a working folder |

**Rule of thumb:** use VeraCrypt when you want a serious, portable encrypted vault; use `folder_lock.py` when you just need to quickly hide a folder's contents while keeping normal file paths.

## Security Tips

- Use a long, unique password — VeraCrypt cannot recover a forgotten password (no backdoors).
- Keep containers on encrypted/backup drives and remember the `.vc` file itself is safe to store anywhere.
- Dismount before sleep/shutdown; VeraCrypt also has auto-dismount hotkeys (Settings → Hot Keys).
- For maximum security on the system drive, combine VeraCrypt system encryption with a strong pre-boot password.
