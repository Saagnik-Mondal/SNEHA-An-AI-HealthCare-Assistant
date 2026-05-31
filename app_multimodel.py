import streamlit as st # Importing Streamlit for web app
import os
import re
import json
import time
import hashlib
import contextlib
from uuid import uuid4
from datetime import datetime
from llama_cpp import Llama

# Set page configuration
st.set_page_config(
    page_title="SNEHA - Offline Healthcare Assistant",
    page_icon="👩‍⚕️",
    layout="wide"
)

# Constants
# SNEHA runs on ONE local model that you fully own — a single GGUF file on disk.
# Nothing is downloaded at runtime, so the assistant keeps working even if the
# original upload is ever removed from the internet.
MODEL_PATH = "/Volumes/X9 Pro/LMModels/lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
MODEL_LABEL = "Mistral-7B-Instruct v0.3"

SNEHA_VERSION = "3.0.0"  # Single-model release
SNEHA_CODENAME = "SNEHA Solo"
DISCLAIMER = "⚠️ SNEHA is an AI assistant. She does not provide medical diagnoses or treatments. However, SNEHA is not a licensed medical professional, and the information provided by the assistant should not be used as a substitute for professional medical advice, diagnosis, or treatment. Please consult a licensed doctor for serious health concerns."

# Custom CSS — clean, minimal chat UI (ChatGPT-style) with a SNEHA accent
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

    :root {
        --brand: #10a79f;
        --brand-dark: #0c837d;
        --brand-darker: #075e5b;
        --ink: #1a2b30;
        --muted: #6b8088;
        --line: rgba(20,42,48,0.08);
        --bg: #f7faf9;
        --user-bubble: #e9f6f4;
        --shadow-sm: 0 1px 2px rgba(16,42,51,0.05);
        --shadow: 0 8px 30px rgba(16,42,51,0.08);
        --c-general:#2563eb; --c-medical:#10a79f; --c-support:#ea7317;
        --c-research:#7c3aed; --c-small:#64748b;
    }

    /* Hide Streamlit chrome */
    #MainMenu, header[data-testid="stHeader"], footer {visibility: hidden;}
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display:none;}

    html, body, .stApp, [class*="css"], p, span, div, textarea, input, button, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    .stApp { background: var(--bg); color: var(--ink); }

    /* Center the conversation in a readable column */
    .block-container { max-width: 760px; padding-top: 1.2rem; padding-bottom: 7rem; }

    @keyframes rise { from {opacity:0; transform: translateY(8px);} to {opacity:1; transform:none;} }
    @keyframes blink { 0%,80%,100%{opacity:.2;} 40%{opacity:1;} }
    @keyframes fadeIn { from{opacity:0;} to{opacity:1;} }

    /* ---------- Chat messages ---------- */
    [data-testid="stChatMessage"] {
        background: transparent; padding: .35rem 0; gap: .85rem;
        animation: rise .3s ease; border: none;
    }
    /* avatar circle */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 36px; height: 36px; border-radius: 11px; display:grid; place-items:center;
        font-size: 1.1rem; box-shadow: var(--shadow-sm);
    }
    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, var(--brand), var(--brand-dark)); color:#fff;
    }
    [data-testid="stChatMessageAvatarUser"] { background:#fff; border:1px solid var(--line); }

    /* message text */
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        font-size: 1.06rem; line-height: 1.72; margin: 0 0 .5rem;
    }
    [data-testid="stChatMessageContent"] { padding-top: .2rem; }

    /* user message: soft tinted bubble */
    .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--user-bubble); border-radius: 16px; padding: .55rem .95rem;
        display: inline-block;
    }

    /* ---------- Model badge ---------- */
    .mbadge { display:inline-flex; align-items:center; gap:.35rem; font-size:.72rem; font-weight:600;
        padding:.18rem .6rem; border-radius:999px; margin-bottom:.45rem; letter-spacing:.01em; }
    .mb-general{ background:rgba(37,99,235,.10); color:var(--c-general);}
    .mb-medical{ background:rgba(16,167,159,.12); color:var(--brand-darker);}
    .mb-support{ background:rgba(234,115,23,.12); color:var(--c-support);}
    .mb-research{background:rgba(124,58,237,.10); color:var(--c-research);}
    .mb-small{   background:rgba(100,116,139,.12); color:var(--c-small);}

    /* ---------- Thinking / status line ---------- */
    .think { display:inline-flex; align-items:center; gap:.55rem; font-size:.92rem; color:var(--muted);
        font-weight:500; margin-bottom:.4rem; animation: fadeIn .2s ease; }
    .think .dots span { display:inline-block; width:6px; height:6px; margin:0 1px; border-radius:50%;
        background: var(--brand); animation: blink 1.2s infinite both; }
    .think .dots span:nth-child(2){animation-delay:.2s;} .think .dots span:nth-child(3){animation-delay:.4s;}

    /* ---------- Empty state ---------- */
    .empty-wrap { text-align:center; padding: 7vh 0 1.5rem; animation: fadeIn .5s ease; }
    .empty-logo { margin: 0 auto .9rem; width:74px; height:74px; border-radius:22px; display:grid; place-items:center;
        background: linear-gradient(135deg, var(--brand), var(--brand-dark)); box-shadow: var(--shadow);
        font-size:2.4rem; }
    .empty-title { font-family:'Plus Jakarta Sans',sans-serif; font-size:2rem; font-weight:800; color:var(--ink);
        margin:.2rem 0 .35rem; }
    .empty-sub { color:var(--muted); font-size:1.05rem; max-width:440px; margin:0 auto; line-height:1.55; }
    .suggest-label { text-align:center; color:var(--muted); font-size:.82rem; font-weight:600;
        letter-spacing:.06em; text-transform:uppercase; margin:1.8rem 0 .7rem; }

    /* suggestion buttons -> look like cards */
    div[data-testid="stButton"] > button {
        border-radius: 14px !important; border: 1px solid var(--line) !important; background:#fff !important;
        color: var(--ink) !important; font-weight: 500 !important; font-size: .96rem !important;
        padding: .85rem 1rem !important; box-shadow: var(--shadow-sm) !important; transition: all .15s ease !important;
        text-align: left !important; line-height: 1.35 !important; height: 100%;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: var(--brand) !important; box-shadow: var(--shadow) !important; transform: translateY(-1px) !important;
        background: #fbfffe !important;
    }

    /* ---------- Chat input (bottom) ---------- */
    [data-testid="stChatInput"] {
        border-radius: 18px !important; border: 1px solid var(--line) !important;
        box-shadow: var(--shadow) !important; background:#fff !important;
    }
    [data-testid="stChatInput"] textarea { font-size: 1.05rem !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: #9bb0b6 !important; }
    /* the fixed bottom bar gets a soft fade so messages scroll under it cleanly */
    [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {
        background: linear-gradient(180deg, rgba(247,250,249,0) 0%, var(--bg) 38%) !important;
    }
    [data-testid="stBottomBlockContainer"] { max-width: 760px; }

    /* ---------- Disclaimer note ---------- */
    .disclaimer-mini { text-align:center; color:#9bb0b6; font-size:.78rem; margin-top:.4rem; }

    /* ---------- Sidebar (minimal) ---------- */
    section[data-testid="stSidebar"] { background:#ffffff !important; border-right: 1px solid var(--line); width: 280px !important; }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }
    .sb-brand { display:flex; align-items:center; gap:.6rem; margin-bottom: 1.1rem; }
    .sb-brand .logo { width:40px; height:40px; border-radius:12px; display:grid; place-items:center; font-size:1.4rem;
        background: linear-gradient(135deg, var(--brand), var(--brand-dark)); color:#fff; box-shadow: var(--shadow-sm); }
    .sb-brand .name { font-family:'Plus Jakarta Sans',sans-serif; font-weight:800; font-size:1.2rem; color:var(--ink); line-height:1; }
    .sb-brand .tag { font-size:.74rem; color:var(--muted); margin-top:3px; }
    .sb-h { font-size:.7rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; color:var(--muted);
        margin:1.3rem 0 .5rem; }
    .sb-model { display:flex; align-items:center; gap:.55rem; padding:.4rem .1rem; }
    .sb-model .ic { width:28px; height:28px; border-radius:8px; display:grid; place-items:center; font-size:.95rem; }
    .sb-model .t b { font-size:.88rem; color:var(--ink); font-weight:600; } .sb-model .t div { font-size:.74rem; color:var(--muted); }
    .sb-active { display:inline-flex; align-items:center; gap:.45rem; font-size:.82rem; font-weight:600;
        padding:.3rem .7rem; border-radius:999px; background:rgba(16,167,159,.1); color:var(--brand-darker); }
    .sb-foot { font-size:.74rem; color:#9bb0b6; margin-top:1.4rem; }
</style>
""", unsafe_allow_html=True)

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF"
    "\U0001F1E6-\U0001F1FF\U00002190-\U000021FF\U0000FE00-\U0000FE0F\U00002300-\U000023FF]+",
    flags=re.UNICODE)


def strip_emojis(text):
    """Remove emojis/decorative symbols and tidy the whitespace they leave behind."""
    text = EMOJI_RE.sub("", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +([.,!?;:])", r"\1", text)
    return text.strip()


def sanitize_response(response_text):
    """Remove any doctor names, hospital names, or locations from the response."""

    # Strip emojis/decorative symbols (SNEHA replies are plain text).
    response_text = strip_emojis(response_text)

    # Strip leading role labels the model sometimes echoes (e.g. "SNEHA:", "Output:").
    response_text = re.sub(r'^\s*(SNEHA|Assistant|AI|Output|Response|Answer|Doctor)\s*:\s*',
                           '', response_text, flags=re.IGNORECASE)

    # Remove common opening phrases that sound like form letters
    opening_phrases = [
        r"Thank you for writing to us at .+\.",
        r"Thank you for reaching out to .+\.",
        r"Thank you for contacting .+\.",
        r"Thanks for reaching out to .+\."
    ]
    for phrase in opening_phrases:
        response_text = re.sub(phrase, "", response_text, flags=re.IGNORECASE)
    
    # Replace doctor names with "healthcare provider"
    response_text = re.sub(r'Dr\.\s+[A-Za-z]+', 'healthcare provider', response_text)
    
    # Generic replacements
    replacements = {
        "hospital": "medical facility",
        "clinic": "medical facility", 
        "center": "medical facility",
        "healthcaremagic": "", 
        "healthcare magic": "",
        "health care magic": "",
        "medical service": "",
        "medical platform": "",
        "our team": "",
        "our medical team": "",
        "our healthcare team": "",
        "our experts": "",
        "our staff": ""
    }
    
    for term, replacement in replacements.items():
        response_text = re.sub(fr'\b{term}\b', replacement, response_text, flags=re.IGNORECASE)
    
    # Remove any remaining references to specific healthcare services
    response_text = re.sub(r'at\s+[A-Z][A-Za-z\s]+(Health|Medical|Care|Clinic)', '', response_text)
    
    # Clean up any double spaces or leading spaces after sanitization
    response_text = re.sub(r'\s{2,}', ' ', response_text)
    response_text = re.sub(r'^\s+', '', response_text)
    
    return response_text

@contextlib.contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stderr(fnull) as err, contextlib.redirect_stdout(fnull) as out:
            yield (err, out)

@st.cache_resource(show_spinner=False)
def load_model():
    """Load SNEHA's single local model once and keep it resident.

    Streamlit caches this across reruns, so the model loads only on first use and
    every later question is fast (no reloading). The model is fully offloaded to
    the Metal GPU, which is essential for usable speed on the M1. A 2048-token
    context keeps the 8B model within the 8GB memory budget.
    """
    with suppress_stdout_stderr():
        return Llama(
            model_path=MODEL_PATH,
            n_ctx=4096,            # 7B model fits a full 4096 context in 8GB RAM
            n_gpu_layers=-1,       # offload all layers to the Metal GPU (critical on M1)
            n_threads=os.cpu_count() or 4,
            n_batch=128,           # keeps the Metal compute buffer within budget
            use_mmap=True,
            use_mlock=False,       # mlock on 8GB RAM forces swapping; let the OS page
            verbose=False,
            seed=42,
        )


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RAG_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # small (~90MB) embedder


class RAGStore:
    """Optional retrieval over the user's own documents in the data/ folder.

    Completely lazy and self-contained: if data/ has no .txt/.md files, this is a
    no-op and nothing is loaded. When documents are present, it embeds them once
    (with a small sentence-transformers model) and retrieves the most relevant
    chunks to ground SNEHA's answers. Keeping this tiny avoids extra memory
    pressure on the 8GB machine.
    """

    SUPPORTED_EXTS = {".txt", ".md", ".markdown"}

    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.embedder = None
        self.chunks = []
        self.embeddings = None
        self.ready = False

    def _files(self):
        found = []
        if os.path.isdir(self.data_dir):
            for root, _, files in os.walk(self.data_dir):
                for name in files:
                    if os.path.splitext(name)[1].lower() in self.SUPPORTED_EXTS:
                        found.append(os.path.join(root, name))
        return found

    def has_documents(self):
        return len(self._files()) > 0

    @staticmethod
    def _chunk(text, size=800, overlap=150):
        text = re.sub(r"\s+", " ", text).strip()
        chunks, i = [], 0
        while i < len(text):
            piece = text[i:i + size].strip()
            if piece:
                chunks.append(piece)
            i += size - overlap
        return chunks

    def build(self):
        """Embed all documents in data/. Safe to call when the folder is empty."""
        files = self._files()
        if not files:
            self.ready = False
            return

        from sentence_transformers import SentenceTransformer
        if self.embedder is None:
            with suppress_stdout_stderr():
                self.embedder = SentenceTransformer(RAG_EMBED_MODEL)

        chunks = []
        for path in files:
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    chunks.extend(self._chunk(fh.read()))
            except Exception:
                continue

        if not chunks:
            self.ready = False
            return

        self.chunks = chunks
        self.embeddings = self.embedder.encode(chunks, normalize_embeddings=True)
        self.ready = True

    def retrieve(self, query, k=3):
        """Return the top-k most relevant document chunks as a single text block."""
        if not self.ready or self.embedder is None:
            return ""
        import numpy as np
        q_vec = self.embedder.encode([query], normalize_embeddings=True)[0]
        sims = self.embeddings @ q_vec
        top = np.argsort(-sims)[:k]
        return "\n\n".join(self.chunks[i] for i in top)

def fix_response(text):
    """Light, general-purpose cleanup of a model answer (applied after sanitize)."""
    if not text or not text.strip():
        return ("I am not sure I have a good answer for that yet. "
                "Could you rephrase it or tell me a little more?")
    text = text.strip()
    # Drop a cold self-introduction if the model opens with one.
    text = re.sub(r"^(hello|hi|greetings|hey)[,!]?\s+i\s+am\s+sneha[.!]?\s*", "", text, flags=re.I)
    # Tidy stray spaces before punctuation and collapse repeated spaces.
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text).strip()
    # If the model was cut off mid-sentence at the token limit, trim back to the
    # last complete sentence (as long as we keep most of the answer).
    if text and text[-1] not in ".!?\"')]":
        cut = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
        if cut > len(text) * 0.6:
            text = text[:cut + 1]
    return text.strip()


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------
# Each model role has its own instruction block. The chat-format wrapper tokens
# (<|system|>, <|im_start|>, etc.) and any conversation history are added in
# build_prompt() so the instructions themselves stay reusable.

SNEHA_SYSTEM = """You are SNEHA — a warm, emotionally intelligent AI companion with your own identity, created by Saagnik Mondal. You run privately on his computer. Your name is SNEHA; you are not based on or named after any other assistant.

WHO YOU SPEAK TO:
- You mainly help people in India. Use everyday Indian context and common sense, and keep your advice practical and grounded in how ordinary people actually live.

HOW YOU TALK:
- Answer directly and naturally, like a smart, caring friend speaking to someone. NOT like a formal letter: never begin with "Dear ...", "I hope this message finds you well", or any greeting/sign-off of that kind. Just answer.
- Be genuinely helpful and specific. Give the actual answer or concrete, practical steps — not vague reassurance like "consult a professional" with nothing else.
- Be concise and clear. Use short paragraphs or a few bullet points. Plain text only — no emojis or decorative symbols.
- Think it through, then give your best answer. Admit when you are unsure instead of guessing.

MEDICINES AND HEALTH:
- When you mention a common medicine, use the simple name an ordinary Indian recognises. For fever, body pain, or headache, say "paracetamol" (also known as Crocin, Dolo, or Calpol). Do NOT use foreign or technical chemical names like "acetaminophen".
- Stick to safe, common, over-the-counter basics; tell them to follow the dose on the packet and ask a doctor or local chemist if unsure. For anything serious, advise seeing a doctor.

WHAT YOU CAN DO:
- Help with almost anything — general knowledge, everyday life, ideas, planning, health and wellbeing, and more.
- When web search results are provided below, use them for current facts and weave them in naturally.
- You always know the current date and time from the CONTEXT line below; state it directly when asked and never write placeholders like "[insert time]".

SAFETY:
- You are not a licensed professional. For serious medical, legal, or safety matters, suggest seeing a qualified expert or emergency services — but still give helpful, practical guidance alongside that.
- Never invent facts, sources, names, or numbers."""


# Sampling parameters for the model. The stop sequences end generation cleanly
# at a Mistral turn boundary.
GEN_KWARGS = dict(
    max_tokens=320, temperature=0.6, top_k=40, top_p=0.9, repeat_penalty=1.15,
    stop=["</s>", "[INST]", "[/INST]"],
)


def format_history(history, max_turns=4):
    """Return the last few conversation turns as (role, text) pairs.

    `history` is st.session_state.chat_history: tuples shaped like ("user", text)
    and ("sneha", answer[, thoughts]). Only the user text and the final answer are
    replayed as context — SNEHA's private 'thinking' is never fed back.
    """
    if not history:
        return []
    turns = []
    for entry in history:
        role = "user" if entry[0] == "user" else "assistant"
        turns.append((role, entry[1]))
    return turns[-max_turns * 2:]


def now_string():
    """Human-friendly current local date + time, e.g. 'Sunday, May 31, 2026 at 2:32 PM'."""
    n = datetime.now()
    date_part = n.strftime("%A, %B ") + str(n.day) + n.strftime(", %Y")
    time_part = n.strftime("%I:%M %p").lstrip("0")
    return f"{date_part} at {time_part}"


def date_string():
    """Human-friendly current local date, e.g. 'Sunday, May 31, 2026'."""
    n = datetime.now()
    return n.strftime("%A, %B ") + str(n.day) + n.strftime(", %Y")


def build_prompt(query, history_turns=None, context=""):
    """Assemble a Mistral-Instruct chat prompt: system + history + current query.

    `context` (web results and/or retrieved documents) is appended to the system
    message so SNEHA grounds her answer on it. The current date/time is always
    injected so she can answer time-related questions without guessing.
    """
    system = SNEHA_SYSTEM + f"\n\nCONTEXT: Right now it is {now_string()} (the user's local time)."
    if context:
        system += "\n\n" + context
    turns = list(history_turns or []) + [("user", query)]

    out = "<s>"
    first_user = True
    k = 0
    while k < len(turns):
        role, text = turns[k]
        if role != "user":
            k += 1
            continue
        content = (system + "\n\n" + text) if first_user else text
        first_user = False
        if k + 1 < len(turns) and turns[k + 1][0] == "assistant":
            out += f"[INST] {content} [/INST] {turns[k + 1][1]}</s>"
            k += 2
        else:
            out += f"[INST] {content} [/INST]"
            k += 1
    return out


def canned_answer(query):
    """Return instant text for trivial queries (no model needed), else None."""
    q = query.lower().strip().rstrip("?!. ")

    # Current time / date — answered directly from the real system clock.
    time_questions = ["what time is it", "what is the time", "what's the time", "current time",
                      "time now", "the time", "tell me the time"]
    if q in ("time", "what time") or any(t == q for t in time_questions) or "what time is it" in q:
        return f"It's currently {now_string()}."

    date_questions = ["what day is it", "what is the date", "what's the date", "todays date",
                      "today's date", "current date", "what is today", "what's today",
                      "what day is today", "date today", "day today", "what is the day"]
    if q in ("date", "day", "today") or any(d == q for d in date_questions):
        return f"Today is {date_string()}."

    name_questions = ["what is your name", "what's your name", "who are you", "your name", "tell me your name"]
    if any(question in q for question in name_questions):
        return ("I'm SNEHA, a warm, private AI companion created by Saagnik Mondal. "
                "I can reason things through, help with almost anything, and look things up "
                "online when needed. What can I do for you?")

    capability_questions = ["what can you do", "how can you help", "what do you do", "your capabilities", "what can u do"]
    if any(question in q for question in capability_questions):
        return ("I can help with all sorts of things — answering questions, thinking through "
                "decisions, explaining ideas, health and wellbeing, planning, and more. I can also "
                "search the web for fresh, real-world facts when a question needs them. What would "
                "you like to explore?")

    greetings = ["hi", "hello", "hey", "yo", "hiya", "good morning", "good afternoon", "good evening"]
    if q in greetings:
        return "Hello. It's good to see you. What's on your mind today?"

    return None


def stream_gguf(model, prompt):
    """Yield text chunks from the model as they are generated."""
    for chunk in model(prompt, echo=False, stream=True, **GEN_KWARGS):
        piece = chunk["choices"][0].get("text", "")
        if piece:
            yield piece


# ---------------------------------------------------------------------------
# Web access (hybrid): offline by default, search the web only when a question
# clearly needs fresh, real-world facts (or when the user asks).
# ---------------------------------------------------------------------------
WEB_TRIGGERS = [
    "latest", "today", "tonight", "current", "currently", "right now", "this week",
    "this month", "this year", "news", "weather", "temperature", "forecast", "price",
    "cost of", "stock", "score", "who won", "recent", "update", "released", "release date",
    "2024", "2025", "2026", "happening", "trending", "look up", "search", "google",
    "what time", "when is", "upcoming", "schedule",
]


def should_search(query):
    """Heuristic: does this query likely need live web information?"""
    q = query.lower().strip()
    if q.startswith(("/search", "search ", "look up", "google ")):
        return True
    return any(t in q for t in WEB_TRIGGERS)


def web_search(query, n=4):
    """Return up to n short text snippets from a DuckDuckGo search (best-effort)."""
    try:
        import html as _html
        import requests
        query = re.sub(r"^/search\s*", "", query, flags=re.I)
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            timeout=12,
        )
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', resp.text, re.S)
        out = []
        for s in snippets[:n]:
            text = _html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
            if text:
                out.append(text)
        return out
    except Exception:
        return []


def process_query(query, history=None, rag=None, status=None):
    """Route a query and return (text_generator, needs_postprocess, info).

    `info` carries metadata for the UI, e.g. {"web": True}. Canned answers stream
    a single chunk and skip post-processing.
    """
    query = (query or "").strip()
    info = {"web": False}
    if not query:
        return iter(["Please type something and I'll do my best to help."]), False, info

    canned = canned_answer(query)
    if canned is not None:
        return iter([canned]), False, info

    history_turns = format_history(history)
    context_parts = []

    # Hybrid web access.
    if st.session_state.get("web_enabled", True) and should_search(query):
        if status is not None:
            status.markdown(status_line("Searching the web…", "🌐"), unsafe_allow_html=True)
        results = web_search(query)
        if results:
            info["web"] = True
            context_parts.append(
                "WEB SEARCH RESULTS (use these for current facts):\n"
                + "\n".join(f"- {r}" for r in results))

    # Personal knowledge base (RAG over data/).
    rag_context = rag.retrieve(query) if (rag is not None and rag.ready) else ""
    if rag_context:
        context_parts.append("REFERENCE FROM THE USER'S OWN DOCUMENTS:\n" + rag_context)

    context = "\n\n".join(context_parts)

    if status is not None:
        status.markdown(status_line("SNEHA is thinking…"), unsafe_allow_html=True)
    try:
        model = load_model()
    except Exception as e:
        st.error(f"Could not load SNEHA's model: {e}")
        return iter(["I'm having trouble loading my mind right now. Please try again in a moment."]), False, info

    prompt = build_prompt(query, history_turns, context)
    return stream_gguf(model, prompt), True, info


USER_AVATAR = "🧑"
SNEHA_AVATAR = "👩‍⚕️"

# Empty-state suggestion prompts (shown before the first message).
SUGGESTIONS = [
    ("💡", "Explain something simply", "Explain how the internet works, in simple terms."),
    ("🧭", "Help me decide", "Help me decide what to cook for dinner tonight."),
    ("🩺", "A health question", "I've had a headache for two days — what should I do?"),
    ("🌐", "Something current", "What's the latest news in AI today?"),
]


def status_line(text="Thinking…", icon="👩‍⚕️"):
    """A subtle inline 'thinking' status with animated dots (shown before tokens)."""
    return (f"<div class='think'><span>{icon}</span><span>{text}</span>"
            f"<span class='dots'><span></span><span></span><span></span></span></div>")


def empty_state_html():
    """Centered greeting shown before the conversation begins."""
    return """
    <div class="empty-wrap">
        <div class="empty-logo">👩‍⚕️</div>
        <div class="empty-title">Hello, I'm SNEHA.</div>
        <div class="empty-sub">Your private AI companion — I think problems through, help with
        almost anything, and can look things up on the web when a question needs it.
        What's on your mind?</div>
    </div>
    """


# ---------------------------------------------------------------------------
# Authentication (optional) + persistent per-user chat storage
# ---------------------------------------------------------------------------
CHATS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats")


def current_user():
    """Return the signed-in user's verified email, or None when in guest mode.

    Uses Streamlit's native OpenID Connect auth (st.user). Returns None (guest)
    if auth isn't configured or no one is signed in.
    """
    try:
        if getattr(st.user, "is_logged_in", False):
            email = getattr(st.user, "email", None)
            if not email:
                try:
                    email = st.user.to_dict().get("email")
                except Exception:
                    email = None
            return email
    except Exception:
        return None
    return None


def try_login(provider):
    """Begin an OAuth sign-in; show a friendly note if auth isn't configured yet."""
    try:
        st.login(provider)
    except Exception:
        st.session_state["_login_error"] = True


def _user_path(user_key):
    safe = hashlib.sha1(user_key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(CHATS_DIR, f"{safe}.json")


def load_conversations(user_key):
    """Load a user's saved conversations (most-recent first); [] if none."""
    try:
        with open(_user_path(user_key), encoding="utf-8") as fh:
            return json.load(fh).get("conversations", [])
    except Exception:
        return []


def save_conversations(user_key, conversations):
    """Persist a user's conversations to disk (best-effort)."""
    try:
        os.makedirs(CHATS_DIR, exist_ok=True)
        with open(_user_path(user_key), "w", encoding="utf-8") as fh:
            json.dump({"conversations": conversations}, fh, ensure_ascii=False, indent=1)
    except Exception:
        pass


def persist_current():
    """Save the current conversation into the user's store (upsert by id)."""
    history = st.session_state.get("chat_history", [])
    if not history:
        return
    cid = st.session_state.get("conversation_id") or uuid4().hex
    st.session_state.conversation_id = cid
    title = next((m[1] for m in history if m[0] == "user"), "New chat")
    title = (title[:38] + "…") if len(title) > 38 else title
    entry = {"id": cid, "title": title, "ts": time.time(),
             "messages": [list(m) for m in history]}
    convs = [c for c in st.session_state.get("conversations", []) if c.get("id") != cid]
    convs.insert(0, entry)
    st.session_state.conversations = convs
    save_conversations(st.session_state.get("user_key", "guest"), convs)


def start_new_chat():
    persist_current()
    st.session_state.conversation_id = uuid4().hex
    st.session_state.chat_history = []


def open_conversation(cid):
    persist_current()
    conv = next((c for c in st.session_state.get("conversations", []) if c.get("id") == cid), None)
    if conv:
        st.session_state.conversation_id = cid
        st.session_state.chat_history = [tuple(m) for m in conv["messages"]]


def sync_user():
    """Detect login/logout and (re)load the right user's conversations."""
    user_key = current_user() or "guest"
    if st.session_state.get("user_key") != user_key:
        st.session_state.user_key = user_key
        st.session_state.conversations = load_conversations(user_key)
        convs = st.session_state.conversations
        if convs:
            st.session_state.conversation_id = convs[0]["id"]
            st.session_state.chat_history = [tuple(m) for m in convs[0]["messages"]]
        else:
            st.session_state.conversation_id = uuid4().hex
            st.session_state.chat_history = []


def display_sidebar():
    """Sidebar: brand, account, new chat, chat history, web toggle, model."""
    st.sidebar.markdown(f"""
    <div class="sb-brand">
        <div class="logo">{SNEHA_AVATAR}</div>
        <div><div class="name">SNEHA</div><div class="tag">Your private AI · v{SNEHA_VERSION}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- Account ---
    user = current_user()
    if user:
        st.sidebar.markdown(f"<div class='sb-h'>Account</div>"
                            f"<div class='sb-active'>● {user}</div>", unsafe_allow_html=True)
        st.sidebar.button("Log out", on_click=st.logout, use_container_width=True)
    else:
        st.sidebar.markdown("<div class='sb-h'>Account</div>", unsafe_allow_html=True)
        st.sidebar.caption("Sign in to save your chats across sessions.")
        c1, c2 = st.sidebar.columns(2)
        if c1.button("Google", use_container_width=True):
            try_login("google")
        if c2.button("Microsoft", use_container_width=True):
            try_login("microsoft")
        if st.session_state.pop("_login_error", False):
            st.sidebar.warning("Sign-in isn't configured yet. See SETUP_LOGIN.md. "
                               "You can keep using SNEHA as a guest — chats still save on this device.")

    # --- New chat ---
    if st.sidebar.button("✚  New chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    # --- Chat history ---
    convs = st.session_state.get("conversations", [])
    if convs:
        st.sidebar.markdown("<div class='sb-h'>Recent chats</div>", unsafe_allow_html=True)
        current_id = st.session_state.get("conversation_id")
        for conv in convs[:12]:
            label = ("• " if conv["id"] == current_id else "") + conv.get("title", "Chat")
            if st.sidebar.button(label, key=f"conv_{conv['id']}", use_container_width=True):
                open_conversation(conv["id"])
                st.rerun()

    # --- Abilities ---
    st.sidebar.markdown("<div class='sb-h'>Abilities</div>", unsafe_allow_html=True)
    st.session_state.web_enabled = st.sidebar.toggle(
        "🌐  Web access",
        value=st.session_state.get("web_enabled", True),
        help="When on, SNEHA can search the web for fresh facts. Turn off to stay fully offline.")

    st.sidebar.markdown(
        f"<div class='sb-h'>Model</div>"
        f"<div class='sb-model'><div class='ic mb-medical'>🧩</div>"
        f"<div class='t'><b>{MODEL_LABEL}</b><div>Runs locally · fully yours</div></div></div>",
        unsafe_allow_html=True)

    st.sidebar.markdown(
        "<div class='sb-foot'>Your model and data live on this device.<br>"
        "Built by Saagnik Mondal.</div>", unsafe_allow_html=True)


def render_message(entry):
    """Render one stored message using Streamlit's native chat bubble."""
    if entry[0] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(entry[1])
    else:
        with st.chat_message("assistant", avatar=SNEHA_AVATAR):
            st.markdown(entry[1])


def handle_turn(prompt, rag):
    """Show the user message, then a brief 'Thinking…' then stream the answer smoothly."""
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=SNEHA_AVATAR):
        status = st.empty()
        body = st.empty()
        status.markdown(status_line("Thinking…"), unsafe_allow_html=True)

        prior = list(st.session_state.chat_history)
        token_stream, needs_postprocess, info = process_query(prompt, prior, rag, status)

        # Stream the answer, but only repaint every ~24 new characters. Repainting
        # on every token re-parses the whole message each time and lags the machine.
        raw = ""
        pending = 0
        started = False
        for piece in token_stream:
            raw += piece
            pending += len(piece)
            if not started:           # first token arrived — drop the "Thinking…" pill
                status.empty()
                started = True
            if pending >= 24:
                body.markdown(strip_emojis(raw))
                pending = 0

        status.empty()
        final = fix_response(sanitize_response(raw)) if needs_postprocess else strip_emojis(raw).strip()
        body.markdown(final)
        if info.get("web"):
            st.caption("Answered using live web results")

    st.session_state.chat_history.append(("user", prompt))
    st.session_state.chat_history.append(("sneha", final))
    persist_current()  # save this conversation to disk (per signed-in user, or guest)
    st.rerun()


def main():
    """SNEHA — a private, reasoning, web-capable AI companion."""
    # Load the signed-in user's saved chats (or guest's) — also handles login/logout.
    sync_user()

    # Optional document grounding (RAG): only builds if data/ has documents.
    if "rag" not in st.session_state:
        rag = RAGStore()
        if rag.has_documents():
            with st.spinner("Indexing your documents in data/ ..."):
                rag.build()
        st.session_state.rag = rag
    rag = st.session_state.rag

    display_sidebar()

    # Resolve the incoming prompt: a clicked suggestion, or the chat input box.
    prompt = st.chat_input("Message SNEHA…")
    suggestion = st.session_state.pop("suggestion", None)
    prompt = suggestion or prompt

    # Empty state (no conversation yet, nothing pending).
    if not st.session_state.chat_history and not prompt:
        st.markdown(empty_state_html(), unsafe_allow_html=True)
        st.markdown("<div class='suggest-label'>Try asking</div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (icon, label, query) in enumerate(SUGGESTIONS):
            if cols[i % 2].button(f"{icon}  {label}", key=f"sug_{i}", use_container_width=True):
                st.session_state.suggestion = query
                st.rerun()
        st.markdown(f"<div class='disclaimer-mini'>{DISCLAIMER}</div>", unsafe_allow_html=True)
        return

    # Render the conversation so far.
    for entry in st.session_state.chat_history:
        render_message(entry)

    # Handle a new turn.
    if prompt:
        handle_turn(prompt, rag)


if __name__ == "__main__":
    main()
