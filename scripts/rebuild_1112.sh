#!/bin/bash
set -e
/home/neilh/venv/bin/python /home/neilh/gen_fixes.py
cd /home/neilh/prime_video
for i in 11 12; do
  d=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 audio/seg_${i}.mp3)
  dur=$(echo "$d + 0.5" | bc)
  ffmpeg -y -v error -loop 1 -framerate 30 -i slides/s${i}_*.png \
    -i audio/seg_${i}.mp3 \
    -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -t $dur \
    -c:a aac -b:a 192k -shortest segs/seg_${i}.mp4
  echo "reseg $i done"
done
ffmpeg -y -v error -f concat -safe 0 -i concat.txt -c copy prime_discovery.mp4
ffprobe -v quiet -show_entries format=duration -of csv=p=0 prime_discovery.mp4
