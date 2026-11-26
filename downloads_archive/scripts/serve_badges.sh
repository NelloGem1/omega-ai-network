#!/bin/bash
cd /home/neilh/science
# kill any stale server on 8796
pkill -f "http.server 8796" 2>/dev/null || true
nohup /home/neilh/venv/bin/python -m http.server 8796 --bind 0.0.0.0 >/home/neilh/science/http8796.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "%{http_code}" http://localhost:8796/CORPS_BADGES.html
echo " <- status"
ps aux | grep "http.server 8796" | grep -v grep
