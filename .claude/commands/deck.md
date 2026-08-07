---
description: Export a rendered deck from docs/slides to PDF with Decktape
argument-hint: <filename>
allowed-tools: Bash(bash .claude/scripts/deck.sh:*)
---

Export the deck `$1` to PDF by running, from the project root:

```
bash .claude/scripts/deck.sh $1
```

The script takes `docs/slides/<filename>.html` and writes `slides/pdf/<filename>.pdf`,
mirroring it into `docs/slides/pdf/` so the new PDF is live on the served site
without a full re-render. `slides/pdf/*.pdf` is in the `resources:` list in
`_quarto.yml`, so a later `quarto render` refreshes that copy too.

The extension is optional and the name is matched loosely — `7`, `7_ai-for-research`
and `ai-for-research` all find the same deck. If no argument was given, or the
name matches nothing, the script lists the decks it found; relay that list.

If the deck's HTML is missing or stale, run `quarto render slides/<filename>.qmd`
first, then export. Report where the PDF landed and its page count.
