"""Tutorbot backend: serves the player, the deck, the audio, and a streaming
chat endpoint backed by Claude.

Run with:  uvicorn app:app --reload --port 8000

NOTE ON PATHS: the app is designed to sit behind an nginx sub-path (e.g.
/tutorbot/). The player page therefore calls the API with RELATIVE paths
('api/chat', 'audio/manifest.json', ...) so everything resolves under
whatever prefix the reverse proxy uses.
"""

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

BASE_DIR = Path(__file__).parent
DECK_DIR = BASE_DIR / "deck"
AUDIO_DIR = BASE_DIR / "audio"
PLAYER_INDEX = BASE_DIR / "player" / "index.html"
NARRATION_JSON = BASE_DIR / "narration.json"
LOGS_DIR = BASE_DIR / "logs"
QUESTIONS_LOG = LOGS_DIR / "questions.jsonl"

CLAUDE_MODEL = "claude-sonnet-5"
MAX_TOKENS = 1000

load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# HTTP Basic Auth (covers every route, including the mounted static files).
# Credentials come from env; default to the shared classroom login.
# ---------------------------------------------------------------------------
BASIC_AUTH_USER = os.environ.get("BASIC_AUTH_USER", "student")
BASIC_AUTH_PASS = os.environ.get("BASIC_AUTH_PASS", "ricebusiness")


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import base64

        header = request.headers.get("Authorization", "")
        ok = False
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[6:]).decode("utf-8")
                user, _, pw = decoded.partition(":")
                ok = secrets.compare_digest(user, BASIC_AUTH_USER) and \
                    secrets.compare_digest(pw, BASIC_AUTH_PASS)
            except Exception:
                ok = False
        if not ok:
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Rice Business Tutorbot"'},
            )
        return await call_next(request)


app = FastAPI(title="Tutorbot")
app.add_middleware(BasicAuthMiddleware)

# ---------------------------------------------------------------------------
# Knowledge base: narration.json, loaded once at startup.
# ---------------------------------------------------------------------------
SLIDES: list = []
if NARRATION_JSON.exists():
    SLIDES = json.loads(NARRATION_JSON.read_text(encoding="utf-8")).get("slides", [])


def build_course_material() -> str:
    """Render the full narration script + slide text, with slide numbers."""
    parts = []
    for s in SLIDES:
        parts.append(
            f"### Slide {s['index']}: {s.get('title') or 'untitled'}\n"
            f"Slide text: {s.get('slide_text') or '(none)'}\n"
            f"Narration: {s.get('narration') or '(no narration)'}"
        )
    return "\n\n".join(parts)


COURSE_MATERIAL = build_course_material()


def build_system_prompt(slide_index: int) -> str:
    current = next((s for s in SLIDES if s["index"] == slide_index), None)
    current_block = ""
    if current is not None:
        current_block = (
            f"The student is currently viewing slide {slide_index}"
            f" ({current.get('title') or 'untitled'}). The narration for that slide is:\n"
            f"\"{current.get('narration') or '(this slide has no narration)'}\""
        )
    else:
        current_block = f"The student is currently viewing slide {slide_index}."

    return f"""You are the course tutor for this session on AI security, part of an \
executive-education course taught by Kerry Back at Rice Business (Jones Graduate School \
of Business, Rice University). The student is watching a narrated slide presentation and \
has paused it to ask you a question.

Here is the full script of the session, slide by slide:

{COURSE_MATERIAL}

{current_block}

Guidelines:
- The script above is your anchor: use its terminology and framing, treat it as the \
record of what the student has already been told, and prefer it when it answers the question.
- You may freely draw on your general knowledge to explain further, give examples, \
define terms, and connect the material to situations the student raises.
- When an answer goes beyond what the session covers, briefly signpost that in a \
natural way (e.g. "the session doesn't cover this, but...") and then answer -- do not refuse.
- Keep answers short and conversational -- a few sentences, as they may be read aloud.
- Do not use markdown formatting, bullet lists, or headers; respond in plain prose."""


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    slide_index: int
    question: str
    history: list[ChatMessage] = []


def log_question(slide_index: int, question: str, answer: str) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "slide_index": slide_index,
        "question": question,
        "answer": answer,
    }
    with QUESTIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not SLIDES:
        raise HTTPException(503, "narration.json not found - run generate_audio.py first")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "ANTHROPIC_API_KEY is not configured")

    import anthropic

    client = anthropic.Anthropic()
    system_prompt = build_system_prompt(req.slide_index)

    messages = [
        {"role": m.role, "content": m.content}
        for m in req.history
        if m.role in ("user", "assistant") and m.content.strip()
    ]
    messages.append({"role": "user", "content": req.question})

    def generate():
        chunks = []
        try:
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    chunks.append(text)
                    yield text
        except Exception as e:  # surface the failure in the chat panel
            msg = f"\n[tutor error: {e}]"
            chunks.append(msg)
            yield msg
        finally:
            log_question(req.slide_index, req.question, "".join(chunks))

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
@app.get("/")
async def index():
    if not PLAYER_INDEX.exists():
        raise HTTPException(404, "player/index.html not found")
    return FileResponse(PLAYER_INDEX)


# check_dir=False lets the server start before deck/ or audio/ exist
# (they can be produced afterwards without a restart).
app.mount("/deck", StaticFiles(directory=DECK_DIR, html=True, check_dir=False), name="deck")
app.mount("/audio", StaticFiles(directory=AUDIO_DIR, check_dir=False), name="audio")
