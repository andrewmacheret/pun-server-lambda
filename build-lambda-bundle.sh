#!/usr/bin/env bash
set -e

# Generate Lambda zip file

echo 'Testing ...'
(cd src/lambda && python3 -m unittest)
echo 'Tests passed!'

echo "Zipping files ..."
rm -f lambda-build.zip
(cd src/lambda && zip -q ../../lambda-build.zip main.py)
