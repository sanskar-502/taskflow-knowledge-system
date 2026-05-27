FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (much smaller than full torch)
RUN pip install --default-timeout=300 --no-cache-dir \
    torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directories for uploads and chroma data
RUN mkdir -p /app/uploads /app/chroma_data

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
