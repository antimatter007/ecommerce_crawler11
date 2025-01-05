# ecommerce_crawler/items.py

import scrapy

class MobileDetails(scrapy.Item):
    """
    A Scrapy Item that represents detailed information of a mobile product.
    """
    domain = scrapy.Field()            # E.g., 'amazon.in'
    url = scrapy.Field()               # Product URL
    title = scrapy.Field()             # Product title
    brand = scrapy.Field()             # Brand name
    model_name = scrapy.Field()        # Model name
    price = scrapy.Field()             # Price
    star_rating = scrapy.Field()       # Star rating
    no_rating = scrapy.Field()         # Number of ratings
    colour = scrapy.Field()            # Colour
    storage_cap = scrapy.Field()       # Storage capacity
    img_url = scrapy.Field()           # Image URL
