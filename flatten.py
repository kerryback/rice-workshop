#!/usr/bin/env python3
"""Quarto post-render hook.

Quarto preserves the input directory structure under output-dir, so files in
slides-qmd/ render to slides-html/slides-qmd/. This lifts them one level up so
the rendered decks land directly in slides-html/ (keeping each deck's _files
directory and images/ alongside it, with relative asset paths intact).
"""
import shutil
from pathlib import Path

src = Path("slides-html/slides-qmd")
dest = Path("slides-html")

if src.is_dir():
    for item in src.iterdir():
        target = dest / item.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.move(str(item), str(target))
    src.rmdir()
    print(f"flattened {src} -> {dest}")
