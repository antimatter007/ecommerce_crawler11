# ecommerce_crawler/spiders/amazon_spider.py

from urllib.parse import urlencode, urljoin
import scrapy
from scrapy import Request
from ecommerce_crawler.items import MobileDetails
import re

class AmazonSpider(scrapy.Spider):
    name = 'amazon_spider'
    allowed_domains = ['amazon.in']
    base_url = 'https://www.amazon.in/Today-Mobile-Offer/s?k=Today+Mobile+Offer'
    count = 1
    max_pages = 20  # Adjust as needed
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
            'div.s-main-slot div[data-component-type="s-search-result"] h2 a::attr(href)'
        ).getall()

        # Extract additional details if needed
        img_urls = response.css(
            'div.s-main-slot div[data-component-type="s-search-result"] img.s-image::attr(src)'
        ).getall()
        titles = response.css(
            'div.s-main-slot div[data-component-type="s-search-result"] h2 a span::text'
        ).getall()
        prices = response.css(
            'div.s-main-slot div[data-component-type="s-search-result"] span.a-price-whole::text'
        ).getall()
        star_ratings = response.css(
            'div.s-main-slot div[data-component-type="s-search-result"] span.a-icon-alt::text'
        ).getall()
        no_ratings = response.css(
            'div.s-main-slot div[data-component-type="s-search-result"] span.a-size-base::text'
        ).getall()

        for i, link in enumerate(product_links):
            if not link.startswith('http'):
                link = urljoin(response.meta['original_url'], link)
            details['domain'] = 'amazon.in'
            details['url'] = link
            details['title'] = titles[i] if i < len(titles) else None
            # Simple brand extraction from title
            details['brand'] = titles[i].split()[0] if titles and len(titles[i].split()) > 0 else None
            # Model name extraction can be complex; placeholder
            details['model_name'] = None  # Implement as needed
            details['price'] = prices[i] if i < len(prices) else None
            details['star_rating'] = star_ratings[i] if i < len(star_ratings) else None
            details['no_rating'] = no_ratings[i] if i < len(no_ratings) else None
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
