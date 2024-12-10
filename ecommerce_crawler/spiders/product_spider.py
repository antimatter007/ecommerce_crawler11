# ecommerce_crawler/spiders/product_spider.py

import scrapy
import re
import json
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from scrapy_playwright.page import PageMethod

class ProductSpider(scrapy.Spider):
    name = "product_spider"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    # Define product URL patterns (add more patterns as needed)
    PRODUCT_PATTERNS = [
        re.compile(r"/product/[\w-]+"),
        re.compile(r"/item/[\w-]+"),
        re.compile(r"/p/[\w-]+"),
        re.compile(r"/products/[\w-]+"),
        re.compile(r"/shop/[\w-]+"),
        re.compile(r"/detail/[\w-]+"),
        re.compile(r"/store/[\w-]+"),
        re.compile(r"/goods/[\w-]+"),
    ]

    def __init__(self, domains=None, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        if domains:
            self.start_domains = [d.strip() for d in domains.split(",")]
            self.start_urls = [f"https://{domain}" for domain in self.start_domains]
            self.allowed_domains = [urlparse(u).netloc for u in self.start_urls]
        else:
            self.logger.error("No domains provided. Use -a domains=\"example1.com,example2.com\"")
            self.start_urls = []
            self.allowed_domains = []

        self.product_urls = defaultdict(set)

    def start_requests(self):
        # For each domain, we start from the homepage and attempt infinite scrolling
        # and dynamic content rendering if needed.
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    # Apply infinite scrolling logic for dynamic sites
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("evaluate", """
                            async () => {
                                let previousHeight = 0;
                                while (true) {
                                    window.scrollTo(0, document.body.scrollHeight);
                                    await new Promise(resolve => setTimeout(resolve, 2000));
                                    let newHeight = document.body.scrollHeight;
                                    if (newHeight === previousHeight) break;
                                    previousHeight = newHeight;
                                }
                            }
                        """),
                    ],
                },
                callback=self.parse,
            )

    def parse(self, response):
        domain = urlparse(response.url).netloc

        # Extract all links from the current page
        links = response.css('a::attr(href)').getall()
        seen_urls = self.crawler.stats.get_value("seen_urls", set()) or set()

        for link in links:
            absolute_url = urljoin(response.url, link)
            parsed_url = urlparse(absolute_url)

            # Normalize URL by removing fragments and query parameters
            normalized_url = parsed_url._replace(fragment="", query="").geturl()

            # Ensure the link is within the same domain
            if parsed_url.netloc not in self.allowed_domains:
                continue

            # Check if the URL matches any product pattern
            if any(pattern.search(parsed_url.path) for pattern in self.PRODUCT_PATTERNS):
                self.product_urls[domain].add(normalized_url)
            else:
                # Avoid revisiting the same URL
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    self.crawler.stats.set_value("seen_urls", seen_urls)

                    # For non-product pages, we follow links as well
                    yield scrapy.Request(
                        normalized_url,
                        meta={
                            "playwright": True,
                            # Attempt a shorter scroll sequence to load content
                            "playwright_page_methods": [
                                PageMethod("wait_for_load_state", "networkidle"),
                            ],
                        },
                        callback=self.parse,
                    )

    def closed(self, reason):
        # Output results in product_urls.json mapping each domain to its list of product URLs
        output = {domain: sorted(urls) for domain, urls in self.product_urls.items()}
        with open("product_urls.json", "w") as f:
            json.dump(output, f, indent=4)
        self.logger.info("Crawling completed. Product URLs saved to product_urls.json")
