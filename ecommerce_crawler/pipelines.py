# ecommerce_crawler/pipelines.py

import logging
from sqlalchemy.orm import Session
from scrapy.exceptions import DropItem
from ecommerce_crawler.items import MobileDetails
from app.database import SessionLocal
from app.models import ProductURL

class PostgresPipeline:
    """
    Pipeline to store product details in PostgreSQL.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def open_spider(self, spider):
        self.session = SessionLocal()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        if not isinstance(item, MobileDetails):
            return item  # Skip non-MobileDetails items

        domain = item.get('domain')
        url = item.get('url')

        if not url:
            raise DropItem("Missing URL in item")

        # Check for duplicates
        exists = self.session.query(ProductURL).filter_by(url=url).first()
        if exists:
            self.logger.info(f"Duplicate URL found: {url}. Skipping.")
            raise DropItem(f"Duplicate URL: {url}")

        # Create new record
        product = ProductURL(
            domain=domain,
            url=url,
            is_valid=item.get('is_valid', True)
        )

        # Add additional fields if necessary
        product.title = item.get('title')
        product.brand = item.get('brand')
        product.model_name = item.get('model_name')
        product.price = item.get('price')
        product.star_rating = item.get('star_rating')
        product.no_rating = item.get('no_rating')
        product.colour = item.get('colour')
        product.storage_cap = item.get('storage_cap')
        product.img_url = item.get('img_url')

        try:
            self.session.add(product)
            self.session.commit()
            self.logger.info(f"Stored URL: {url}")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error storing URL {url}: {e}")
            raise DropItem(f"Error storing URL {url}: {e}")

        return item
