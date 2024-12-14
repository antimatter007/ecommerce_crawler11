# app.py

from flask import Flask, request, jsonify
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from ecommerce_crawler.spiders.product_spider import ProductSpider
import asyncio

app = Flask(__name__)

@app.route('/run-crawler', methods=['POST'])
def run_crawler():
    data = request.get_json()
    domains = data.get('domains', '')

    if not domains:
        return jsonify({"error": "No domains provided"}), 400

    # Get Scrapy settings
    settings = get_project_settings()

    # Create a new event loop for asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initialize CrawlerRunner with settings
    runner = CrawlerRunner(settings=settings)

    # Create a list to store scraped data
    scraped_data = {}

    async def crawl():
        # Initialize the spider with domains
        spider = ProductSpider(domains=domains)

        # Start crawling
        await runner.crawl(spider)

        # After crawling, retrieve the data
        return spider.product_urls

    try:
        # Run the crawl coroutine
        scraped_data = loop.run_until_complete(crawl())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

    # Convert sets to lists for JSON serialization
    serialized_data = {domain: list(urls) for domain, urls in scraped_data.items()}

    return jsonify(serialized_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
