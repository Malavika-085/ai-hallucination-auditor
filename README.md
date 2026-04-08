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
Before running the inference script or the product mode, ensure the following are defined in your environment (or Space Secrets):
- `API_BASE_URL`: `https://api-inference.huggingface.co/v1`
- `MODEL_NAME`: `meta-llama/Llama-3-8B-Instruct`
- `HF_TOKEN`: Your Hugging Face User Access Token (Write)

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
- `MODE=API`: `uvicorn api:app --host 0.0.0.0 --port 7860`
- `MODE=UI`: `streamlit run app.py --server.port 7860`

---

## 📂 Project Structure
- `api.py`: FastAPI server (OpenEnv compliant)
- `app.py`: Streamlit Dashboard
- `service.py`: Core Auditing Logic & Logging
- `batch_eval.py`: CSV/JSON Batch processing
- `inference.py`: Mandatory hackathon inference script
- `logs/`: Persisted audit history
