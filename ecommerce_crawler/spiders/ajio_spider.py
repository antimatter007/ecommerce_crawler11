# ecommerce_crawler/spiders/ajio_spider.py

from urllib.parse import urlencode, urljoin
import scrapy
from scrapy import Request
from ecommerce_crawler.items import MobileDetails
import re

class AjioSpider(scrapy.Spider):
    name = 'ajio_spider'
    allowed_domains = ['ajio.com']
    base_url = 'https://www.ajio.com/shop/search?q=mobile+phones'
    count = 1
    max_pages = 15  # Adjust as needed
    API = 'YOUR-SCRAPERAPI-KEY'  # Replace with your ScraperAPI key

    def get_proxy_url(self, url):
        payload = {
            'api_key': self.API,
            'url': url,
            'country_code': 'in'
        }
        proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
        return proxy_url

    def start_requests(self):
        proxy_url = self.get_proxy_url(self.base_url)
        yield Request(
            url=proxy_url,
            callback=self.parse,
            meta={'original_url': self.base_url}
        )

    def parse(self, response):
        details = MobileDetails()

        # Extract product URLs
        product_links = response.css(
            'a.item__name::attr(href)'
        ).getall()

        # Extract additional details
        img_urls = response.css(
            'img[itemprop="image"]::attr(src)'
        ).getall()
        titles = response.css(
            'div[itemprop="name"]::text'
        ).getall()
        prices = response.css(
            'span[itemprop="price"]::text'
        ).getall()
        star_ratings = response.css(
            'div[itemprop="aggregateRating"] span::text'
        ).getall()
        no_ratings = response.css(
            'div[itemprop="aggregateRating"] span.review-count::text'
        ).getall()

        for i, link in enumerate(product_links):
            if not link.startswith('http'):
                link = urljoin(response.meta['original_url'], link)
            details['domain'] = 'ajio.com'
            details['url'] = link
            details['title'] = titles[i].strip() if i < len(titles) else None
            # Brand extraction could be part of the title or separate
            details['brand'] = None  # Implement as needed
            details['model_name'] = None  # Implement as needed
            details['price'] = prices[i].strip('₹') if i < len(prices) else None
            details['star_rating'] = star_ratings[i].strip() if i < len(star_ratings) else None
            details['no_rating'] = no_ratings[i].strip() if i < len(no_ratings) else None
            details['colour'] = None  # Implement as needed
            details['storage_cap'] = None  # Implement as needed
            details['img_url'] = img_urls[i] if i < len(img_urls) else None

            yield details

        # Handle pagination
        if self.count < self.max_pages:
            self.count += 1
            next_page_url = f"{self.base_url}&page={self.count}"
            proxy_next_page_url = self.get_proxy_url(next_page_url)
            yield Request(
                url=proxy_next_page_url,
                callback=self.parse,
                meta={'original_url': next_page_url}
            )
