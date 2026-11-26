#!/bin/bash
echo "=== gh_backup/science tree ==="
find /home/neilh/gh_backup/science -maxdepth 3 -type d | head -50
echo "=== gh_backup/science README ==="
head -60 /home/neilh/gh_backup/science/README.md 2>/dev/null
echo "=== sciencelab_tmp ==="
ls -la /home/neilh/sciencelab_tmp 2>/dev/null | head -30
echo "=== REPORT heads ==="
for f in /home/neilh/science_lab/*/REPORT.md; do echo "----- $f"; head -12 "$f"; done
