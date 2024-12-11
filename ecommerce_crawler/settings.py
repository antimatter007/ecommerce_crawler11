import os

BOT_NAME = 'ecommerce_crawler'

SPIDER_MODULES = ['ecommerce_crawler.spiders']
NEWSPIDER_MODULE = 'ecommerce_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 100

# Configure a delay for requests
DOWNLOAD_DELAY = 0.1

# Configure concurrent requests per domain
CONCURRENT_REQUESTS_PER_DOMAIN = 20

# Disable cookies
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Default request headers
DEFAULT_REQUEST_HEADERS = {
   'User-Agent': 'Mozilla/5.0 (compatible; ProductCrawler/1.0; +http://www.example.com)',
   'Accept-Language': 'en',
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'ecommerce_crawler.middlewares.RotateUserAgentMiddleware': 543,
    'ecommerce_crawler.middlewares.RotateProxyMiddleware': 544,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'ecommerce_crawler.pipelines.MongoDBPipeline': 300,
}

# MongoDB settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongouser:mongopassword@localhost:27017/')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'ecommerce')

# Enable AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 20.0
AUTOTHROTTLE_DEBUG = False

# Playwright settings
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000  # 30 seconds timeout

# Depth limit to prevent overly deep crawls
DEPTH_LIMIT = 3

# Logging
LOG_LEVEL = 'INFO'
