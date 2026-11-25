#!/bin/bash
sed -i \
  -e 's|href="primorial_sieve.html"|href="http://localhost:8796/primorial_sieve.html"|g' \
  -e 's|href="rsa.html"|href="http://localhost:8796/rsa.html"|g' \
  -e 's|href="prime_story.html"|href="http://localhost:8796/prime_story.html"|g' \
  /home/neilh/rsa_folder.html "/mnt/c/Users/neilh/Downloads/rsa_folder.html"
grep -o 'href="[^"]*"' /home/neilh/rsa_folder.html | tail -4
