#!/bin/bash
cd /home/neilh/science_lab/stats
for s in exp5_infotheory exp6_testing exp6b_fix exp7_randomness exp7b_fix exp8_regression exp8c; do
  echo "##### $s"
  /home/neilh/venv/bin/python "$s.py" 2>&1
done
echo "ALLDONE"
