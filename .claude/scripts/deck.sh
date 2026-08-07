#!/usr/bin/env bash
# Export one rendered reveal.js deck to PDF with Decktape.
#
#   deck.sh <filename>          e.g. deck.sh 7_ai-for-research
#
# Reads  docs/slides/<stem>.html   (the rendered deck)
# Writes slides/pdf/<stem>.pdf     (the tracked copy, in _quarto.yml resources)
#        docs/slides/pdf/<stem>.pdf (mirror, so the new PDF is live without a
#                                    full re-render; a render refreshes it too)
#
# The extension is optional and ignored: 3, 3.qmd, 3.html and 3.pdf all work,
# as does any unique substring-free stem prefix like the leading number.
#
# Reveal decks are JS-driven and will not export from a file:// URL, so docs/ is
# served over HTTP and Decktape is pointed at that. The whole site has to be
# served rather than docs/slides/, because that is where site_libs/ lives --
# decks served without it come out unstyled.
#
# Requires: decktape, python3, and Chrome/Chromium/Edge.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

SRC_DIR="docs/slides"
OUT_DIR="slides/pdf"
MIRROR_DIR="docs/slides/pdf"
SIZE="1920x1080"   # matches width/height in slides/_metadata.yml

NAME="${1:-}"
[ -n "$NAME" ] || { echo "usage: deck.sh <filename>   e.g. deck.sh 7_ai-for-research"; exit 1; }

command -v decktape >/dev/null 2>&1 || { echo "decktape not found — 'brew install decktape'"; exit 1; }
[ -d "$SRC_DIR" ] || { echo "no $SRC_DIR/ — run 'quarto render' first"; exit 1; }

stem="${NAME%.qmd}"; stem="${stem%.html}"; stem="${stem%.pdf}"
DECK="$SRC_DIR/$stem.html"
if [ ! -f "$DECK" ]; then
  # Fall back to a loose match on the leading number or the name after it.
  MATCHES=()
  while IFS= read -r f; do
    base="$(basename "$f" .html)"
    if [ "${base%%_*}" = "$stem" ] || [ "${base#*_}" = "$stem" ]; then MATCHES+=("$f"); fi
  done < <(find "$SRC_DIR" -maxdepth 1 -name '*.html' | sort)
  case ${#MATCHES[@]} in
    1) DECK="${MATCHES[0]}"; stem="$(basename "$DECK" .html)" ;;
    0) echo "no deck matches '$NAME'. Found in $SRC_DIR/:"
       find "$SRC_DIR" -maxdepth 1 -name '*.html' | sort | while IFS= read -r f; do
         echo "  $(basename "$f" .html)"; done
       exit 1 ;;
    *) echo "'$NAME' is ambiguous — matches:"
       for f in "${MATCHES[@]}"; do echo "  $(basename "$f" .html)"; done
       exit 1 ;;
  esac
fi

# Prefer a system Chrome; Decktape's bundled Chromium is the fallback.
CHROME=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
         "$(command -v google-chrome 2>/dev/null || true)" \
         "$(command -v chromium 2>/dev/null || true)"; do
  [ -n "$c" ] && [ -x "$c" ] && { CHROME="$c"; break; }
done
CHROME_ARG=(); [ -n "$CHROME" ] && CHROME_ARG=(--chrome-path "$CHROME")

PORT="${PORT:-8799}"
python3 -m http.server "$PORT" --directory docs >/dev/null 2>&1 &
SRV=$!; trap 'kill $SRV 2>/dev/null' EXIT
sleep 1

mkdir -p "$OUT_DIR" "$MIRROR_DIR"
echo ">> $DECK"
decktape reveal -s "$SIZE" "${CHROME_ARG[@]}" \
  "http://127.0.0.1:$PORT/slides/$stem.html" "$OUT_DIR/$stem.pdf"
cp "$OUT_DIR/$stem.pdf" "$MIRROR_DIR/$stem.pdf"

echo
echo "wrote $OUT_DIR/$stem.pdf"
echo "mirrored to $MIRROR_DIR/$stem.pdf"
