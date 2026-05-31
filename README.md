# SNEHA — your private AI companion 👩‍⚕️

SNEHA is a **private AI companion** that runs on your own machine. She owns her
model (a single local file — nothing is fetched at runtime), **reasons before she answers**,
and can **search the web** when a question needs fresh, real-world facts.

Built by **Saagnik Mondal**.

> ⚠️ SNEHA is an AI assistant, not a licensed professional. For serious medical, legal, or
> safety matters, please consult a qualified expert or emergency services.

---

## What makes her tick

- **One model, fully yours** — Mistral-7B-Instruct-v0.3 (a local GGUF). It works forever,
  offline, even if the original upload ever disappears from the internet.
- **Thinks before answering** — you see a brief 💭 *thinking* step, then her answer.
- **Hybrid web access** — offline by default for privacy; she searches the web only when a
  question needs current facts (or when you ask). Toggle it off anytime in the sidebar.
- **Her own knowledge base** — drop `.txt`/`.md` files in `data/` and she'll ground answers
  on them (optional; zero cost when empty).
- **Warm personality** — caring, expressive, with a light touch of wit. Not a scripted bot.
- **Clean chat UI** — ChatGPT-style, with live streaming.

## Requirements

- **Apple Silicon Mac** recommended (Metal GPU). Tested on an **M1 / 8GB RAM**.
- Python 3.9 and the Mistral GGUF model file.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The model path is the `MODEL_PATH` constant at the top of `app_multimodel.py` — point it at
your `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf` file. To use a different model, change
`MODEL_PATH`/`MODEL_LABEL` and the prompt format in `build_prompt`.

## Run

```bash
streamlit run app_multimodel.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## How it works (and why)

SNEHA keeps **one model resident in memory** (loaded once, cached), so every answer is fast.
Everything is offloaded to the **Metal GPU** — essential for usable speed on an M1. A 7B model
at 4-bit with a 4096 context fits the 8GB budget; that's why she uses a 7B rather than an 8B.

When you ask something time-sensitive, she runs a quick web search, reads the results, reasons
over them, and answers — citing what she found.

## Project layout

```
app_multimodel.py   # the whole app (UI + model + reasoning + web + RAG)
data/               # drop .txt/.md files here for SNEHA's private knowledge base
archive/            # the original multi-model version, kept for reference
requirements.txt
```
