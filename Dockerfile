# Use Python 3.10-slim as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# 1. Install dependencies directly from requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy all project files
COPY . .

# 3. Create logs directory
RUN mkdir -p logs

# Hugging Face Spaces MUST listen on Port 7860
EXPOSE 7860

# Entrypoint logic using robust python module syntax
CMD ["sh", "-c", "if [ \"$MODE\" = \"API\" ]; then python -m uvicorn server.app:app --host 0.0.0.0 --port 7860; elif [ \"$MODE\" = \"UI\" ]; then python -m streamlit run server/ui.py --server.port 7860 --server.address 0.0.0.0; else python inference.py; fi"]
