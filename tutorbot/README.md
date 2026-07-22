# Tutorbot — narrated slides with an AI tutor

A self-paced prototype: a student watches the AI-security session (a Quarto
reveal.js deck) with AI voiceover, and can interrupt at any time to ask a
question. Questions are answered by Claude using the full narration script as
its knowledge base, streamed into a chat panel next to the slides.

## Setup

1. Install dependencies (Python 3.10+) in a virtual environment (a `.venv`
   already exists here if you set this up with Claude; otherwise create one —
   on macOS a plain `pip install` outside a venv is blocked):

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

   Then use `.venv/bin/python3` and `.venv/bin/uvicorn` in the commands below
   (or `source .venv/bin/activate` once per shell).

2. Configure API keys. Copy `.env.example` to `.env` and fill in real values:

   ```bash
   cp .env.example .env
   # edit .env: ANTHROPIC_API_KEY (chat) and OPENAI_API_KEY (TTS)
   ```

   The real `.env` is never committed.

3. The deck. The narrated source and its rendered HTML live in `deck/`
   (`5_security.qmd` -> `5_security.html`). After editing the qmd or its
   narration notes, re-render in place:

   ```bash
   cd deck && quarto render 5_security.qmd
   ```

4. Generate narration and audio. Always dry-run first to eyeball the
   extraction and the cost:

   ```bash
   python3 generate_audio.py --dry-run
   ```

   This prints every slide's narration plus a total word count. Narration is
   spoken at roughly 150 words (~1000 characters) per minute, so the word
   count tells you both the audio length and the TTS cost. It also writes
   `narration.json` (the tutor's knowledge base). Then:

   ```bash
   python3 generate_audio.py          # synthesizes audio/slide-NNN.mp3 + manifest.json
   python3 generate_audio.py --force  # re-synthesize everything
   ```

   The script is idempotent: existing MP3s are skipped unless `--force` is
   given. Slides without narration get no file; the player dwells 4 seconds
   on them and moves on. TTS model and voice are constants at the top of
   `generate_audio.py` (`gpt-4o-mini-tts`, voice `alloy`).

5. Run the server and open the player:

   ```bash
   uvicorn app:app --reload --port 8000
   # open http://localhost:8000/
   ```

## How it works

1. `generate_audio.py` parses the deck's `<aside class="notes">` per slide
   (in reveal.js order) into `narration.json`, and synthesizes one MP3 per
   narrated slide via OpenAI TTS, indexed by slide number in
   `audio/manifest.json`.
2. `player/index.html` embeds the deck in an iframe and drives it through
   reveal.js's postMessage API: on every `slidechanged` it plays that slide's
   MP3, and when the audio ends (autoplay on) it advances to the next slide.
3. Asking a question pauses the audio and POSTs `{slide_index, question,
   history}` to `api/chat`.
4. `app.py` (FastAPI) holds the full narration script in Claude's system
   prompt, tells it which slide the student is on, and streams the answer
   back as plain text into the chat panel. Answers are anchored to the deck's
   script and terminology but may draw on general knowledge, with the tutor
   signposting when it goes beyond what the session covers.
5. Every Q&A is appended to `logs/questions.jsonl`.

All client-side URLs (`api/chat`, `audio/...`, `deck/...`) are relative, so
the app works unchanged behind an nginx sub-path (e.g. `/tutorbot/`). Make
sure the proxied location ends with a slash (`location /tutorbot/ { ... }`)
so relative paths resolve under the prefix.

## Next steps

- Voice input: let the student ask questions by speaking (Web Speech API /
  `SpeechRecognition`) instead of typing.
- Realtime barge-in: switch to a realtime voice model so the student can
  interrupt the narration mid-sentence and get a spoken answer with low
  latency.
- Per-student auth and logging: identify students (e.g. via the LMS), log
  per-student question histories, and surface common questions to the
  instructor.
