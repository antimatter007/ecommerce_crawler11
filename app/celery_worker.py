from celery import Celery
from ecommerce_crawler.spiders.product_spider import ProductSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
from urllib.parse import urlparse

# Create a Celery instance
celery = Celery('tasks', broker='redis://localhost:6379/0')  # Update with correct broker if needed

# Set up logging for the task
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def scrape_product_task(url):
    """
    This task triggers the Scrapy spider to scrape product URLs.
    """
    logger.info(f"Starting scraping task for URL: {url}")

    # Get Scrapy project settings
    settings = get_project_settings()

    # Set Scrapy settings for fast crawling
    settings.set('DOWNLOAD_DELAY', 0)  # No delay between requests for fast testing
    settings.set('CONCURRENT_REQUESTS', 10)  # Allow multiple requests in parallel
    settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', 10)  # Allow multiple requests per domain
    settings.set('DEPTH_LIMIT', 2)  # Limit crawl depth for testing
    settings.set('AUTOTHROTTLE_ENABLED', False)  # Disable throttling
    settings.set('LOG_LEVEL', 'ERROR')  # Only log errors

    # Set up Scrapy's CrawlerProcess
    process = CrawlerProcess(settings)

    logger.info(f"Running spider for URL: {url}")

    try:
        # Pass the spider class to the crawl method (not an instance)
        process.crawl(ProductSpider, start_urls=[url])  # Pass the class and arguments
        process.start()
        logger.info(f"Scraping started for {url}")
        return f"Scraping started for {url}"
    except Exception as e:
        logger.error(f"Error during scraping task for {url}: {e}")
        return f"Failed to start scraping for {url}. Error: {e}"
