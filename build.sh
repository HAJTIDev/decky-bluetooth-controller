#!/bin/bash
# build.sh

# Build frontend
npm run build

# Package plugin
mkdir -p out
cp -r dist package.json plugin.json main.py backend.py assets/ out/
cp requirements.txt out/

echo "Plugin built in 'out/' directory"