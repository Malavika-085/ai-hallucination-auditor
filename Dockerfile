# Use Python 3.10-slim as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# 1. Copy dependency definitions first (for caching)
COPY requirements.txt .
COPY pyproject.toml .
COPY uv.lock .

# 2. Install external dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy ALL project files (Mandatory before pip install -e .)
COPY . .

# 4. Install the regional project
RUN pip install -e .

# Create logs directory
RUN mkdir -p logs

# Hugging Face Spaces MUST listen on Port 7860
EXPOSE 7860

# Entrypoint logic
CMD ["sh", "-c", \"if [ \\"$MODE\\" = \\"API\\" ]; then server; elif [ \\"$MODE\\" = \\"UI\\" ]; then streamlit run server/ui.py --server.port 7860 --server.address 0.0.0.0; else python inference.py; fi\"]
