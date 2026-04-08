# Use Python 3.10-slim as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create logs directory for the product mode
RUN mkdir -p logs

# Expose ports for API (8000) and Streamlit UI (8501)
EXPOSE 8000
EXPOSE 8501

# Entrypoint logic:
# - Default: runs inference.py (Benchmark mode)
# - MODE=API: runs FastAPI server
# - MODE=UI: runs Streamlit dashboard
CMD ["sh", "-c", "if [ \"$MODE\" = \"API\" ]; then uvicorn api:app --host 0.0.0.0 --port 8000; elif [ \"$MODE\" = \"UI\" ]; then streamlit run app.py --server.port 8501 --server.address 0.0.0.0; else python inference.py; fi"]
