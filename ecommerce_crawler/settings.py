# settings.py

BOT_NAME = 'ecommerce_crawler'

SPIDER_MODULES = ['ecommerce_crawler.spiders']
NEWSPIDER_MODULE = 'ecommerce_crawler.spiders'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 0.5

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
   'User-Agent': 'Mozilla/5.0 (compatible; ProductCrawler/1.0; +http://www.amazon.com)',
   'Accept-Language': 'en',
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0
AUTOTHROTTLE_DEBUG = False

TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000  # Increased to 30 seconds

# Stop after 1 minute
CLOSESPIDER_TIMEOUT = 60

# Limit depth to 5 levels
DEPTH_LIMIT = 5
