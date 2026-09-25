#!/usr/bin/env bash
# usage: gen2.sh NAME MODEL ASPECT "PROMPT" REF1 [REF2]
set -euo pipefail
name=$1 model=$2 aspect=$3 prompt=$4; shift 4
args=(--space aleksei-krasnoperov/cat-room --kind image --model "$model" --param aspect_ratio="$aspect" --prompt "$prompt" --name "$name" --wait --json)
for r in "$@"; do args+=(--ref "$r:reference"); done
out=$(makefx create "${args[@]}")
id=$(echo "$out" | python3 -c "import json,sys;d=json.load(sys.stdin);a=d.get('assets') or [d.get('asset') or d];print(a[0].get('asset_id') or a[0].get('id'))")
makefx download "$id" --space aleksei-krasnoperov/cat-room --out "assets/$name.png" >/dev/null
echo "$name $id"
