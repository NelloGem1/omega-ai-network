#!/bin/bash
grep -il "science\|agent" /home/neilh/FLEET_ANATOMY.md /home/neilh/MASTER_SYSTEM.md /home/neilh/BLUEPRINT.md 2>/dev/null
echo ====
grep -i -A3 -B1 "science" /home/neilh/FLEET_ANATOMY.md 2>/dev/null | head -60
echo ====
head -50 /home/neilh/FLEET_ANATOMY.md 2>/dev/null
