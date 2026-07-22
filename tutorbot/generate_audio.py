"""Generate per-slide narration audio for the tutorbot player.

Parses deck/5_security.html (a Quarto reveal.js deck), extracts the narration
from each slide's <aside class="notes"> in reveal order, and synthesizes one
MP3 per narrated slide with OpenAI TTS.

Outputs:
  audio/slide-NNN.mp3   one file per slide that has narration (NNN = 0-based
                        reveal slide index, zero-padded to 3 digits)
  audio/manifest.json   list of {"index", "file", "words"} for every slide
  narration.json        {"slides": [{"index", "narration", "slide_text"}, ...]}
                        used by the chat backend as its knowledge base

Usage:
  python3 generate_audio.py --dry-run    # extract + print narration, no API calls
  python3 generate_audio.py              # synthesize missing MP3s
  python3 generate_audio.py --force      # re-synthesize everything
  python3 generate_audio.py --self-test  # run the parser against synthetic HTML
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DECK_HTML = Path(__file__).parent / "deck" / "5_security.html"
AUDIO_DIR = Path(__file__).parent / "audio"
NARRATION_JSON = Path(__file__).parent / "narration.json"

TTS_MODEL = "gpt-4o-mini-tts"   # or "tts-1"
TTS_VOICE = "nova"              # brighter/warmer than "alloy"
TTS_SPEED = 1.0                 # 0.25 - 4.0 (tts-1 only; ignored by gpt-4o-mini-tts)

# Delivery direction for gpt-4o-mini-tts (ignored by tts-1). This is the main
# lever for tone -- edit it to taste and re-run with --force.
TTS_INSTRUCTIONS = (
    "Speak with warm, upbeat enthusiasm, like an engaging lecturer who genuinely "
    "loves this material and wants students to be excited about it. Sound "
    "energetic and encouraging, with lively pacing and natural emphasis on key "
    "ideas -- but stay clear and easy to follow, never rushed or over-the-top."
)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def enumerate_slides(html: str):
    """Return the deck's slides in reveal.js linear order.

    Quarto revealjs normally emits a flat list of <section> elements inside
    <div class="slides">. Some decks nest one level (a top-level <section>
    wrapping child <section>s); in that case reveal treats each child as its
    own slide, so we flatten one level.

    Returns a list of BeautifulSoup <section> tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    slides_div = soup.find("div", class_="slides")
    if slides_div is None:
        raise ValueError("Could not find <div class='slides'> - is this a reveal.js deck?")

    slides = []
    for top in slides_div.find_all("section", recursive=False):
        children = top.find_all("section", recursive=False)
        if children:
            slides.extend(children)
        else:
            slides.append(top)
    return slides


def extract_slide(section) -> dict:
    """Extract narration and visible text from one <section>."""
    narration = ""
    aside = section.find("aside", class_="notes")
    if aside is not None:
        narration = normalize_ws(aside.get_text(" "))
        # Remove the aside so it doesn't leak into slide_text.
        aside.extract()

    slide_text = normalize_ws(section.get_text(" "))
    title = ""
    heading = section.find(re.compile(r"^h[1-6]$"))
    if heading is not None:
        title = normalize_ws(heading.get_text(" "))

    return {"title": title, "narration": narration, "slide_text": slide_text}


def parse_deck(html: str) -> list:
    """Parse deck HTML into [{'index', 'title', 'narration', 'slide_text'}, ...]."""
    out = []
    for i, section in enumerate(enumerate_slides(html)):
        info = extract_slide(section)
        info["index"] = i
        out.append(info)
    return out


# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------
def synthesize(text: str, out_path: Path) -> None:
    """Call OpenAI TTS and write an MP3 to out_path."""
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY
    kwargs = dict(model=TTS_MODEL, voice=TTS_VOICE, input=text, response_format="mp3")
    if TTS_MODEL == "tts-1":
        kwargs["speed"] = TTS_SPEED
    else:
        kwargs["instructions"] = TTS_INSTRUCTIONS
    with client.audio.speech.with_streaming_response.create(**kwargs) as response:
        response.stream_to_file(out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="extract and print narration; write narration.json; no API calls")
    parser.add_argument("--force", action="store_true",
                        help="re-synthesize MP3s even if they already exist")
    parser.add_argument("--self-test", action="store_true",
                        help="run the parser against synthetic HTML and exit")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not DECK_HTML.exists():
        print(f"Deck not found: {DECK_HTML}", file=sys.stderr)
        print("Render the deck first (see README), or run --self-test to check the parser.",
              file=sys.stderr)
        return 1

    slides = parse_deck(DECK_HTML.read_text(encoding="utf-8"))
    total_words = sum(len(s["narration"].split()) for s in slides)
    narrated = [s for s in slides if s["narration"]]

    print(f"Parsed {len(slides)} slides; {len(narrated)} have narration; "
          f"{total_words} narration words total (~{total_words / 150:.0f} min of audio).")

    # narration.json - always written, even in --dry-run.
    NARRATION_JSON.write_text(
        json.dumps({"slides": slides}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {NARRATION_JSON}")

    if args.dry_run:
        for s in slides:
            print(f"\n--- slide {s['index']:03d}  [{s['title'] or 'untitled'}] "
                  f"({len(s['narration'].split())} words)")
            print(s["narration"] or "(no narration)")
        print("\nDry run: no audio generated, no manifest written.")
        return 0

    # Load .env so OPENAI_API_KEY is available.
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / ".env")
    except ImportError:
        pass

    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set (put it in .env). Aborting.", file=sys.stderr)
        return 1

    AUDIO_DIR.mkdir(exist_ok=True)
    manifest = []
    for s in slides:
        entry = {"index": s["index"], "file": None, "words": len(s["narration"].split())}
        if s["narration"]:
            filename = f"slide-{s['index']:03d}.mp3"
            out_path = AUDIO_DIR / filename
            entry["file"] = filename
            if out_path.exists() and not args.force:
                print(f"skip  {filename} (exists)")
            else:
                print(f"tts   {filename} ({entry['words']} words) ...")
                synthesize(s["narration"], out_path)
        manifest.append(entry)

    manifest_path = AUDIO_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")
    return 0


# ---------------------------------------------------------------------------
# Self-test (no deck, no API)
# ---------------------------------------------------------------------------
FLAT_HTML = """
<html><body><div class="reveal"><div class="slides">
  <section id="title-slide"><h1>AI Security</h1><p>Kerry Back</p></section>
  <section id="s1"><h2>Prompt Injection</h2><p>Attacks   embed instructions.</p>
    <aside class="notes">Prompt injection is the top risk. It hides instructions in data.</aside>
  </section>
  <section id="s2"><h2>No Notes Here</h2><p>Body only.</p></section>
</div></div></body></html>
"""

NESTED_HTML = """
<html><body><div class="reveal"><div class="slides">
  <section id="title-slide"><h1>Title</h1></section>
  <section>
    <section id="a"><h2>A</h2><aside class="notes">Notes for A.</aside></section>
    <section id="b"><h2>B</h2><aside class="notes">Notes for B.</aside></section>
  </section>
  <section id="c"><h2>C</h2><aside class="notes">Notes for C.</aside></section>
</div></div></body></html>
"""


def self_test() -> int:
    flat = parse_deck(FLAT_HTML)
    assert len(flat) == 3, f"expected 3 flat slides, got {len(flat)}"
    assert flat[0]["narration"] == "", "title slide should have no narration"
    assert flat[0]["title"] == "AI Security"
    assert flat[1]["narration"].startswith("Prompt injection is the top risk.")
    assert "hides instructions" in flat[1]["narration"]
    assert "Prompt injection is the top risk" not in flat[1]["slide_text"], \
        "notes leaked into slide_text"
    assert "Attacks embed instructions." in flat[1]["slide_text"], "whitespace not normalized"
    assert flat[2]["narration"] == ""

    nested = parse_deck(NESTED_HTML)
    assert len(nested) == 4, f"expected 4 flattened slides, got {len(nested)}"
    assert [s["title"] for s in nested] == ["Title", "A", "B", "C"]
    assert nested[1]["narration"] == "Notes for A."
    assert nested[2]["narration"] == "Notes for B."
    assert nested[3]["narration"] == "Notes for C."

    print("self-test: all assertions passed (flat + one-level-nested decks).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
