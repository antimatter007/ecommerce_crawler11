from fastapi import FastAPI
from celery.result import AsyncResult
from app.celery_worker import scrape_product_task  # Import the scrape task
from pydantic import BaseModel

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape/")
async def scrape(request: ScrapeRequest):
    # Trigger the scraping task asynchronously using Celery
    task = scrape_product_task.delay(request.url)
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.ready():
        return {"status": task_result.status, "result": task_result.result}
    return {"status": task_result.status}
