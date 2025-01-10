# import logging
# import subprocess
# import uuid
# import os
# import json
# from celery import Celery
# from app.database import SessionLocal
# from app.models import ProductURL

# # Hardcoded config for illustration:
# CELERY_BROKER_URL = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"
# CELERY_RESULT_BACKEND = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"

# SCRAPERAPI_KEY = "a808071ccff9da6df8e44950f64246c8"
# DATABASE_URL = "postgresql://postgres:dCQIJcrivbBKaqIBmEExwVrCcYhurtWl@junction.proxy.rlwy.net:38132/railway"

# celery = Celery(
#     "worker",
#     broker=CELERY_BROKER_URL,
#     backend=CELERY_RESULT_BACKEND,
# )

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# # @celery.task
# # def scrape_product_task(url: str):
# #     """
# #     Celery task to run the Flipkart spider on a given URL,
# #     ensuring ecommerce_crawler.* is importable.
# #     """
# #     logger.info(f"Starting scraping task for URL: {url}")

# #     unique_id = uuid.uuid4()
# #     output_file = f'items_{unique_id}.json'
# #     spider_relative_path = 'ecommerce_crawler/spiders/flipkart_spider.py'

# #     # Copy existing environment, but also add PYTHONPATH
# #     env_dict = os.environ.copy()
# #     env_dict['PYTHONPATH'] = '/app'  # crucial for imports like `ecommerce_crawler.*`

# #     try:
# #         # 1) We'll run "scrapy runspider" with the relative path
# #         # 2) We set `cwd="/app"` so the spider file is found relative to /app
# #         # 3) We use `env=env_dict` so that PYTHONPATH is set
# #         subprocess.run(
# #             [
# #                 'scrapy',
# #                 'runspider',
# #                 spider_relative_path,
# #                 '-a', f'start_url={url}',
# #                 # We can store results as "filename.json:json" or just "filename.json"
# #                 '-o', f'{output_file}:json',
# #             ],
# #             check=True,
# #             cwd='/app',
# #             env=env_dict,  # ensure PYTHONPATH is recognized
# #         )

# #         logger.info(f"Scrapy spider completed for URL: {url}")

# #         with open(output_file, 'r', encoding='utf-8') as f:
# #             items = json.load(f)
# #         logger.info(f"Loaded {len(items)} items from {output_file}")

# #     except subprocess.CalledProcessError as e:
# #         logger.error(f"Scrapy crawl failed for URL: {url} with error: {e}")
# #         return {"url": url, "status": "failed", "error": str(e)}

# #     except FileNotFoundError:
# #         logger.error(f"Output file not found: {output_file}")
# #         return {"url": url, "status": "failed", "error": f"File {output_file} not found."}

# #     except json.JSONDecodeError:
# #         logger.error(f"Invalid JSON in {output_file}.")
# #         return {"url": url, "status": "failed", "error": f"JSON decode error in {output_file}."}

# #     finally:
# #         # Clean up
# #         full_output_path = os.path.join('/app', output_file)
# #         if os.path.exists(full_output_path):
# #             os.remove(full_output_path)
# #             logger.info(f"Removed temporary file {output_file}")

# #     # Insert into DB
# #     db = SessionLocal()
# #     try:
# #         for item in items:
# #             product = ProductURL(
# #                 domain=item.get('domain'),
# #                 url=item.get('url'),
# #                 title=item.get('title'),
# #                 brand=item.get('brand'),
# #                 model_name=item.get('model_name'),
# #                 price=float(item['price']) if item.get('price') else None,
# #                 star_rating=float(item['star_rating']) if item.get('star_rating') else None,
# #                 no_rating=int(item['no_rating']) if item.get('no_rating') else None,
# #                 colour=item.get('colour'),
# #                 storage_cap=item.get('storage_cap'),
# #                 img_url=item.get('img_url'),
# #             )
# #             db.add(product)
# #         db.commit()
# #         logger.info(f"Scraping completed and data inserted for URL: {url}")
# #         return {"url": url, "status": "scraped"}

