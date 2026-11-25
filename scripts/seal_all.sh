#!/bin/bash
for d in crypto_research lean_lab prime_video downloads_archive; do
  echo "=== $d ==="
  /home/neilh/venv/bin/python /home/neilh/folder_lock.py lock "/home/neilh/$d" --keydir /home/neilh/secure/vault 2>&1 | tail -3
done
