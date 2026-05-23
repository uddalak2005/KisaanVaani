# Use Python 3.11 as a stable base image
FROM python:3.11-slim

# Install system dependencies required for audio processing and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the uv package manager configuration
COPY pyproject.toml uv.lock ./

# Install uv and use it to install dependencies into the system python
RUN pip install uv && uv sync --system

# Copy the application source code
COPY . .

# Expose the port Hugging Face Spaces uses by default
EXPOSE 7860

# Give execution permission to the start script
RUN chmod +x start.sh

# Run the start script as the container entrypoint
CMD ["./start.sh"]