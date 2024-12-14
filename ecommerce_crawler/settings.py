# ecommerce_crawler/ecommerce_crawler/settings.py

BOT_NAME = 'ecommerce_crawler'

SPIDER_MODULES = ['ecommerce_crawler.spiders']
NEWSPIDER_MODULE = 'ecommerce_crawler.spiders'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 1.0

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
   'User-Agent': 'Mozilla/5.0 (compatible; ProductCrawler/1.0; +http://www.example.com)',
   'Accept-Language': 'en',
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
AUTOTHROTTLE_DEBUG = False

TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000
CLOSESPIDER_TIMEOUT = 60
DEPTH_LIMIT = 5

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]

LOG_LEVEL = 'INFO'

# Disable playwright request/response/storage_state logging
SCRAPY_PLAYWRIGHT_LOG_REQUEST = False
SCRAPY_PLAYWRIGHT_LOG_RESPONSE = False
SCRAPY_PLAYWRIGHT_LOG_STORAGE_STATE = False
