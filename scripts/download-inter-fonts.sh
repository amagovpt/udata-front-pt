#!/usr/bin/env bash
set -euo pipefail

# Downloads Inter font TTF files from the Google Fonts GitHub repository
# into `udata_front/theme/gouvfr/assets/fonts`.
# Usage: ./scripts/download-inter-fonts.sh

OUT_DIR="$(dirname "$0")/../udata_front/theme/gouvfr/assets/fonts"
mkdir -p "$OUT_DIR"

BASE_URL="https://raw.githubusercontent.com/google/fonts/main/ofl/inter"

# The Google Fonts repository provides variable fonts with bracketed names;
# download the two variable TTFs and save them with simpler names locally.
FILES=(
  "Inter%5Bopsz%2Cwght%5D.ttf:Inter-Variable.ttf"
  "Inter-Italic%5Bopsz%2Cwght%5D.ttf:Inter-VariableItalic.ttf"
)

echo "Downloading Inter fonts to: $OUT_DIR"
for entry in "${FILES[@]}"; do
  # entry format: remote_name:local_name
  remote_name="${entry%%:*}"
  local_name="${entry##*:}"
  url="$BASE_URL/$remote_name"
  dest="$OUT_DIR/$local_name"
  if curl -fSL -o "$dest" "$url"; then
    echo "Downloaded $local_name (from $remote_name)"
  else
    echo "Warning: failed to download $remote_name from $url"
    rm -f "$dest" || true
  fi
done

# Convert downloaded TTF -> WOFF2 when possible for better web performance.
if command -v woff2_compress >/dev/null 2>&1; then
  echo "Converting .ttf -> .woff2 using woff2_compress"
  for ttf in "$OUT_DIR"/*.ttf; do
    [ -f "$ttf" ] || continue
    woff2_compress "$ttf" && echo "Converted: $(basename "$ttf") -> $(basename "${ttf%.ttf}.woff2")"
  done
else
  echo "woff2_compress not found; skipping conversion. Install the 'woff2' package to enable (.e.g apt install woff2)"
fi

# Try to generate .woff as well (fallback). Prefer native ttf2woff, else try npx ttf2woff if available.
if command -v ttf2woff >/dev/null 2>&1; then
  echo "Converting .ttf -> .woff using ttf2woff"
  for ttf in "$OUT_DIR"/*.ttf; do
    [ -f "$ttf" ] || continue
    out="${ttf%.ttf}.woff"
    if ttf2woff "$ttf" "$out"; then
      echo "Converted: $(basename "$ttf") -> $(basename "$out")"
    else
      echo "Warning: failed to convert $ttf to woff with ttf2woff"
    fi
  done
elif command -v npx >/dev/null 2>&1; then
  echo "ttf2woff not found; attempting conversion via 'npx ttf2woff'"
  for ttf in "$OUT_DIR"/*.ttf; do
    [ -f "$ttf" ] || continue
    out="${ttf%.ttf}.woff"
    if npx --yes ttf2woff "$ttf" > "$out" 2>/dev/null; then
      echo "Converted: $(basename "$ttf") -> $(basename "$out") (via npx)"
    else
      echo "Warning: failed to convert $ttf to woff via npx"
      rm -f "$out" || true
    fi
  done
else
  echo "No woff converter (ttf2woff or npx) found; skipping .woff conversion"
fi

echo "Done. You may want to run your build process to regenerate compiled CSS assets."
