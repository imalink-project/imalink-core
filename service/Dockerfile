# FastAPI service for imalink-core
FROM python:3.13-slim

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY service/ ./service/

# Install uv and dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

# Install FastAPI dependencies
RUN uv pip install --system fastapi uvicorn[standard]

# Expose port
EXPOSE 8765

# Run FastAPI service
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8765"]
