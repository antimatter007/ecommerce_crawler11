# ecommerce_crawler/spiders/myntra_spider.py

from urllib.parse import urlencode, urljoin
import scrapy
from scrapy import Request
from ecommerce_crawler.items import MobileDetails
import re

class MyntraSpider(scrapy.Spider):
    name = 'myntra_spider'
    allowed_domains = ['myntra.com']
    base_url = 'https://www.myntra.com/search?searchTerm=mobile+phones'
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
            'a.product-base::attr(href)'
        ).getall()

        # Extract additional details
        img_urls = response.css(
            'img.product-image::attr(src)'
        ).getall()
        titles = response.css(
            'h3.product-brand::text'
        ).getall()
        sub_titles = response.css(
            'h4.product-product::text'
        ).getall()
        prices = response.css(
            'div.product-price::text'
        ).getall()
        star_ratings = response.css(
            'div.product-ratings::text'
        ).getall()
        no_ratings = response.css(
            'span.product-ratings-count::text'
        ).getall()

        for i, link in enumerate(product_links):
            if not link.startswith('http'):
                link = urljoin(response.meta['original_url'], link)
            details['domain'] = 'myntra.com'
            details['url'] = link
            details['title'] = titles[i].strip() if i < len(titles) else None
            details['brand'] = titles[i].strip() if i < len(titles) else None
            details['model_name'] = sub_titles[i].strip() if i < len(sub_titles) else None
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
