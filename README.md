# SNEHA — Your Private AI Companion 👩‍⚕️

SNEHA (v3.0 - *SNEHA Solo*) is a **fully private, locally-hosted AI companion** that runs entirely on your own machine. Designed with a warm, empathetic, and highly capable persona, she reasons through problems, grounds her answers in your private documents, and searches the web only when fresh, real-world facts are needed.

Built by **Saagnik Mondal**.

> ⚠️ **Disclaimer:** SNEHA is an AI assistant, not a licensed medical professional. For serious medical, legal, or safety matters, please consult a qualified expert or emergency services.

---

## 🌟 Key Features

- **100% Private & Local**: She runs off a single local GGUF model file. Nothing is sent to the cloud, and she continues to work offline forever.
- **Apple Silicon Optimized**: Fully offloads model computation to the Metal GPU. A 7B model at 4-bit quantization fits perfectly within an 8GB Unified Memory budget, making her blazing fast on M1/M2/M3 Macs.
- **Hybrid Web Access**: While fully offline by default for privacy, SNEHA can intelligently query the web (via DuckDuckGo) when you ask for current events, weather, or real-time facts. You can toggle this off anytime in the sidebar.
- **Personal Knowledge Base (RAG)**: Simply drop `.txt` or `.md` files into the `data/` folder. SNEHA will embed them locally using `sentence-transformers` and ground her answers in your personal data.
- **Warm & Grounded Persona**: Unlike generic AI models, SNEHA is tuned to be emotionally intelligent, practical, and heavily grounded in everyday Indian context.
- **Clean Chat UI**: A beautiful, minimalist, ChatGPT-style interface built on Streamlit, featuring live text streaming, animated "thinking" states, and persistent chat history.
- **Persistent Accounts**: Supports guest mode (local saving) as well as optional Google/Microsoft OAuth for authenticated users.

## ⚙️ Requirements

- **Hardware**: Apple Silicon Mac (M1/M2/M3) highly recommended for Metal GPU acceleration. Tested on a base M1 with 8GB RAM.
- **Software**: Python 3.9+
- **Model**: `Mistral-7B-Instruct-v0.3` (specifically the `Q4_K_M.gguf` quantized version).

## 🚀 Getting Started

### 1. Download the Model
Download the `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf` model from Hugging Face or LM Studio. 
Open `app_multimodel.py` and update the `MODEL_PATH` constant at the top of the file to point to where you saved your `.gguf` file:
```python
MODEL_PATH = "/path/to/your/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
```

### 2. Install Dependencies
Open your terminal and set up a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run SNEHA
Launch the Streamlit application:
```bash
streamlit run app_multimodel.py
```
Then, open the URL provided in your terminal (usually `http://localhost:8501`) to start chatting!

## 📁 Project Structure

```text
├── app_multimodel.py      # Core application (UI, LLM routing, RAG, Web Search)
├── data/                  # Drop .txt/.md files here for SNEHA's private knowledge base
├── chats/                 # Automatically generated to store user chat histories locally
├── archive/               # Legacy multi-model versions kept for reference
├── requirements.txt       # Python dependencies
└── .gitignore             # Secured to prevent leaking local models or secrets
```

## 🧠 How SNEHA Thinks

SNEHA keeps **one model resident in memory** (loaded once and cached by Streamlit). This ensures that every response is nearly instantaneous without the overhead of reloading the model weights into the GPU for every single question. 

When you ask a complex question, SNEHA transparently:
1. Determines if the question requires live internet access.
2. Checks your `data/` folder for any relevant personal context.
3. Assembles a dynamic prompt featuring your conversation history, the system persona, and any retrieved web/document context.
4. Streams the answer back to you in real-time, completely scrubbing any unnecessary technical boilerplate.
