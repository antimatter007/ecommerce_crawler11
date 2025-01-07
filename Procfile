web: uvicorn app.main:app --host 0.0.0.0 --port 8000
worker: celery -A app.celery_worker.celery worker --loglevel=info
flower: celery -A app.celery_worker.celery flower --port=5555
