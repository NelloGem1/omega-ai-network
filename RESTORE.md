# 🔄 RESTORE GUIDE — rebuild everything from this repo

## Step 0 — prerequisites
- Windows 11 + WSL Ubuntu (or any Linux)
- `winget` for tool installs · Python 3.12+ · `uv` or standard pip
- Lean 4 via elan: `curl https://elan.lean-lang.org/elan-init.sh -sSf | sh`

## Step 1 — clone
```powershell
git clone https://github.com/NelloGem1/experiment-vault.git
cd experiment-vault
```

## Step 2 — restore by folder

### lean_lab/ (the proofs)
```bash
mkdir -p ~/lean_lab && cp -r lean_lab/* ~/lean_lab/
cd ~/lean_lab && lake exe cache get   # fetch Mathlib deps (~13GB)
lake build                           # verify all 8 theorems
```
Expected: `prime_coprime_210`, `prime_mod30`, `prime_gt_five_last_digit`, `infinite_primes_ours` all VERIFIED, axioms `[propext, Classical.choice, Quot.sound]`.

### crypto_research/ — just read the .md files. Nothing to install.

### prime_video/ (video pipeline)
```bash
pip install pillow edge-tts   # TTS + slides
# ffmpeg required for assembly: sudo apt install ffmpeg
# regenerate slides: python scripts/gen_fixes.py  (edit OUT path first)
# TTS per segment: edge-tts --voice en-US-ChristopherNeural --file audio/seg_NN.txt --write-media audio/seg_NN.mp3
# assemble: ffmpeg -f concat -safe 0 -i concat.txt -c copy prime_discovery.mp4
```

### scripts/ — copy needed .py/.sh to ~/ and run with python3
- `folder_lock.py` needs `pip install cryptography`
- `upload_prime.py` needs YouTube OAuth token (NOT in repo — re-auth via client_secret)

### youtube_tool_scripts/ — the automation code. Re-auth needed:
- Place your OWN `client_secret.json` + run auth flow → creates `token.json`
- NEVER commit those files.

### guides/ — copy *.md anywhere, read in Notepad/browser.

## Step 3 — reinstall tools (one winget line each)
```powershell
winget install FiloSottile.age GnuPG.Gpg4win IDRIX.VeraCrypt Cryptomator.Cryptomator KeePassXCTeam.KeePassXC Bitwarden.Bitwarden WiresharkFoundation.Wireshark Insecure.Nmap FiloSottile.mkcert hashcat.hashcat TorProject.TorBrowser
```
(folder_lock.py: `pip install cryptography` · age key at `C:\Users\neilh\age\key.txt` is LOCAL only)

## Step 4 — the secrets you must back up MANUALLY (not in repo)
| Secret | Location | Why |
|---|---|---|
| `folder_lock_priv.pem` | `C:\Users\neilh\RSA-Keys\` + `/home/neilh/secure/vault/` | unlocks sealed vault |
| `token.json` / `client_secret*.json` | `~/youtube-tool/` | YouTube API access |
| age `key.txt` | `C:\Users\neilh\age\` | age decryption |
| KeePassXC/Bitwarden vaults | wherever you save them | passwords |

> Store these on a USB drive or encrypted backup — this repo has ZERO secrets by design.
