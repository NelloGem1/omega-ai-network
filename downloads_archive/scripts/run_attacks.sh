#!/bin/bash
cd /home/neilh/science_lab/vit
for t in fm_vit_tiny_112 fm_vit_tiny_112_b cifar_vit_tiny_112 var_vitsmall_112 var_vit224_tiny cifar_cnn; do
  /home/neilh/venv/bin/python vit_exp.py attack --tag  --eps 0.3 --n 1000
done
