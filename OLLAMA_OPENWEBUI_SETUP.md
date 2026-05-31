# SNEHA on Ollama + Open WebUI (the production-grade stack)

This is the recommended architecture: **Ollama serves the model** (fast, Metal-optimized,
keeps the model warm) and **Open WebUI is the ChatGPT-style frontend** (login, persistent
chat history, RAG, web search — all built in). SNEHA keeps her exact identity via an
Ollama *Modelfile*.

On an 8GB Mac we run Open WebUI **without Docker** (Docker Desktop's VM would eat the RAM
the model needs). Everything stays local.

---

## 1. The SNEHA model (already created)

SNEHA is defined in [`ollama/SNEHA.Modelfile`](ollama/SNEHA.Modelfile) on top of the local
`mistral:7b-instruct`. To (re)build it after editing the persona or parameters:

```bash
ollama create sneha -f ollama/SNEHA.Modelfile
ollama run sneha "say hi"     # quick test
```

Keep the model warm between messages (no reload lag):

```bash
launchctl setenv OLLAMA_KEEP_ALIVE 30m   # macOS; persists for the login session
```

## 2. Run Open WebUI

```bash
# one-time install (already done into ./openwebui_venv)
# openwebui_venv/bin/pip install open-webui

openwebui_venv/bin/open-webui serve --port 3000
```

Open http://localhost:3000. The **first account you create becomes the admin.**
Open WebUI auto-detects Ollama at `http://localhost:11434`, so **`sneha` appears in the
model dropdown** — pick it (or set it as the default in *Admin → Settings → Models*).

## 3. Sign in with Google / Microsoft (optional, "valid login")

Open WebUI has OAuth built in. Set environment variables before `open-webui serve`:

```bash
# Google
export ENABLE_OAUTH_SIGNUP=true
export GOOGLE_CLIENT_ID="...apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="..."
# redirect URI to register in Google Console:
#   http://localhost:3000/oauth/google/callback

# Microsoft
export MICROSOFT_CLIENT_ID="..."
export MICROSOFT_CLIENT_SECRET="..."
export MICROSOFT_CLIENT_TENANT_ID="common"   # personal + work accounts
# redirect URI:  http://localhost:3000/oauth/microsoft/callback
```

Because Google/Microsoft verify the account, only **real, valid emails** can sign in — no
fake `abc@m` addresses. Chat history is stored per account in Open WebUI's database.

## 3b. Give SNEHA the real current time (important)

Ollama can't know the live clock on its own. Open WebUI can inject it. Paste SNEHA's
system prompt **with time variables** into Open WebUI so "what's the time?" returns the
actual time, and the India/medicine guidance applies:

1. Go to **Workspace → Models → `sneha` → ✎ Edit** (or create a custom model).
2. In **System Prompt**, paste the contents of
   [`ollama/SNEHA-openwebui-system-prompt.txt`](ollama/SNEHA-openwebui-system-prompt.txt).
   It begins with `Today is {{CURRENT_WEEKDAY}}, {{CURRENT_DATE}} … {{CURRENT_TIME}}` —
   Open WebUI replaces those with the real date/time on every message.
3. Save. Now "time?" → the actual current time; medicine answers use Indian names
   (paracetamol, not acetaminophen).

> The Modelfile already carries this persona for direct `ollama run` use, but only the
> Open WebUI system prompt can fill in the live `{{CURRENT_TIME}}` value.

## 4. Enable web search

*Admin → Settings → Web Search → enable*, choose **DuckDuckGo** (no API key needed).
SNEHA will then search the web when you toggle the web button on a message.

## 5. (Balance both) A faster, smaller SNEHA

The 7B is the quality option (~8 tok/s on this M1). For snappier replies, pull a small
model and make a fast variant — switch between them in the dropdown:

```bash
ollama pull llama3.2:3b
# create a fast SNEHA from the same persona:
sed 's/^FROM .*/FROM llama3.2:3b/' ollama/SNEHA.Modelfile > ollama/SNEHA-fast.Modelfile
ollama create sneha-fast -f ollama/SNEHA-fast.Modelfile
```

`sneha-fast` runs roughly 2–3× faster (smaller model), trading a little depth for speed.

---

## Why this beats the old Streamlit app

| | Old Streamlit app | Ollama + Open WebUI |
|---|---|---|
| Streaming | repaint hacks, laggy | native, smooth |
| Login | hand-rolled | Google/Microsoft built in |
| Chat history | hand-rolled JSON | proper database |
| RAG / web search | hand-rolled | built in |
| Model serving | in-process (reloads) | warm, optimized server |

The Streamlit app remains in the repo (`app_multimodel.py`) as the self-contained version;
this stack is the one to use day-to-day.
