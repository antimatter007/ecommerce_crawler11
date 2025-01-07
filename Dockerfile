# Start from a lightweight Python base image
FROM python:3.11-slim

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    curl \
    gnupg \
    # If you do NOT need Supervisor, remove it:
    #   supervisor \
    && rm -rf /var/lib/apt/lists/*

# If using Scrapy-Playwright (optional), install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory for all subsequent commands
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Upgrade pip and install your Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) If using Scrapy-Playwright, install the required browser(s)
RUN playwright install chromium

# Expose any ports your FastAPI app needs (e.g., 8000)
EXPOSE 8000
# If you also plan to run Celery Flower in a separate container/service,
# you do NOT need to expose port 5555 here. If you do, add:
# EXPOSE 5555

# Run your FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
