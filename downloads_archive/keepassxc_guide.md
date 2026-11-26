# KeePassXC — Beginner's Guide

**Version installed:** 2.8.0 (winget package `KeePassXCTeam.KeePassXC`, MSI)
**Install path:** `C:\Program Files\KeePassXC\KeePassXC.exe`
**Website:** https://keepassxc.org

KeePassXC is a free, open-source password manager. All passwords live in a single encrypted **vault file** (`.kdbx`) that only you can unlock. There is no cloud account required — your data stays on your machine unless you choose to sync it yourself.

---

## 1. How the Vault Encryption Works

When you create a vault, KeePassXC encrypts the entire database with:

- **Cipher:** AES-256 (default) or ChaCha20 — both are industry-standard, audited algorithms. AES-256 is the recommended default.
- **Key Derivation Function (KDF):** Argon2id by default. It deliberately consumes memory and CPU to make brute-force password guessing extremely slow. You can tune memory/time/parallelism in Database Settings → Encryption; the defaults are safe — only lower them if unlocking feels slow on a weak machine.
- **Composite key:** your vault is protected by whatever combination you choose at creation:
  - **Master password** — the main factor. Make it a long passphrase (4+ random words or 20+ characters). This is the ONLY thing standing between an attacker and your passwords.
  - **Key file** — an optional extra secret file. Adds a second factor: an attacker needs BOTH the password and the file.
  - **Windows Hello / system authentication** — optional quick-unlock via PIN/biometrics (convenience layer; the master password still protects the vault at rest).

**Key fact:** if you forget the master password AND have no key file, the vault is unrecoverable. KeePassXC cannot reset it — there is no backdoor.

---

## 2. Creating Your First Vault

1. Launch KeePassXC → **Databases → New Database**.
2. **Encryption settings:** accept defaults (AES-256 + Argon2). Optionally enable "Decrypt database after every lock" is NOT needed — leave defaults.
3. **General tab:** give it a name (e.g., "Personal") and optionally a color/icon.
4. **Credentials tab — choose your protection:**
   - Enter a strong **master password** (twice).
   - Click **Add key file** to also require a key file. Save it somewhere safe (USB drive, password manager of a *different* account, printed backup). **Do not store it next to the vault file** — that defeats the purpose.
   - Optionally enable **Windows Hello** for faster unlocks.
5. Click **Save As** and choose a location, e.g. `Documents\KeePassXC\Personal.kdbx`.
6. Test: lock the database (**Ctrl+L**) and unlock it with your password.

---

## 3. Saving Logins & Entries

- Right-click a group (e.g., "General") → **Add New → Add new login**.
- Fill in **Title** (recognizable name), **Username**, **Password**.
- Click the **dices icon** next to the password field to generate a strong one (adjust length, character sets; a 20+ char random password is ideal).
- **URL:** paste the site's login URL. This enables browser integration matching and Auto-Type website detection.
- **Notes/TOTP:** see section 5 for two-factor codes.
- **Ctrl+S** or auto-saves on lock/close.

Organize entries into **groups** (right-click → Add New → Add New Group) like folders — e.g., "Work", "Banking", "Shopping".

---

## 4. Unlocking, Locking, and Auto-Type

- **Lock:** Ctrl+L or the lock icon. The vault re-encrypts and stays safe even if the app crashes.
- **Inactivity lock:** Database Settings → Security → "Lock database after X seconds" (default 900s since 2.7.11).
- **Auto-Type** (type credentials into the focused window without clipboard exposure):
  1. Edit an entry → **Auto-Type** tab.
  2. Set **Auto-Type sequence**, e.g. `{USERNAME}{TAB}{PASSWORD}{ENTER}`.
  3. On the login page, focus the username field and press **Ctrl+Shift+V** (default) or right-click entry → **Perform Auto-Type**.
  4. If multiple windows are open, a selection dialog appears — pick the right one.

---

## 5. Two-Factor Codes (TOTP) Inside KeePassXC

KeePassXC can generate TOTP codes (Google Authenticator-style) so you don't need a separate 2FA app:

