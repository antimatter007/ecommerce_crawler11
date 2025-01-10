# ecommerce_crawler/items.py

import scrapy

class MobileDetails(scrapy.Item):
    domain = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    model_name = scrapy.Field()
    price = scrapy.Field()
    star_rating = scrapy.Field()
    no_rating = scrapy.Field()
    colour = scrapy.Field()
    storage_cap = scrapy.Field()
    img_url = scrapy.Field()