# #     except Exception as e:
# #         db.rollback()
# #         logger.error(f"Error inserting data into database: {e}")
# #         return {"url": url, "status": "failed", "error": str(e)}
# #     finally:
# #         db.close()


# @celery.task
# def scrape_product_task(url: str = ""):
#     """
#     If the user passes a URL, we pass `-a start_url=...`
#     Otherwise, the spider uses its default.
#     """
#     logger.info(f"Starting scraping task for URL: {url!r}")

#     unique_id = uuid.uuid4()
#     output_file = f'items_{unique_id}.json'
#     spider_relative_path = 'ecommerce_crawler/spiders/flipkart_spider.py'

#     env_dict = os.environ.copy()
#     env_dict['PYTHONPATH'] = '/app'

#     cmd = [
#         'scrapy', 'runspider', spider_relative_path,
#         '-o', f'{output_file}:json'
#     ]
#     if url:
#         cmd += ['-a', f'start_url={url}']

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


# app/celery_worker.py

import os
import json
import uuid
import logging
import subprocess

from celery import Celery
from app.database import SessionLocal
from app.models import ProductURL

# Hardcoded for demo:
CELERY_BROKER_URL = "redis://..."
CELERY_RESULT_BACKEND = "redis://..."

celery = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def scrape_product_task():
    """
    Task that triggers the Flipkart spider using Scrapy-Playwright.
    The spider is named 'flipkart_playwright' in 'flipkart_playwright_spider.py'.
    """
    unique_id = uuid.uuid4()
    output_file = f"items_{unique_id}.json"
    spider_name = "flipkart_playwright"

    logger.info("Starting flipkart_playwright spider...")

    try:
        # Use 'scrapy crawl <spidername>' so that your project can see ecommerce_crawler
        # The -O <filename> auto-detects JSON from extension or you can do -o FILE:json
        subprocess.run(
            [
                "scrapy", "crawl", spider_name,
                "-O", output_file,
                # We can also override any settings here if needed:
                "-s", "DOWNLOAD_HANDLERS={\"http\":\"scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler\",\"https\":\"scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler\"}",
                "-s", "PLAYWRIGHT_BROWSER_TYPE=chromium",
            ],
            check=True,
            cwd="/app"  # assuming /app is your Docker WORKDIR
        )

        logger.info("Scrapy spider completed successfully.")

        # Now read the JSON
        if not os.path.exists(output_file):
            logger.error(f"No items file found: {output_file}")
            return {"status": "failed", "error": "No output file."}

        with open(output_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        logger.info(f"Loaded {len(items)} items from {output_file}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Scrapy crawl error: {e}")
        return {"status": "failed", "error": str(e)}

    except json.JSONDecodeError:
        logger.error(f"Could not parse {output_file} as JSON.")
        return {"status": "failed", "error": "JSON decode error"}

    finally:
        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)

    # Insert into DB
    db = SessionLocal()
    try:
        for item in items:
            url = item.get("url")
            if not url:
                continue

            product = ProductURL(
                domain=item.get("domain", ""),
                url=url,
                title=item.get("title"),
                brand=item.get("brand"),
                model_name=item.get("model_name"),
                price=float(item["price"]) if item.get("price") else None,
                star_rating=float(item["star_rating"]) if item.get("star_rating") else None,
                no_rating=int(item["no_rating"]) if item.get("no_rating") else None,
                colour=item.get("colour"),
                storage_cap=item.get("storage_cap"),
                img_url=item.get("img_url"),
            )
            db.add(product)
        db.commit()
        logger.info("Data inserted into Postgres.")
        return {"status": "scraped", "count": len(items)}
    except Exception as e:
        db.rollback()
        logger.error(f"DB insert error: {e}")
        return {"status": "failed_in_db", "error": str(e)}
    finally:
        db.close()
