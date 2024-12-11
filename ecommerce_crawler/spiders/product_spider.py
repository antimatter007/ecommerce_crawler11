import scrapy
import re
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from scrapy_playwright.page import PageMethod
from ecommerce_crawler.queue_manager import QueueManager
from twisted.internet import reactor, defer
import json

class ProductSpider(scrapy.Spider):
    name = "product_spider"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    # Patterns to detect product URLs
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

    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.product_urls = defaultdict(set)
        self.queue_manager = QueueManager()

    def start_requests(self):
        # Start consuming URLs from RabbitMQ
        d = defer.Deferred()
        reactor.callLater(0, self.consume_from_queue, d)
        return []

    def consume_from_queue(self, deferred):
        def callback(ch, method, properties, body):
            url = body.decode('utf-8')
            self.logger.info(f"Received URL from queue: {url}")

            req = scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        # Handle infinite scrolling if necessary
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
                errback=lambda f: self.handle_error(f, ch, method)
            )
            self.crawler.engine.crawl(req, self)
            self.queue_manager.ack_message(method.delivery_tag)

        self.queue_manager.consume_urls(callback)

    def parse(self, response):
        domain = urlparse(response.url).netloc
        links = response.css('a::attr(href)').getall()
        seen_urls = self.crawler.stats.get_value("seen_urls", set()) or set()

        for link in links:
            absolute_url = urljoin(response.url, link)
            parsed_url = urlparse(absolute_url)
            normalized_url = parsed_url._replace(fragment="", query="").geturl()

            if parsed_url.netloc not in self.allowed_domains:
                continue

            if any(pattern.search(parsed_url.path) for pattern in self.PRODUCT_PATTERNS):
                self.product_urls[domain].add(normalized_url)
            else:
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    self.crawler.stats.set_value("seen_urls", seen_urls)
                    self.queue_manager.publish_url(normalized_url)

        # Yield item for pipeline
        yield {
            'domain': domain,
            'urls': list(self.product_urls[domain])
        }

    def handle_error(self, failure, ch, method):
        self.logger.warning(f"Request failed: {failure.request.url}, reason: {failure.value}")
        self.queue_manager.ack_message(method.delivery_tag)

    def closed(self, reason):
        # Optionally output to JSON or just rely on MongoDB
        output = {domain: sorted(urls) for domain, urls in self.product_urls.items()}
        with open("product_urls.json", "w") as f:
            json.dump(output, f, indent=4)
        self.logger.info("Crawling completed. Product URLs saved to product_urls.json")
