#!/usr/bin/env bash
# Collect what the site serves into dist/ for Cloudflare Pages.
set -euo pipefail
rm -rf dist && mkdir -p dist
cp index.html dist/
cp -r img dist/img
cp -r audio dist/audio
mkdir -p dist/models/props && cp models/*.glb dist/models/ && cp models/props/*.glb dist/models/props/
cat > dist/_headers <<'H'
/img/*
  Cache-Control: public, max-age=604800
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
H
du -sh dist
