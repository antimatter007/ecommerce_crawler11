from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Configure MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongouser:mongopassword@localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.productdb
collection = db.product_urls

@app.route('/')
def index():
    return "E-commerce Product URL Crawler Dashboard"

@app.route('/domains', methods=['GET'])
def get_domains():
    domains = collection.distinct("domain")
    return jsonify(domains)

@app.route('/products/<domain>', methods=['GET'])
def get_products(domain):
    products = collection.find({"domain": domain}, {"_id": 0, "url": 1})
    product_list = [product['url'] for product in products]
    return jsonify({domain: product_list})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
