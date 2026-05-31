# Enabling Google / Microsoft sign-in for SNEHA

Login is **optional**. SNEHA works immediately as a guest, and your chats are saved
locally on this device either way. Signing in with a **real, verified** Google or
Microsoft account (no fake `abc@m` addresses possible) keeps your chats tied to your
account, so they follow you across sessions.

## 1. Install the auth dependency

```bash
source venv/bin/activate
pip install "Authlib>=1.3.2"   # already added to requirements.txt
```

## 2. Create the secrets file

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Generate a cookie secret and paste it into `cookie_secret`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 3. Register an OAuth app (do at least one)

**Google** — https://console.cloud.google.com/apis/credentials
1. *Create credentials → OAuth client ID → Web application.*
2. Under **Authorized redirect URIs** add exactly:
   `http://localhost:8501/oauth2callback`
3. Copy the **Client ID** and **Client secret** into `[auth.google]` in `secrets.toml`.

**Microsoft** — https://portal.azure.com → *Microsoft Entra ID → App registrations → New registration*
1. Supported account types: choose "personal + work/school" if you want gmail-style personal accounts too.
2. Add a **Web** redirect URI: `http://localhost:8501/oauth2callback`
3. Under *Certificates & secrets* create a **client secret**.
4. Copy the **Application (client) ID** and the secret value into `[auth.microsoft]`.

> The `redirect_uri` must match your run port. If you run on a different port
> (e.g. `--server.port 8533`), use `http://localhost:8533/oauth2callback` everywhere.

## 4. Run

```bash
streamlit run app_multimodel.py
```

The sidebar will show **Google** and **Microsoft** buttons. After you sign in, your
email appears under *Account*, and your conversations are stored per account.

## Notes
- `.streamlit/secrets.toml` and the `chats/` folder are gitignored — never commit them.
- Only the providers you fill in will work; the other button will simply show a
  "not configured" note.
