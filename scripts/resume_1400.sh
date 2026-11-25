#!/bin/bash
# Resume factories at 14:00 local time (postponed from 09:00 — user busy).
export PATH=/home/neilh/venv/bin:$PATH
PY=/home/neilh/venv/bin/python
ASSETS=/home/neilh/youtube-tool/assets
NOW=$(date +%s)
TARGET=$(date -d "today 14:00" +%s)
if [ "$NOW" -ge "$TARGET" ]; then
  TARGET=$(date -d "tomorrow 14:00" +%s)
fi
WAIT=$((TARGET - NOW))
echo "[$(date +%H:%M:%S)] resume-1400 scheduled in ${WAIT}s (at $(date -d @$TARGET '+%H:%M'))"
sleep $WAIT

echo "[$(date +%H:%M:%S)] === RESUMING FACTORIES ==="
cd $ASSETS
pgrep -f mm_par.py >/dev/null || { rm -f mm_par_running.flag; MM_WORKERS=1 nohup $PY mm_par.py > mm_par.log 2>&1 & echo "mm_par started"; }
pgrep -f mm_watch.py >/dev/null || { nohup $PY mm_watch.py > mm_watch.log 2>&1 & echo "mm_watch started"; }
pgrep -f shorts_factory.py >/dev/null || { nohup $PY shorts_factory.py > shorts_factory.log 2>&1 & echo "shorts_factory started"; }
pgrep -f shorts_watch.py >/dev/null || { nohup $PY shorts_watch.py > shorts_watch.log 2>&1 & echo "shorts_watch started"; }
cd /home/neilh/pastel_skies
pgrep -f ps_watch.py >/dev/null || { nohup $PY ps_watch.py > ps_watch.log 2>&1 & echo "ps_watch started"; }
pgrep -f ps_factory.py >/dev/null || { nohup $PY ps_factory.py > ps_factory.log 2>&1 & echo "ps_factory started"; }
echo "[$(date +%H:%M:%S)] resume done"
