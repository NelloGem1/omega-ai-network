# Beginner's Guide to Gpg4win, Kleopatra, and OpenPGP

## What is Gpg4win?

**Gpg4win** is a Windows bundle that brings the GnuPG (GNU Privacy Guard) tools to
Windows in a friendly way. The most important parts are:

- **GnuPG (gpg.exe)** — the command-line engine that actually does the crypto.
- **Kleopatra** — the graphical user interface (GUI) for managing keys and
  encrypting/decrypting files. This is what most beginners should use.
- **GpgOL** — optional Outlook plugin for encrypting email.
- **Okular** — PDF viewer that can verify signed/decrypted PDFs.
- **GpgEX** — Explorer shell extension (right-click menu support for files).

Installed here: **Gpg4win 5.1.2** (contains GnuPG 2.5.24, Kleopatra 5.1.0).
Binaries live at `C:\Program Files\GnuPG\bin\` (e.g. `gpg.exe`, `kleopatra.exe`).

## What is OpenPGP?

OpenPGP (RFC 4880, now maintained by the openpgp working group) is an open,
public standard for:

- **Encryption** — scrambles data so only the intended recipient can read it.
- **Decryption** — the inverse operation.
- **Digital signatures** — proves a message/file came from you and wasn't tampered with.

It is built on **public-key cryptography**. Each person has a *keypair*:

- A **public key** — safe to share with anyone. Used to encrypt things *to* you,
  and to verify signatures *from* you.
- A **private key** — secret, never shared. Used to decrypt things *for* you
  and to create signatures.

A keypair also has a **fingerprint** (a long hex string, e.g.
`C466 CF70 3436 258C F6EB 87EF 7264 2FA7 B31A 1F05`) which uniquely identifies
the key. You verify fingerprints out-of-band (in person, on a website, via
another channel) before trusting a key.

## Step 1 — Generate a keypair in Kleopatra

1. Open **Kleopatra** (Start Menu → "Kleopatra", or `C:\Program Files\Gpg4win\bin\kleopatra.exe`).
2. Click **File → New Key Pair** (or the green "+" button on the toolbar).
3. Choose **Personal OpenPGP key pair** → Next.
4. Fill in:
   - **Name** (real name)
   - **Email address** — this links your key to an identity.
   - **Advanced settings** (optional): key type. Defaults are fine
     (RSA 2048+ or Curve25519). Set an **expiry date** if you like ("never"
     is common for personal keys).
5. Click **Next**, then **Create Key**.
6. Kleopatra will ask for a **passphrase** — this protects your private key.
   Choose a strong one and remember it; you can't decrypt anything without it.
7. Kleopatra generates a **revocation certificate**. Save/print it somewhere safe —
   it's the "kill switch" if your key is ever compromised or you lose your passphrase.

Your public key can now be found under **Certificates → All Certificates** (tab
"Secret Keys" shows private keys). Export your public key with
**File → Export Certificates** and share it with people who want to send you
encrypted files or verify your signatures.

## Step 2 — Encrypt and decrypt files

### From Kleopatra (GUI)

1. In the main window, click the **Encrypt** tab.
2. Drag files onto the big box (or click **Add Recipient** / choose files).
3. In the recipient list, click **Add Recipient** and type the recipient's
   email or paste their public key.
   - To encrypt **to yourself** (e.g. to store files securely), add your own key.
4. Choose output mode:
   - **Binary OpenPGP message** → `.gpg` file (compact, binary).
   - **ASCII-armored OpenPGP message** → `.asc` file (text-safe, good for email/paste).
5. Check "Sign with my key" if you also want a signature proving authorship.
6. Click **Encrypt** and enter your passphrase if signing.
7. Save the `.gpg`/`.asc` file and send it. The recipient decrypts it with
   **Decrypt** tab (choose file → Decrypt → enter *their* passphrase).

### From the command line (gpg.exe)

```powershell
# Encrypt a file to someone (creates file.gpg)
gpg --recipient "their@email.com" --encrypt file.txt

# Encrypt to yourself for private storage
gpg --recipient "me@email.com" --encrypt file.txt

# Decrypt
gpg --decrypt file.txt.gpg

# Decrypt and write to a specific file
gpg --decrypt --output out.txt file.txt.gpg

# Sign + encrypt (signing proves it was you)
gpg --recipient "them@email.com" --sign --encrypt file.txt
```

Or use Explorer right-click (GpgEX): select file → right-click →
**Encrypt** / **Sign and Encrypt**.

## File formats you will see

| Extension | Meaning |
|---|---|
| `.gpg` | Binary OpenPGP message (encrypted and/or signed data) |
| `.asc` | ASCII-armored OpenPGP message — same data, Base64-encoded with `-----BEGIN PGP MESSAGE-----` header so it survives email/text channels |
| `.sig` / `.asc` sig | Detached signature file proving integrity/authorship |
| `.key` / `.asc` key export | Your public key in ASCII armor (`-----BEGIN PGP PUBLIC KEY BLOCK-----`) |

An `.asc` file looks like plain text you could paste into an email; a `.gpg`
file is binary (still fine as an email attachment).

## Email encryption: OpenPGP vs S/MIME

- **OpenPGP** (what Gpg4win does) encrypts the *message content* using your
  PGP keys. Keys are self-issued and distributed manually (web of trust).
  Works in any mail client via copy/paste or plugins (e.g. Enigmail in
  Thunderbird, GpgOL for Outlook).
- **S/MIME** encrypts using **X.509 certificates** issued by a Certificate
  Authority (like a website HTTPS cert), integrated into many mail clients.

OpenPGP pros: free, no CA needed, you control your identity. Cons: key
exchange is manual and users often find key management confusing.
S/MIME pros: easier for enterprise, certs auto-distributed. Cons: needs a CA,
costs money, corporate-centric.

Gpg4win includes **GpgOL** which can add OpenPGP signing/encryption buttons
directly into Outlook.

## How does this compare to `folder_lock.py` and `age`?

- **folder_lock.py (typical password-based folder encryption)** — symmetric:
  one shared secret/password encrypts everything. Anyone with the password can
  read it; sharing requires sending the password through another channel. Simple
  but the "key" is the weak link and there's no sender authentication.
- **OpenPGP/Gpg4win** — asymmetric public-key: no secret is ever shared, anyone
  can encrypt *to* you with your public key, only you can decrypt with your
  private key. Also gives signatures. Heavier setup (key generation, key
  exchange, web of trust) but the gold standard for interoperable encryption.
- **age** — modern, simple file encryption tool by the same author as
  minisign. Much simpler CLI than GPG: one-line encrypt/decrypt with either a
  passphrase (scrypt) or an SSH-style public key (X25519). Less feature-rich
  (no signatures in the classic sense, no email ecosystem), but far easier for
  casual "encrypt this file for someone" use. Good choice for scripts/automation
  where GPG's complexity and config quirks get in the way.

**Rule of thumb:** need email encryption, signatures, or maximum
compatibility/interop → OpenPGP/Gpg4win. Need quick, modern, scriptable file
encryption → `age`. Quick-and-dirty local folder locking → password tool or
BitLocker/VeraCrypt.

## Quick reference

- Kleopatra GUI: Start Menu → Kleopatra (or `C:\Program Files\Gpg4win\bin\kleopatra.exe`)
- gpg CLI: `C:\Program Files\GnuPG\bin\gpg.exe`
- Your keys folder: `%APPDATA%\gnupg`
- Verify a download/signature, manage keys, revoke: all inside Kleopatra.
- Never share your **private** key or forget your **passphrase** — keep the
  revocation certificate somewhere safe.
