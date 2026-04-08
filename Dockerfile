# Use Python 3.10-slim as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the requirements/pyproject and install dependencies
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Copy all project files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Hugging Face Spaces MUST listen on Port 7860
EXPOSE 7860

# Entrypoint logic:
# - Default: runs inference.py (Benchmark mode)
# - MODE=API: runs the 'server' entry point (FastAPI)
# - MODE=UI: runs Streamlit on server/ui.py
CMD ["sh", "-c", "if [ \"$MODE\" = \"API\" ]; then server; elif [ \"$MODE\" = \"UI\" ]; then streamlit run server/ui.py --server.port 7860 --server.address 0.0.0.0; else python inference.py; fi"]
