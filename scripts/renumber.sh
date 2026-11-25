#!/bin/bash
set -e
cd /home/neilh/prime_video/audio
for i in 13 12 11 10; do
  j=$((10#$i + 1))
  for ext in mp3 txt; do
    [ -f "seg_${i}.${ext}" ] && mv "seg_${i}.${ext}" "seg_${j}.${ext}"
  done
done
echo "--- audio tail ---"; ls seg_*.mp3 | tail -6
cd /home/neilh/prime_video/slides
mv s13_endcard.png s14_endcard.png
mv s12_formulas.png s13_formulas.png
mv s11_cta.png s12_cta.png
mv s10_loop.png s11_loop.png
echo "--- slides tail ---"; ls s1*.png
