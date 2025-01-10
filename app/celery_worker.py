# app/celery_worker.py

from celery import Celery
from ecommerce_crawler.spiders.flipkart_spider import FlipkartSpider
from scrapy.crawler import CrawlerProcess
from app.database import SessionLocal
from app.models import ProductURL
import logging
import json

# Hardcoded Configuration
CELERY_BROKER_URL = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"
CELERY_RESULT_BACKEND = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"

SCRAPERAPI_KEY = "a808071ccff9da6df8e44950f64246c8"

DATABASE_URL = "postgresql://postgres:dCQIJcrivbBKaqIBmEExwVrCcYhurtWl@junction.proxy.rlwy.net:38132/railway"

celery = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def scrape_product_task(url: str):
    logger.info(f"Starting scraping task for URL: {url}")
    
    # Configure Scrapy settings
    process = CrawlerProcess(settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "ROBOTSTXT_OBEY": False,
    })
    
    # Start the crawler
    process.crawl(FlipkartSpider, start_url=url)
    process.start()  # Blocks until the crawling is finished
    
    # After crawling, read the scraped items and insert into the database
    try:
        with open('items.json') as f:
            items = json.load(f)
    except FileNotFoundError:
        logger.error("Scraping failed: items.json not found.")
        return {"url": url, "status": "failed", "error": "Scraping failed: items.json not found."}
    except json.JSONDecodeError:
        logger.error("Scraping failed: items.json is not a valid JSON file.")
        return {"url": url, "status": "failed", "error": "Scraping failed: items.json is not a valid JSON file."}
    
    db = SessionLocal()
    try:
        for item in items:
            product = ProductURL(
                domain=item.get('domain'),
                url=item.get('url'),
                title=item.get('title'),
                brand=item.get('brand'),
                model_name=item.get('model_name'),
                price=float(item.get('price')) if item.get('price') else None,
                star_rating=float(item.get('star_rating')) if item.get('star_rating') else None,
                no_rating=int(item.get('no_rating')) if item.get('no_rating') else None,
                colour=item.get('colour'),
                storage_cap=item.get('storage_cap'),
                img_url=item.get('img_url'),
            )
            db.add(product)
        db.commit()
        logger.info(f"Scraping completed and data inserted for URL: {url}")
        return {"url": url, "status": "scraped"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting data into database: {e}")
        return {"url": url, "status": "failed", "error": str(e)}
    finally:
        db.close()
