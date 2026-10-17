#!/usr/bin/env bash
# Renders an HTML file to a PNG with headless Chromium. Usage: render-png.sh in.html out.png [width] [height]
# Uses the Playwright browser cache if present; otherwise set CHROME=/path/to/chrome. Look at the PNG afterwards.
set -euo pipefail
in="$1"; out="$2"; w="${3:-930}"; h="${4:-1600}"
chrome="${CHROME:-$(ls -d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1)}"
[ -x "${chrome:-}" ] || { echo "no Chromium found: set CHROME=, or screenshot the page with a browser tool" >&2; exit 1; }
"$chrome" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size="$w,$h" --screenshot="$out" "file://$(realpath "$in")" >/dev/null 2>&1
[ -s "$out" ] || { echo "render failed" >&2; exit 1; }
# the window is deliberately taller than the page; cut the empty space and leave a margin
if command -v magick >/dev/null; then magick "$out" -trim +repage -bordercolor white -border 24 "$out"; fi
echo "wrote $out"
