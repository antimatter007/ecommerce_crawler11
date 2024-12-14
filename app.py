# app.py

from flask import Flask, request, jsonify
import subprocess
import threading
import json
import os

app = Flask(__name__)

def run_spider(domains):
    # Run the Scrapy spider with specified domains
    cmd = [
        "scrapy",
        "crawl",
        "product_spider",
        "-a",
        f"domains={domains}",
        "--loglevel",
        "INFO"
    ]
    subprocess.run(cmd)

@app.route('/run-crawler', methods=['POST'])
def run_crawler():
    data = request.json
    domains = data.get('domains', '')
    if not domains:
        return jsonify({"error": "No domains provided"}), 400

    # Run the spider in a separate thread
    thread = threading.Thread(target=run_spider, args=(domains,))
    thread.start()

    return jsonify({"status": "Crawler started"}), 200

@app.route('/get-results', methods=['GET'])
def get_results():
    try:
        with open("product_urls.json", "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "No results found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
