FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install your Python deps:
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install the chromium browser for Playwright:
RUN playwright install chromium

# Then whatever start commands, e.g. for your Celery + FastAPI
CMD ["celery", "-A", "app.celery_worker.celery", "worker", "--loglevel=info"]
