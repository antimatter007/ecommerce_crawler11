import scrapy

class EcommerceCrawlerItem(scrapy.Item):
    domain = scrapy.Field()
    url = scrapy.Field()
