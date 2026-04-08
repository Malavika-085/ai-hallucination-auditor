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

## 🚀 Key Features

*   **Deterministic Auditing**: Reusable engine for consistent safety checks.
*   **Real-time API**: FastAPI service for production integration.
*   **Interactive Dashboard**: Streamlit UI for visual inspection.
*   **Risk Scoring**: Multi-level risk assessment (Critical, High, Medium, Low).
*   **Benchmark Compliant**: STRICTLY preserves all OpenEnv evaluation logic.

---

## 🛠️ Installation & Setup

### Mandatory Environment Variables
Before running the inference script or the product mode, ensure the following are defined:
- `API_BASE_URL`: The API endpoint for the LLM (OpenAI-compatible).
- `MODEL_NAME`: The model identifier to use for inference.
- `HF_TOKEN`: Your Hugging Face / API key.

### Local Run (Windows)
Simply run the provided batch file to install dependencies, run a test audit, and launch the UI:
```bash
run_audit_system.bat
```

---

## 📊 Evaluation & Compliance (Base Criteria)

This project is built to strictly follow the Meta Hackathon evaluation criteria:

*   **HF Space Deploys**: API exposes `POST /reset`, `POST /step`, and `GET /state` for automated pings.
*   **OpenEnv Compliance**: Fully compliant with `openenv.yaml`, typed Pydantic models, and 100% deterministic graders.
*   **Structured Logs**: `inference.py` emits logs strictly in `[START]`, `[STEP]`, and `[END]` format.
*   **OpenAI Client**: `inference.py` uses the standard `openai.OpenAI` client for all LLM auditing calls.
*   **Infra Specs**: Optimized to run on vCPU=2, RAM=8GB, and completes under 20 minutes.

---

## 🐳 Docker Deployment

The application supports three operational modes via the `MODE` environment variable.

### 1. Benchmark Mode (Default)
Runs the OpenEnv inference script for hackathon evaluation.
```bash
docker build -t ai-auditor .
docker run ai-auditor
```

### 2. API Mode
Runs the FastAPI production server.
```bash
docker run -e MODE=API -p 8000:8000 ai-auditor
```

### 3. UI Mode
Runs the Streamlit interactive dashboard.
```bash
docker run -e MODE=UI -p 8501:8501 ai-auditor
```

---

## 📂 Project Structure
- `api.py`: FastAPI server (compliant with OpenEnv spec)
- `app.py`: Streamlit Dashboard
- `service.py`: Core Auditing Logic & Logging
- `batch_eval.py`: CSV/JSON Batch processing
- `inference.py`: Mandatory hackathon inference script
- `env.py`: OpenEnv Environment
- `tasks.py`: Predetermined task logic
- `logs/`: Persisted audit history
