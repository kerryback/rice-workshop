#!/usr/bin/env bash
# Render the decks, then export each to PDF via the `slides-pdf` skill.
# Re-run after editing any deck.  Requires: quarto, decktape, Chrome.
set -euo pipefail
cd "$(dirname "$0")"

quarto render >/dev/null

SKILL="$HOME/.claude/skills/slides-pdf/assets/reveal-to-pdf.sh"
[ -f "$SKILL" ] || { echo "slides-pdf skill not found at $SKILL"; exit 1; }
bash "$SKILL" docs 'slides-qmd/*.html' slides-pdf 1920x1080
