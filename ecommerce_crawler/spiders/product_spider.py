# ecommerce_crawler/ecommerce_crawler/spiders/product_spider.py

import scrapy
import re
import json
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from scrapy_playwright.page import PageMethod
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

class ProductSpider(scrapy.Spider):
    name = "product_spider"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "timeout": 60000,  # 60 seconds
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        },
    }

    PRODUCT_PATTERNS = [
        re.compile(r"/product/[\w-]+"),
        re.compile(r"/item/[\w-]+"),
        re.compile(r"/p/[\w-]+"),
        re.compile(r"/products/[\w-]+"),
        re.compile(r"/shop/[\w-]+"),
        re.compile(r"/detail/[\w-]+"),
        re.compile(r"/store/[\w-]+"),
        re.compile(r"/goods/[\w-]+"),
        # eBay-specific pattern
        re.compile(r"/itm/\d+"),
        # Amazon-specific patterns
        re.compile(r"/dp/[A-Z0-9]{10}"),
        re.compile(r"/gp/product/[A-Z0-9]{10}")
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
        self.seen_urls = set()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
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
                    "playwright_include_page": True,
                    "errback": self.errback_httpbin,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        domain = urlparse(response.url).netloc
        links = response.css('a::attr(href)').getall()

        for link in links:
            absolute_url = urljoin(response.url, link)
            parsed_url = urlparse(absolute_url)
            normalized_url = parsed_url._replace(fragment="", query="").geturl()

            if parsed_url.netloc not in self.allowed_domains:
                continue

            if normalized_url in self.seen_urls:
                continue

            self.seen_urls.add(normalized_url)

            if any(pattern.search(parsed_url.path) for pattern in self.PRODUCT_PATTERNS):
                self.product_urls[domain].add(normalized_url)
                self.logger.info(f"Found product URL: {normalized_url}")
                yield {
                    'domain': domain,
                    'url': normalized_url,
                }
            else:
                yield scrapy.Request(
                    normalized_url,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "domcontentloaded"),
                        ],
                        "errback": self.errback_httpbin,
                    },
                    callback=self.parse,
                    dont_filter=True,
                )

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        request = failure.request

        if failure.check(PlaywrightTimeoutError):
            self.logger.error(f"TimeoutError on {request.url}, retrying...")
            yield request.copy().replace(dont_filter=True)
        elif failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            self.logger.error(f"HttpError on {response.url}: {response.status}")
            if response.status in [403, 429]:
                self.logger.error(f"Likely blocked on {response.url}")
        else:
            self.logger.error(f"Unhandled exception on {request.url}")

    def closed(self, reason):
        # Write out product URLs
        output = {domain: sorted(urls) for domain, urls in self.product_urls.items()}
        with open("product_urls.json", "w") as f:
            json.dump(output, f, indent=4)
        self.logger.info("Crawling completed. Product URLs saved to product_urls.json")
