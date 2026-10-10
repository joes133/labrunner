#!/usr/bin/env bash
# labrunner installer (macOS / Linux)
#
# Note: output strings are ASCII-only for consistency with install.ps1
# and to avoid encoding surprises on terminals with a non-UTF-8 locale.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST="$HOME/.workbuddy/skills/labrunner"

echo "Installing labrunner ..."
echo "  from : $SRC"
echo "  to   : $DST"

if [ -d "$DST" ]; then
    echo "  target exists, will be overwritten"
fi

mkdir -p "$DST"

cp "$SRC/SKILL.md"  "$DST/"
cp "$SRC/README.md" "$DST/"
cp "$SRC/LICENSE"   "$DST/"
cp -R "$SRC/scripts"    "$DST/"
cp -R "$SRC/references" "$DST/"

# .local holds personal config; create it without clobbering existing data
mkdir -p "$DST/.local"
if [ -f "$SRC/.local/profile.example.json" ] && [ ! -f "$DST/.local/profile.json" ]; then
    cp "$SRC/.local/profile.example.json" "$DST/.local/"
fi

echo ""
echo "Installed to: $DST"
echo ""
echo "Next step - install dependencies:"
echo "  pip install pillow python-docx chardet"
echo "  (pywin32 is Windows-only and not needed here)"
echo ""
echo "Done. Note: window capture is Windows-optimized;"
echo "on macOS/Linux capture.py falls back to full-screen capture."
