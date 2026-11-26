#!/bin/bash
set -e
S=/mnt/c/Users/neilh/Downloads/badge_stage
mkdir -p /home/neilh/science
cp "$S/CORPS_ROSTER.md" /home/neilh/science/CORPS_ROSTER.md
cp "$S/CORPS_BADGES.html" /home/neilh/science/CORPS_BADGES.html
cp "$S/BADGE_vit.md" /home/neilh/science_lab/vit/BADGE.md
cp "$S/BADGE_formal.md" /home/neilh/science_lab/formal/BADGE.md
cp /home/neilh/science/CORPS_ROSTER.md /home/neilh/learning/CORPS_ROSTER.md
cp /home/neilh/science/CORPS_BADGES.html /home/neilh/learning/CORPS_BADGES.html
cp /home/neilh/science/CORPS_ROSTER.md "/mnt/c/Users/neilh/Downloads/Learning/science-corps-roster.md"
cp /home/neilh/science/CORPS_BADGES.html "/mnt/c/Users/neilh/Downloads/Learning/science-corps-badges.html"
echo "deployed:"
ls -la /home/neilh/science /home/neilh/science_lab/vit/BADGE.md /home/neilh/science_lab/formal/BADGE.md
ls -la "/mnt/c/Users/neilh/Downloads/Learning/" | grep science
