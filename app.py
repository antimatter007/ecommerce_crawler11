# app.py

from flask import Flask, request, jsonify
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ecommerce_crawler.spiders.product_spider import ProductSpider
import multiprocessing
import json
import os

app = Flask(__name__)

# Global variable to store scraped data
scraped_data = {}

def run_spider(domains):
    """
    Function to run the Scrapy spider in a separate process.
    """
    try:
        # Initialize CrawlerProcess with project settings
        process = CrawlerProcess(get_project_settings())
        # Start crawling with the spider class and pass 'domains' as an argument
        process.crawl(ProductSpider, domains=domains)
        process.start()  # This will block until the crawling is finished

        # After crawling, read the 'product_urls.json' file
        if os.path.exists("product_urls.json"):
            with open("product_urls.json", "r") as f:
                data = json.load(f)
                scraped_data.update(data)
    except Exception as e:
        print(f"Error running crawler: {e}")

@app.route('/run-crawler', methods=['POST'])
def run_crawler():
    """
    Endpoint to initiate the crawler.
    Expects a JSON payload with a 'domains' key containing comma-separated domain names.
    """
    data = request.get_json()
    domains = data.get('domains', '')
    
    if not domains:
        return jsonify({"error": "No domains provided"}), 400
    
    # Clear previous results
    if os.path.exists("product_urls.json"):
        os.remove("product_urls.json")
    scraped_data.clear()
    
    # Run the spider in a separate process
    process = multiprocessing.Process(target=run_spider, args=(domains,))
    process.start()
    
    return jsonify({"status": "Crawler started"}), 200

@app.route('/get-results', methods=['GET'])
def get_results():
    """
    Endpoint to retrieve the scraped product URLs.
    Returns the contents of 'product_urls.json'.
    """
    try:
        # Ensure the JSON file exists
        if not os.path.exists("product_urls.json"):
            return jsonify({"error": "No results found"}), 404
        
        with open("product_urls.json", "r") as f:
            data = json.load(f)
        
        return jsonify(data), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding results"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on all available IPs, port 8000
    app.run(host='0.0.0.0', port=8000)
