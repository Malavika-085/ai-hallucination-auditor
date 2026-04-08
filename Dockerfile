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

# Hugging Face Spaces MUST listen on Port 7860
EXPOSE 7860

# Entrypoint logic:
# - Default: runs inference.py (Benchmark mode)
# - MODE=API: runs FastAPI server on 7860
# - MODE=UI: runs Streamlit dashboard on 7860
CMD ["sh", "-c", "if [ \"$MODE\" = \"API\" ]; then uvicorn api:app --host 0.0.0.0 --port 7860; elif [ \"$MODE\" = \"UI\" ]; then streamlit run app.py --server.port 7860 --server.address 0.0.0.0; else python inference.py; fi"]
