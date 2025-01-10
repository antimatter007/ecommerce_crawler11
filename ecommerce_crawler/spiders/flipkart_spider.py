# from urllib.parse import urlencode, urljoin
# import scrapy
# from scrapy import Request
# from ecommerce_crawler.items import MobileDetails
# import re

# class FlipkartSpider(scrapy.Spider):
#     name = 'flipkart_spider'
#     allowed_domains = ['flipkart.com']

#     # Default base_url if no spider argument is provided
#     default_base_url = 'https://www.flipkart.com/search?q=mobile+phones'
#     count = 1
#     max_pages = 20  # Adjust as needed
#     API = 'a808071ccff9da6df8e44950f64246c8'  # Replace with your ScraperAPI key

#     def __init__(self, start_url=None, *args, **kwargs):
#         """
#         If user passes -a start_url=... we store it in self.base_url;
#         otherwise, fallback to default_base_url.
#         """
#         super().__init__(*args, **kwargs)
#         self.base_url = start_url or self.default_base_url
#         self.count = 1

#     def get_proxy_url(self, url):
#         payload = {
#             'api_key': self.API,
#             'url': url,
#             'country_code': 'in'
#         }
#         proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
#         return proxy_url

#     def start_requests(self):
#         proxy_url = self.get_proxy_url(self.base_url)
#         yield Request(
#             url=proxy_url,
#             callback=self.parse,
#             meta={'original_url': self.base_url}
#         )

#     def parse(self, response):
#         # We'll store results in a Scrapy Item or dictionary
#         # MobileDetails is a dictionary-like object
#         details = MobileDetails()

#         # Extract product URLs
#         product_links = response.css('a._1fQZEK::attr(href)').getall()
#         if not product_links:
#             product_links = response.css('a.IRpwTa::attr(href)').getall()

#         # Extract additional details
#         img_urls = response.css('div._1AtVbE img._396cs4::attr(src)').getall()
#         titles   = response.css('div._1AtVbE div._4rR01T::text').getall()
#         prices   = response.css('div._1AtVbE div._30jeq3::text').getall()
#         star_ratings = response.css('div._1AtVbE div._3LWZlK::text').getall()
#         no_ratings   = response.css('div._1AtVbE div._3LWZlK + span::text').getall()

#         # For each product link, yield an item
#         for i, link in enumerate(product_links):
#             absolute_url = link
#             if not link.startswith('http'):
#                 absolute_url = urljoin(response.meta['original_url'], link)

#             details['domain']       = 'flipkart.com'
#             details['url']          = absolute_url
#             details['title']        = titles[i] if i < len(titles) else None
#             details['brand']        = (titles[i].split()[0]
#                                        if i < len(titles) and titles[i]
#                                        else None)
#             details['model_name']   = None  # placeholder
#             details['price']        = (prices[i].strip('₹')
#                                        if i < len(prices) else None)
#             details['star_rating']  = star_ratings[i] if i < len(star_ratings) else None
#             details['no_rating']    = no_ratings[i]   if i < len(no_ratings)   else None
#             details['colour']       = None  # placeholder
#             details['storage_cap']  = None  # placeholder
#             details['img_url']      = img_urls[i] if i < len(img_urls) else None

#             yield details

#         # Handle pagination if we haven't reached max_pages
#         if self.count < self.max_pages:
#             self.count += 1
#             next_page_url = f"{self.base_url}&page={self.count}"
#             proxy_next_page_url = self.get_proxy_url(next_page_url)

#             yield Request(
#                 url=proxy_next_page_url,
#                 callback=self.parse,
#                 meta={'original_url': next_page_url}
#             )
# ecommerce_crawler/spiders/flipkart_playwright_spider.py

import scrapy
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin
from ecommerce_crawler.items import MobileDetails


class FlipkartPlaywrightSpider(scrapy.Spider):
    """
    Spider that uses Scrapy-Playwright to scrape mobile phone listings from Flipkart.
    """
    name = "flipkart_playwright"
    allowed_domains = ["flipkart.com"]
    start_urls = [
        "https://www.flipkart.com/search?q=mobile+phones"
    ]
    max_pages = 3  # set smaller for quick test; increase as needed

    # We'll track how many pages we've crawled
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_count = 0

    def start_requests(self):
        """
        Start by requesting the first URL with Playwright enabled.
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    # We'll wait for the product list container or 
                    # any selector that ensures content is loaded.
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div._1AtVbE")
                    ],
                },
                callback=self.parse
            )

    async def parse(self, response):
        """
        Parse the search results page. 
        Note: we’re in an `async def` because Scrapy-Playwright uses async I/O.
        """
        # Log how many product blocks we detect:
        product_cards = response.css("div._1AtVbE")
        self.logger.info(f"Found {len(product_cards)} product blocks on page {self.page_count+1}")

        for card in product_cards:
            # Some blocks on Flipkart are banners or ads. 
            # We can skip those that don't have price/title.
            title = card.css("div._4rR01T::text").get()
            price = card.css("div._30jeq3::text").get()
            if not title or not price:
                continue

            details = MobileDetails()
            details["domain"] = "flipkart.com"
            details["title"] = title
            details["price"] = price.strip("₹").replace(",", "")
            # Example: extracting link
            product_link = card.css("a._1fQZEK::attr(href)").get()
            if product_link:
                details["url"] = urljoin(response.url, product_link)
            # Additional fields:
            details["brand"] = title.split()[0]
            details["star_rating"] = card.css("div._3LWZlK::text").get()
            details["no_rating"] = None  # you can parse next sibling if needed
            # color / storage could be looked up in the link text, or not available 
            yield details

        # Next pages
        self.page_count += 1
        if self.page_count < self.max_pages:
            next_page_url = response.css("a._1LKTO3::attr(href)").get()  # typical 'Next' link
            if next_page_url:
                absolute_url = response.urljoin(next_page_url)
                yield scrapy.Request(
                    absolute_url,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "div._1AtVbE")
                        ],
                    },
                    callback=self.parse
                )
