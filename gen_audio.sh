#!/usr/bin/env bash
# usage: gen_audio.sh NAME MODEL "PROMPT" [param=value ...]
set -euo pipefail
name=$1 model=$2 prompt=$3; shift 3
args=(--space aleksei-krasnoperov/cat-room --kind audio --model "$model" --prompt "$prompt" --name "$name" --wait --json)
for p in "$@"; do args+=(--param "$p"); done
out=$(makefx create "${args[@]}")
id=$(echo "$out" | python3 -c "import json,sys;d=json.load(sys.stdin);a=d.get('assets') or [d.get('asset') or d];print(a[0].get('asset_id') or a[0].get('id'))")
makefx download "$id" --space aleksei-krasnoperov/cat-room --out "audio-src/$name" >/dev/null
f=$(ls audio-src/$name* | head -1)
echo "$name $id $f"
