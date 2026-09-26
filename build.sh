#!/usr/bin/env bash
# Build the static site for Cloudflare Workers. Run npm ci once first.
set -euo pipefail
cd "$(dirname "$0")"
node build.mjs
du -sh dist
