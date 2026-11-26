#!/bin/bash
echo "=== vit results ==="
ls -la /home/neilh/science_lab/vit/results /home/neilh/science_lab/vit/data 2>/dev/null | head -30
tail -20 /home/neilh/science_lab/vit/make_plots.py 2>/dev/null | head -5
echo "=== formal ==="
ls -la /home/neilh/science_lab/formal/; head -30 /home/neilh/science_lab/formal/automata.py
echo "=== DIGEST search ==="
find /home/neilh -maxdepth 3 -iname "*DIGEST*" -o -iname "*digest*" 2>/dev/null | head
echo "=== science DESIGN ==="
head -40 /home/neilh/gh_backup/science/DESIGN.md 2>/dev/null
echo "=== recent mtimes in science_lab ==="
ls -lt /home/neilh/science_lab/*/ | head -40
