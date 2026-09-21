# 🛡️ Enterprise Auditor 2.0

> **Autonomous Enterprise Contract Auditing System** powered by Multi-Agent Courtroom Debate, Hybrid Retrieval (BM25 + Vector), Visual Layout Scanning, 100-Point Safety Scoring, and Executive Memo Generation.

[![Render Deploy](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Key Capabilities

1. **📄 Visual Page & Layout Scanner**
   - Extracts structured pricing/SLA tables using `pdfplumber`.
   - Analyzes execution signature blocks for missing or unilateral signatures using `PyMuPDF`.

2. **🔍 Hybrid Retrieval Engine**
   - Combines BM25 lexical keyword search with high-speed batched vector embeddings (`text-embedding-3-small`) in ChromaDB.
   - Reciprocal Rank Fusion (RRF) for resilient, pinpoint clause retrieval.

3. **⚖️ AI Courtroom Multi-Agent Debate**
   - **Auditor Agent (`gpt-4o-mini`)**: Probes the contract for hidden risks, asymmetries, and non-standard terms.
   - **Skeptic Verifier (`gpt-4o-mini` / `gemini-3.6-flash`)**: Adversarially challenges findings against exact cited text and page references.
   - **Stopping Rules**: Automatic convergence or structured rebuttal when claims are ambiguous.

4. **🎯 3 Plain-English Risk Categories**
   - 🚨 **Deal-Breakers**: Fatal liabilities, extreme unilateral termination, unreasonable indemnities.
   - ⚠️ **Watch Out**: Auto-renewal traps, hidden data retention, vague SLA penalties.
   - 🛡️ **Protections**: Vendor warranties, subcontractor accountability, clear audit rights.

5. **📊 100-Point Mathematical Health Score**
   - Weighted safety rating dynamically computed from verified risks and missing protections.

6. **🗺️ Interactive Grounded Knowledge Graph**
   - Visual entity mapping connecting parties, key obligations, liability caps, and risk nodes.

7. **📝 Executive Audit Memo**
   - Generates downloadable board-ready Markdown memos with redline negotiation suggestions.

---

## 🚀 One-Click Deploy to Render

### Option A: Deploy via Blueprint (`render.yaml`)

1. Fork or push this repository to your GitHub account.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Blueprint**.
4. Connect your GitHub repository.
5. In the Environment Variables prompt:
   - Enter your `OPENAI_API_KEY`.
   - (Optional) Enter your `GEMINI_API_KEY`.
6. Click **Apply**. Render will automatically build and launch your service!

### Option B: Deploy as a Web Service Manually

1. Click **New +** → **Web Service** on Render.
2. Select your repository.
3. Configure the settings:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
4. Add Environment Variables:
   - `OPENAI_API_KEY`: `your_openai_api_key`
   - `OPENAI_MODEL`: `gpt-4o-mini`
   - `PYTHON_VERSION`: `3.11.9`
   - `HOST`: `0.0.0.0`
5. Click **Create Web Service**.

---

## 💻 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/enterprise-auditor.git
cd enterprise-auditor
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and provide your API keys:
```bash
cp .env.example .env
```
Edit `.env`:
```env
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 5. Run the Application
```bash
python run.py
```
Open your browser at:
* **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Running Tests & CLI Scripts

* **Run Test Suite:**
  ```bash
  pytest
  ```

* **Run Audit Pipeline via CLI:**
  ```bash
  python scripts/run_audit.py
  ```

* **Test Document Upload & Audit:**
  ```bash
  python scripts/test_upload.py
  ```

---

## 📁 Repository Structure

```
enterprise-auditor/
├── app/
│   ├── auditing/           # Audit planner, finding generator, missing clauses
│   ├── chunking/           # Section-aware semantic chunking
│   ├── debate/             # LangGraph multi-agent courtroom debate engine
│   ├── graph/              # NetworkX knowledge graph synthesis
│   ├── ingestion/          # PDF loaders, table extractor, signature analyzer
│   ├── pipeline/           # Unified AuditPipeline execution engine
│   ├── reports/            # JSON and Markdown memo report builders
│   ├── retrieval/          # BM25, Chroma vector store, batched embeddings
│   ├── scoring/            # 3-bucket risk scorer & 100-pt health score
│   ├── verification/       # Adversarial Skeptic Verifier
│   └── main.py             # FastAPI REST endpoints and static file mounts
├── data/
│   ├── documents/          # Uploaded contract PDFs
│   ├── indexes/            # Local Chroma vector databases
│   └── reports/            # Generated audit JSON reports & memos
├── frontend/               # Single-page web dashboard (HTML, CSS, JS)
├── scripts/                # CLI test & benchmarking scripts
├── tests/                  # Pytest automated test suite
├── .env.example            # Sanitized environment template
├── .gitignore              # Production gitignore rules
├── render.yaml             # Render cloud deployment blueprint
├── requirements.txt        # Production dependencies
└── run.py                  # Server entrypoint with dynamic port binding
```

---

## 🔒 Security & Privacy

* Contracts uploaded to Enterprise Auditor are processed in your local or private cloud environment.
* API keys and secrets are never committed to version control (`.env` is excluded in `.gitignore`).
* Embeddings and index files are stored in local storage and excluded from public git history.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
