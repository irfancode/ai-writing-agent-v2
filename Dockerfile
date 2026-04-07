FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy only the files needed for generating the uv layer
COPY pyproject.toml .

# Install dependencies before copying code
RUN uv pip install --system -e .[dev]

# Copy the rest of the application
COPY . .

# Expose API port
EXPOSE 8000

# Run the API server
CMD ["python", "-m", "uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
