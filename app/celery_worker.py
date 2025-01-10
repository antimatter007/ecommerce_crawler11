import logging
import subprocess
import uuid
import os
import json
from celery import Celery
from app.database import SessionLocal
from app.models import ProductURL

# Hardcoded config for illustration:
CELERY_BROKER_URL = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"
CELERY_RESULT_BACKEND = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"

SCRAPERAPI_KEY = "a808071ccff9da6df8e44950f64246c8"
DATABASE_URL = "postgresql://postgres:dCQIJcrivbBKaqIBmEExwVrCcYhurtWl@junction.proxy.rlwy.net:38132/railway"

celery = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @celery.task
# def scrape_product_task(url: str):
#     """
#     Celery task to run the Flipkart spider on a given URL,
#     ensuring ecommerce_crawler.* is importable.
#     """
#     logger.info(f"Starting scraping task for URL: {url}")

#     unique_id = uuid.uuid4()
#     output_file = f'items_{unique_id}.json'
#     spider_relative_path = 'ecommerce_crawler/spiders/flipkart_spider.py'

#     # Copy existing environment, but also add PYTHONPATH
#     env_dict = os.environ.copy()
#     env_dict['PYTHONPATH'] = '/app'  # crucial for imports like `ecommerce_crawler.*`

#     try:
#         # 1) We'll run "scrapy runspider" with the relative path
#         # 2) We set `cwd="/app"` so the spider file is found relative to /app
#         # 3) We use `env=env_dict` so that PYTHONPATH is set
#         subprocess.run(
#             [
#                 'scrapy',
#                 'runspider',
#                 spider_relative_path,
#                 '-a', f'start_url={url}',
#                 # We can store results as "filename.json:json" or just "filename.json"
#                 '-o', f'{output_file}:json',
#             ],
#             check=True,
#             cwd='/app',
#             env=env_dict,  # ensure PYTHONPATH is recognized
#         )

#         logger.info(f"Scrapy spider completed for URL: {url}")

#         with open(output_file, 'r', encoding='utf-8') as f:
#             items = json.load(f)
#         logger.info(f"Loaded {len(items)} items from {output_file}")

#     except subprocess.CalledProcessError as e:
#         logger.error(f"Scrapy crawl failed for URL: {url} with error: {e}")
#         return {"url": url, "status": "failed", "error": str(e)}

#     except FileNotFoundError:
#         logger.error(f"Output file not found: {output_file}")
#         return {"url": url, "status": "failed", "error": f"File {output_file} not found."}

#     except json.JSONDecodeError:
#         logger.error(f"Invalid JSON in {output_file}.")
#         return {"url": url, "status": "failed", "error": f"JSON decode error in {output_file}."}

#     finally:
#         # Clean up
#         full_output_path = os.path.join('/app', output_file)
#         if os.path.exists(full_output_path):
#             os.remove(full_output_path)
#             logger.info(f"Removed temporary file {output_file}")

#     # Insert into DB
#     db = SessionLocal()
#     try:
#         for item in items:
#             product = ProductURL(
#                 domain=item.get('domain'),
#                 url=item.get('url'),
#                 title=item.get('title'),
#                 brand=item.get('brand'),
#                 model_name=item.get('model_name'),
#                 price=float(item['price']) if item.get('price') else None,
#                 star_rating=float(item['star_rating']) if item.get('star_rating') else None,
#                 no_rating=int(item['no_rating']) if item.get('no_rating') else None,
#                 colour=item.get('colour'),
#                 storage_cap=item.get('storage_cap'),
#                 img_url=item.get('img_url'),
#             )
#             db.add(product)
#         db.commit()
#         logger.info(f"Scraping completed and data inserted for URL: {url}")
#         return {"url": url, "status": "scraped"}

#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error inserting data into database: {e}")
#         return {"url": url, "status": "failed", "error": str(e)}
#     finally:
#         db.close()


@celery.task
def scrape_product_task(url: str = ""):
    """
    If the user passes a URL, we pass `-a start_url=...`
    Otherwise, the spider uses its default.
    """
    logger.info(f"Starting scraping task for URL: {url!r}")

    unique_id = uuid.uuid4()
    output_file = f'items_{unique_id}.json'
    spider_relative_path = 'ecommerce_crawler/spiders/flipkart_spider.py'

    env_dict = os.environ.copy()
    env_dict['PYTHONPATH'] = '/app'

    cmd = [
        'scrapy', 'runspider', spider_relative_path,
        '-o', f'{output_file}:json'
    ]
    if url:
        cmd += ['-a', f'start_url={url}']

    try:
        # 1) We'll run "scrapy runspider" with the relative path
        # 2) We set `cwd="/app"` so the spider file is found relative to /app
        # 3) We use `env=env_dict` so that PYTHONPATH is set
        subprocess.run(
            [
                'scrapy',
                'runspider',
                spider_relative_path,
                '-a', f'start_url={url}',
                # We can store results as "filename.json:json" or just "filename.json"
                '-o', f'{output_file}:json',
            ],
            check=True,
            cwd='/app',
            env=env_dict,  # ensure PYTHONPATH is recognized
        )

        logger.info(f"Scrapy spider completed for URL: {url}")

        with open(output_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        logger.info(f"Loaded {len(items)} items from {output_file}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Scrapy crawl failed for URL: {url} with error: {e}")
        return {"url": url, "status": "failed", "error": str(e)}

    except FileNotFoundError:
        logger.error(f"Output file not found: {output_file}")
        return {"url": url, "status": "failed", "error": f"File {output_file} not found."}

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {output_file}.")
        return {"url": url, "status": "failed", "error": f"JSON decode error in {output_file}."}

    finally:
        # Clean up
        full_output_path = os.path.join('/app', output_file)
        if os.path.exists(full_output_path):
            os.remove(full_output_path)
            logger.info(f"Removed temporary file {output_file}")

    # Insert into DB
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
        logger.info(f"Scraping completed and data inserted for URL: {url}")
        return {"url": url, "status": "scraped"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting data into database: {e}")
        return {"url": url, "status": "failed", "error": str(e)}
    finally:
        db.close()