1. On the website's 2FA setup page, choose "can't scan QR? / enter manually" and copy the **secret key**.
2. Edit the entry → **TOTP** tab → paste the secret → **Add**.
3. The entry now shows a time-based code that refreshes every 30s. Click the clock icon to copy it.

KeePassXC 2.8.0 also supports **passkeys** — store WebAuthn credentials in entries for phishing-resistant login.

---

## 6. Browser Extension (KeePassXC-Browser)

Official extension for Chrome, Firefox, Edge, Brave, etc.:

1. Install the extension from your browser's store (search "KeePassXC-Browser").
2. In KeePassXC: **Tools → Settings → Browser Integration** → enable your browser(s).
3. First time you visit a login page, KeePassXC pops an **access request** — approve it (optionally limit to specific sites/groups).
4. The extension can autofill logins and offer to save new ones. KeePassXC must be **running with the database unlocked** — the extension talks to the local app over a secure local connection (no cloud involved).
5. Use **Ctrl+Shift+V / the extension icon** to fill; passwords are never stored by the browser extension itself.

---

## 7. Export Warnings — READ THIS

- **File → Export** writes all passwords as **plain CSV or XML — completely unencrypted**.
- Only export when necessary (e.g., migrating to another manager), then **securely delete the file immediately** (Shift+Delete won't fully erase it — use a tool like Eraser or cipher /w, or move it to an encrypted container).
- Never email, cloud-sync, or leave an export file on disk.
- If you must share, prefer KeePassXC's built-in sharing or an encrypted channel.

---

## 8. Backup Strategy

- **The `.kdbx` file IS the backup.** Copy it regularly to:
  - An external USB drive (kept offline — protects against ransomware).
  - An encrypted cloud folder (e.g., a VeraCrypt container or encrypted sync).
  - A second physical location.
- **Never back up only to the same disk/folder as the original.** 3-2-1 rule: 3 copies, 2 media types, 1 offsite.
- Test restores: occasionally copy the backup to a test machine and unlock it — an untested backup may be corrupt.
- KeePassXC has **Database → Database Settings → Backup Database** to snapshot before risky changes.
- If using a **key file**, back it up separately and securely — without it, newer backups are useless.
- **KeeShare** can sync vaults across devices (Tools → Settings → Sync, or via a shared network folder/WebDAV). Treat synced copies like any other backup.

---

## 9. Comparison: KeePassXC Vault vs. `folder_lock.py`

| | KeePassXC vault | `folder_lock.py` (folder encryption script) |
|---|---|---|
| Scope | All credentials in one portable `.kdbx` | One folder/directory tree |
| Encryption | AES-256/ChaCha20 + Argon2id, whole DB | Depends on script implementation |
| Access pattern | Unlock once → browse/fill/copy | Unlock per session/use |
| Password generation | Built-in strong generator | N/A |
| 2FA / TOTP / passkeys | Built-in | N/A |
| Browser autofill | Official extension | N/A |
| Auto-Type | Built-in (Ctrl+Shift+V) | N/A |
| Mobile sync | KeeShare / manual file copy | Copy encrypted folder |
| Risk if master password lost | Vault unrecoverable | Folder unrecoverable (same) |
| Auditability | Open source, ANSSI security-certified (2.7.9) | Depends on script quality |

**Takeaway:** use KeePassXC as the primary credential store. If `folder_lock.py` protects arbitrary files (documents, keys), keep it for that — but don't store passwords in plain files inside a locked folder when a proper vault exists.

---

## 10. Quick Reference

| Action | Shortcut / Where |
|---|---|
| New database | Databases → New Database |
| New login | Right-click group → Add New → Add new login |
| Generate password | Dices icon in entry editor |
| Lock database | Ctrl+L |
| Auto-Type | Ctrl+Shift+V (focus field first) |
| Copy TOTP | Clock icon on entry |
| Database settings | Database → Database Settings |
| Browser integration | Tools → Settings → Browser Integration |
| Export (dangerous) | File → Export |

*Stay safe: one strong master password + offline backups + never export to plaintext.*
