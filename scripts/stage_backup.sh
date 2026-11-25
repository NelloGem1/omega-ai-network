#!/bin/bash
set -e
BK=/home/neilh/gh_backup
rm -rf $BK /tmp/dec_*
mkdir -p $BK/{crypto_research,lean_lab/LeanLab,lean_lab_root,prime_video,audio,scripts,guides,youtube_tool_scripts}
LK=/home/neilh/folder_lock.py
KEY=/home/neilh/secure/vault
PY=/home/neilh/venv/bin/python

# --- decrypt sealed dirs to /tmp, copy plaintext sources out ---
for pair in "crypto_research crypto_research" "lean_lab lean_lab_full" "prime_video prime_video_full"; do
  set -- $pair
  mkdir -p /tmp/dec_$2
  cp -r /home/neilh/$1/. /tmp/dec_$2/ 2>/dev/null || true
  (cd /tmp/dec_$2 && $PY $LK unlock . --keydir $KEY >/dev/null 2>&1) || true
done

# crypto reports (3 were sealed; cert reports already plaintext in live dir)
cp /tmp/dec_crypto_research/crypto_research/*.md $BK/crypto_research/ 2>/dev/null || true
cp /home/neilh/crypto_research/certificates_*.md $BK/crypto_research/ 2>/dev/null || true
ls $BK/crypto_research/

# lean sources (skip .lake — public deps, huge)
cp /tmp/dec_lean_lab_full/LeanLab/*.lean $BK/lean_lab/LeanLab/ 2>/dev/null || true
cp /tmp/dec_lean_lab_full/*.lean /tmp/dec_lean_lab_full/*.json /tmp/dec_lean_lab_full/lakefile* /tmp/dec_lean_lab_full/lean-toolchain /tmp/dec_lean_lab_full/README* $BK/lean_lab_root/ 2>/dev/null || true
ls $BK/lean_lab/LeanLab/ $BK/lean_lab_root/

# prime video: scripts + audio txts + slides + concat (skip rendered segs mp4s)
cp /tmp/dec_prime_video_full/*.py /tmp/dec_prime_video_full/*.sh $BK/prime_video/ 2>/dev/null || true
cp -r /tmp/dec_prime_video_full/audio $BK/prime_video/ 2>/dev/null || true
cp /tmp/dec_prime_video_full/concat.txt /tmp/dec_prime_video_full/thumbnail.png $BK/prime_video/ 2>/dev/null || true
mkdir -p $BK/prime_video/slides && cp /tmp/dec_prime_video_full/slides/*.png $BK/prime_video/slides/ 2>/dev/null || true
ls $BK/prime_video/ | head

# home-dir scripts (our tooling)
cp /home/neilh/*.py /home/neilh/*.sh $BK/scripts/ 2>/dev/null || true
ls $BK/scripts | wc -l

# guides + key files from downloads_archive (plaintext second batch)
cp /home/neilh/downloads_archive/*.md /home/neilh/downloads_archive/*.html /home/neilh/downloads_archive/*.py $BK/guides/ 2>/dev/null || true
cp /home/neilh/downloads_archive/*.lean.txt $BK/guides/ 2>/dev/null || true
ls $BK/guides | wc -l

# youtube-tool: code only, NO secrets/assets
for f in /home/neilh/youtube-tool/*.py; do
  case "$f" in *token*|*secret*|*cred*) ;; *) cp "$f" $BK/youtube_tool_scripts/ ;; esac
done
ls $BK/youtube_tool_scripts | wc -l
echo "=== STAGING DONE ==="
du -sh $BK
