#!/bin/bash
echo "=== deep forensic search ==="
find /home/neilh -maxdepth 4 \( -iname "*forensic*" -o -iname "*autopsy*" -o -iname "*coroner*" -o -iname "*death*" -o -iname "*forens*" \) 2>/dev/null | grep -v node_modules | head -50
echo "=== science-related dirs maxdepth2 ==="
find /home/neilh -maxdepth 2 -type d \( -iname "*science*" -o -iname "*research*" -o -iname "*forensic*" -o -iname "*agent*" \) 2>/dev/null | head -50
echo "=== gh_backup/science ==="
ls /home/neilh/gh_backup/science 2>/dev/null | head -40
echo "=== NEED_LOG tail ==="
tail -20 /home/neilh/NEED_LOG.md 2>/dev/null
echo "=== NEED.md ==="
head -40 /home/neilh/NEED.md 2>/dev/null
