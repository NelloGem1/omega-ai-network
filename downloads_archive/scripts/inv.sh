#!/bin/bash
for d in /home/neilh/science_lab/*/; do
  echo "=== $d"
  ls "$d" | head -20
done
echo "=== science_research ==="
ls /home/neilh/science_research | head -40
echo "=== learning ==="
ls /home/neilh/learning | head -60
echo "=== science_pages ==="
ls /home/neilh/science_pages | head -60
echo "=== forensic search ==="
find /home/neilh -maxdepth 3 \( -iname "*forensic*" -o -iname "*autopsy*" -o -iname "*coroner*" \) 2>/dev/null | grep -v node_modules | head -40
