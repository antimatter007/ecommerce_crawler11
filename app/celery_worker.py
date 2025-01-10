import logging
import subprocess
import uuid
import os
import json

from celery import Celery
from app.database import SessionLocal
from app.models import ProductURL

# Hardcoded Configuration (example)
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
    """
    Celery task to run the Flipkart spider on a given URL.
    """
    logger.info(f"Starting scraping task for URL: {url}")

    # Generate a unique filename for the output JSON
    unique_id = uuid.uuid4()
    output_file = f'items_{unique_id}.json'      # The file that Scrapy will write to

    # Path to your spider script (adjust if different)
    spider_script = os.path.join(
        os.getcwd(), 'ecommerce_crawler', 'spiders', 'flipkart_spider.py'
    )

    try:
        # Run Scrapy spider as a subprocess
        #
        # * runspider usage:
        #   scrapy runspider <spider_file> -a <spider_arg>=... -o <file.json:json>
        #
        # Important: No trailing semicolon, and remove -t 'json'
        #
        subprocess.run([
            'scrapy',
            'runspider',
            spider_script,
            '-a', f'start_url={url}',
            '-o', f'{output_file}:json',  
            # ^ appending :json ensures output is treated as JSON
        ], check=True)

        logger.info(f"Scrapy spider completed for URL: {url}")

        # Read items from output JSON
        with open(output_file, 'r') as f:
            items = json.load(f)

        logger.info(f"Loaded {len(items)} items from {output_file}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Scrapy crawl failed for URL: {url} with error: {e}")
        return {"url": url, "status": "failed", "error": str(e)}

    except FileNotFoundError:
        logger.error(f"Scrapy output file {output_file} not found.")
        return {"url": url, "status": "failed", "error": f"Output file {output_file} not found."}

    except json.JSONDecodeError:
        logger.error(f"Scrapy output file {output_file} is not valid JSON.")
        return {"url": url, "status": "failed", "error": f"Invalid JSON in {output_file}."}

    finally:
        # Clean up the output file
        if os.path.exists(output_file):
            os.remove(output_file)
            logger.info(f"Removed temporary file {output_file}")

    # Insert scraped items into the database
    db = SessionLocal()
    try:
        for item in items:
            product = ProductURL(
                domain=item.get('domain'),
                url=item.get('url'),
                title=item.get('title'),
                brand=item.get('brand'),
                model_name=item.get('model_name'),
                price=float(item['price']) if item.get('price') else None,
                star_rating=float(item['star_rating']) if item.get('star_rating') else None,
                no_rating=int(item['no_rating']) if item.get('no_rating') else None,
                colour=item.get('colour'),
                storage_cap=item.get('storage_cap'),
                img_url=item.get('img_url'),
            )
            db.add(product)
        db.commit()
        logger.info(f"Scraping completed. Inserted data for URL: {url}")
        return {"url": url, "status": "scraped"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting data into database: {e}")
        return {"url": url, "status": "failed", "error": str(e)}
    finally:
        db.close()
