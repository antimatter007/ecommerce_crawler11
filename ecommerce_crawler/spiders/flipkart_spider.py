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


import scrapy
from scrapy import Request
from urllib.parse import urljoin

# If you have an items.py with `MobileDetails`, import it.
# For a quick test, we can just yield dict objects instead.
# from ecommerce_crawler.items import MobileDetails

class FlipkartSpider(scrapy.Spider):
    name = 'flipkart_spider'
    allowed_domains = ['flipkart.com']

    # Start with a single test URL
    start_url = 'https://www.flipkart.com/search?q=mobile+phones'

    # Number of pages to crawl
    count = 1
    max_pages = 2  # just do 2 pages for a basic test

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if start_url:
            self.start_url = start_url
        self.count = 1

    def start_requests(self):
        # Just request the direct page (no proxy).
        yield Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        # Debug log the HTTP status and length of the page
        self.logger.info(f"FlipkartSpider parse() => status {response.status}, length {len(response.text)}")

        # Let's do a “best guess” CSS to find product containers
        product_containers = response.css('div._2kHMtA')
        if not product_containers:
            self.logger.warning("No product containers found with `div._2kHMtA`. Trying an alternative selector.")
            # Maybe fallback to another known Flipkart layout:
            product_containers = response.css('div._4ddWXP')

        # For each container, scrape product details
        for container in product_containers:
            link = container.css('a._1fQZEK::attr(href)').get() \
                   or container.css('a.s1Q9rs::attr(href)').get() \
                   or container.css('a::attr(href)').get()

            title = container.css('div._4rR01T::text').get() \
                    or container.css('a.s1Q9rs::text').get()

            price = container.css('div._30jeq3::text').get() \
                    or container.css('div._30jeq3._16Jk6d::text').get()

            # If we found a product link, yield data
            if link:
                absolute_url = urljoin(response.url, link)

                yield {
                    'domain': 'flipkart.com',
                    'url': absolute_url,
                    'title': title,
                    'price': price.strip('₹') if price else None,
                    'star_rating': container.css('div._3LWZlK::text').get(),
                    'no_rating': None,  # We can refine later
                    'brand': (title.split()[0] if title else None),
                }

        # Next page logic
        if self.count < self.max_pages:
            self.count += 1
            next_page_url = f"{self.start_url}&page={self.count}"
            self.logger.info(f"Queuing next page: {next_page_url}")
            yield Request(url=next_page_url, callback=self.parse)
