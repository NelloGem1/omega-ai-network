#!/bin/bash
# Wait for current heavy build to finish, then stop builders until 9AM resume.
export PATH=/home/neilh/venv/bin:$PATH
PY=/home/neilh/venv/bin/python

echo "[$(date +%H:%M:%S)] waiting for heavy_build.lock to free..."
# wait until no ffmpeg factory render is running (max 60 min)
for i in $(seq 1 360); do
  if ! pgrep -f "mm_.*polish|ffmpeg.*mm_|ffmpeg.*ps_" > /dev/null; then
    # also check no whisper/build python children of factories
    if ! pgrep -f "transcribe_one|build_video|movie_pipeline" > /dev/null; then
      break
    fi
  fi
  sleep 10
done
echo "[$(date +%H:%M:%S)] build slot free — stopping builders"
pkill -f "mm_par.py" 2>/dev/null
pkill -f "shorts_factory.py" 2>/dev/null
pkill -f "ps_factory.py" 2>/dev/null
sleep 2
echo "=== remaining factory procs ==="
ps aux | grep -E "mm_par|mm_watch|shorts|ps_" | grep -v grep | grep python
echo "[$(date +%H:%M:%S)] builders stopped. Resume scheduled for 09:00."
