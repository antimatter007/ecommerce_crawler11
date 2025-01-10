# ecommerce_crawler/settings.py

BOT_NAME = 'ecommerce_crawler'

SPIDER_MODULES = ['ecommerce_crawler.spiders']
NEWSPIDER_MODULE = 'ecommerce_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Configure a delay for requests
DOWNLOAD_DELAY = 0.5  # seconds

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'ecommerce_crawler.middlewares.ScraperAPIMiddleware': 543,
    'ecommerce_crawler.middlewares.RotateUserAgentMiddleware': 544,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # Disable default
}
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# We want the chromium browser
PLAYWRIGHT_BROWSER_TYPE = "chromium"

# Enable item pipelines
ITEM_PIPELINES = {
    'ecommerce_crawler.pipelines.PostgresPipeline': 300,
}

# Logging
LOG_LEVEL = 'INFO'

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# User Agents list for rotation
USER_AGENTS_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    # Add more user agents as needed
]

# ScraperAPI Key
SCRAPERAPI_KEY = 'a808071ccff9da6df8e44950f64246c8'  # Replace with your actual ScraperAPI key
