---
title: AI Reliability & Risk Auditing System
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# 🛡️ AI Reliability & Risk Auditing System

**Transforming Hallucination Evaluation into Production-Grade Safeguards.**

This system is a deployable AI Safety & Compliance tool built on the [OpenEnv](github.com/openenv) framework. It provides deterministic auditing of LLM-generated responses to identify factual hallucinations, assess risk, and suggest remediation.

---

## 🏁 Submission Status: READY FOR EVALUATION ✅

The environment has been verified and is ready for Hackathon grading.
- **Direct App URL**: `https://AZ-8714-ai-hallucination-auditor.hf.space`
- **Health Check**: Returns `200 OK` with system status.
- **Compliance**: Responds to `/reset`, `/step`, and `/state`.

---

## 🚀 Key Features

*   **Deterministic Auditing**: Reusable engine for consistent safety checks.
*   **Real-time API**: FastAPI service for production integration.
*   **Interactive Dashboard**: Streamlit UI for visual inspection.
*   **Risk Scoring**: Multi-level risk assessment (Critical, High, Medium, Low).
*   **Benchmark Compliant**: STRICTLY preserves all OpenEnv evaluation logic.

---

## 🛠️ Installation & Setup

### Mandatory Environment Variables
Ensure the following are defined in your environment (or added as **Space Secrets** on Hugging Face):
- `API_BASE_URL`: The proxy URL provided by the hackathon.
- `API_KEY`: Your hackathon API key.
- `MODEL_NAME`: The model name (e.g., `gpt-4o`).

#### ☁️ Setting Secrets on Hugging Face
If your project is deployed on a Hugging Face Space:
1. Go to **Settings** > **Variables and Secrets**.
2. Add `API_BASE_URL` and `API_KEY` as **Secrets**.
3. **Restart the Space** to ensure the server picks up the new keys.

## Pre-Submission Validation
Before submitting, run the validation script to check your Space and Docker build.

**For Private Spaces**: Export your Hugging Face token first.
```bash
export HF_TOKEN="hf_..."
chmod +x validate-submission.sh
./validate-submission.sh https://your-space.hf.space
```

### Local Run (Windows)
Simply run the provided batch file to install dependencies, run a test audit, and launch the UI:
```bash
run_audit_system.bat
```

---

## 📊 Evaluation & Compliance (Base Criteria)

*   **HF Space Deploys**: API exposes mandated OpenEnv endpoints.
*   **Structured Logs**: `inference.py` emits logs strictly in `[START]`, `[STEP]`, and `[END]` format.
*   **OpenAI Client**: Uses standard `openai.OpenAI` for all LLM auditing calls.
*   **Infra Specs**: Optimized for vCPU=2, RAM=8GB, < 20min runtime.

---

## 🐳 Docker Deployment
The application supports three modes via the `MODE` environment variable:
- `MODE=BENCHMARK` (Default): `python inference.py`
- `MODE=API`: `server` (Runs the project entry point)
- `MODE=UI`: `streamlit run server/ui.py --server.port 7860`

---

## 📂 Project Structure
- `server/`
    - `app.py`: FastAPI server (OpenEnv compliant)
    - `ui.py`: Streamlit Dashboard
    - `service.py`: Core Auditing Logic & Logging
    - `models.py`: Data schemas
    - `env.py`: OpenEnv Environment
    - `tasks.py`: Predetermined task logic
- `inference.py`: Mandatory hackathon inference script
- `pyproject.toml`: Modern project configuration
- `uv.lock`: Dependency lock file
- `logs/`: Persisted audit history
