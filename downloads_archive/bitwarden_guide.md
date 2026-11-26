# Bitwarden Guide — Cloud Password Manager

## What it is
Encrypted password vault that syncs across all your devices. Free tier is generous (unlimited passwords + devices).

## The security model — understand this
- Your vault is encrypted **on your device** with your master password
- Bitwarden's servers store only ciphertext — **they cannot read your passwords**
- Lose master password = lose vault forever (no recovery — that's the point)

## Getting started
1. Open **Bitwarden** app → "Create Account"
2. Master password = long + unique (this is the ONE password to rule them all)
3. Save the **emergency sheet / recovery codes** somewhere safe

## Daily use
- **Save logins**: browser extension detects login forms → offer to save
- **Auto-fill**: click the Bitwarden icon in browser → fills credentials
- **Secure notes**: store API keys, WiFi passwords, anything text
- **Generate passwords**: built-in generator — 20+ chars random for every site

## Desktop app + browser extension
- Desktop app = full vault management
- Browser extension = the daily driver (auto-fill, save prompts)
- They sync via your account automatically

## Bitwarden vs KeePassXC
| | Bitwarden | KeePassXC |
|---|---|---|
| Storage | Cloud (encrypted) | Local file only |
| Sync | Automatic | Manual/own method |
| Convenience | ⭐⭐⭐ | ⭐⭐ |
| Paranoia | trusts zero-knowledge math | trusts only yourself |
| Price | Free tier great | 100% free forever |

**Best setup:** Bitwarden for daily convenience + periodic encrypted export as backup.
