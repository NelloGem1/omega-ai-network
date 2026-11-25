#!/bin/bash
set -e
cd /home/neilh/prime_video/audio
/home/neilh/.local/bin/edge-tts --voice en-US-ChristopherNeural --file seg_10.txt --write-media seg_10.mp3
ffprobe -v quiet -show_entries format=duration -of csv=p=0 seg_10.mp3
# rebuild assemble script for 14 segs
cat > /home/neilh/assemble14.sh <<'EOF'
#!/bin/bash
set -e
cd /home/neilh/prime_video
mkdir -p segs
for i in $(seq -w 1 14); do
  d=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 audio/seg_${i}.mp3)
  dur=$(echo "$d + 0.5" | bc)
  ffmpeg -y -v error -loop 1 -framerate 30 -i slides/s${i}_*.png \
    -i audio/seg_${i}.mp3 \
    -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -t $dur \
    -c:a aac -b:a 192k -shortest segs/seg_${i}.mp4
done
for i in $(seq -w 1 14); do echo "file 'segs/seg_${i}.mp4'"; done > concat.txt
ffmpeg -y -v error -f concat -safe 0 -i concat.txt -c copy prime_discovery.mp4
ffprobe -v quiet -show_entries format=duration -of csv=p=0 prime_discovery.mp4
EOF
chmod +x /home/neilh/assemble14.sh
# rebuild only segs 10-14 (01-09 unchanged)
for i in 10 11 12 13 14; do
  d=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 audio/seg_${i}.mp3)
  dur=$(echo "$d + 0.5" | bc)
  ffmpeg -y -v error -loop 1 -framerate 30 -i slides/s${i}_*.png \
    -i audio/seg_${i}.mp3 \
    -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -t $dur \
    -c:a aac -b:a 192k -shortest segs/seg_${i}.mp4
  echo "reseg $i done"
done
for i in $(seq -w 1 14); do echo "file 'segs/seg_${i}.mp4'"; done > /home/neilh/prime_video/concat.txt
ffmpeg -y -v error -f concat -safe 0 -i /home/neilh/prime_video/concat.txt -c copy /home/neilh/prime_video/prime_discovery.mp4
ffprobe -v quiet -show_entries format=duration -of csv=p=0 /home/neilh/prime_video/prime_discovery.mp4
