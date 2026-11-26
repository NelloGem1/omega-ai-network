#!/bin/bash
echo "=== http.server 8796 ==="
ps aux | grep -E "http.server|8796" | grep -v grep
ls -l /proc/2453/cwd 2>/dev/null
echo "=== vit running? ==="
ps aux | grep -E "vit_exp|eval_strong|vit_mnist" | grep -v grep
echo "=== science dir? ==="
ls -la /home/neilh/science 2>/dev/null || echo "no science dir"
