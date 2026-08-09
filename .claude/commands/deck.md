---
description: Export a rendered deck to PDF with the global deck skill
argument-hint: <filename>
allowed-tools: Bash(bash ~/.claude/skills/deck/assets/deck-to-pdf.sh:*)
---

Export the deck `$1` by running, from the project root:

```
bash ~/.claude/skills/deck/assets/deck-to-pdf.sh $1 --root docs --out pdf
```

Those two folders are all this repo contributes. Everything else — the 1440x900pt
page, loose name matching, re-rendering a stale deck, serving the site over HTTP —
lives in the global `deck` skill at `~/.claude/skills/deck/`, so it stays the same
across every repo. Do not reimplement any of it here, and if the export itself
needs fixing, fix it there.

`--root docs` is the rendered site and `--out pdf` is the tracked copy; the script
mirrors each PDF into `docs/pdf/` so it is live on the served site without a full
re-render. `pdf/*.pdf` is in the `resources:` list in `_quarto.yml`, so a later
`quarto render` keeps that copy rather than dropping it. Commit both.

Omit `$1` to export every deck. If the name matches nothing the script lists what
it found; relay that list. Report where the PDF landed and its page count.
