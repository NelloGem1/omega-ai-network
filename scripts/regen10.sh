#!/bin/bash
cd /home/neilh/prime_video/audio
python3 -m edge_tts --voice en-US-ChristopherNeural --file seg_10.txt --write-media seg_10.mp3
ffprobe -v quiet -show_entries format=duration -of csv=p=0 seg_10.mp3
