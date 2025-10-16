# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using UV
RUN uv sync --frozen

# Copy source code
COPY src/ ./src/
COPY arch_pdfs/ ./arch_pdfs/
COPY vector_store/ ./vector_store/

# Create necessary directories
RUN mkdir -p /app/vector_store

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uv", "run", "uvicorn", "normo_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
