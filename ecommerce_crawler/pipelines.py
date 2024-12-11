import motor.motor_asyncio
from urllib.parse import urlparse
from collections import defaultdict
import os

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'ecommerce'),
        )

    async def open_spider(self, spider):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db['product_urls']

    async def close_spider(self, spider):
        self.client.close()

    async def process_item(self, item, spider):
        domain = item['domain']
        urls = item['urls']
        if not urls:
            return item

        operations = []
        for url in urls:
            operations.append(
                self.collection.update_one(
                    {'domain': domain, 'url': url},
                    {'$set': {'domain': domain, 'url': url}},
                    upsert=True
                )
            )
        await self.collection.bulk_write(operations)
        return item
