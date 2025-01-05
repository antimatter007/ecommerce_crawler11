# ecommerce_crawler/middlewares.py

from urllib.parse import urlencode
import logging
import random
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class ScraperAPIMiddleware:
    """
    Middleware to route requests through ScraperAPI.
    """

    def __init__(self, scraperapi_key):
        self.scraperapi_key = scraperapi_key
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_crawler(cls, crawler):
        scraperapi_key = crawler.settings.get('SCRAPERAPI_KEY')
        if not scraperapi_key:
            raise NotConfigured
        return cls(scraperapi_key)

    def process_request(self, request, spider):
        original_url = request.url
        payload = {
            'api_key': self.scraperapi_key,
            'url': original_url,
            'country_code': 'in'
        }
        proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
        request.meta['proxy'] = 'http://api.scraperapi.com'
        request.url = proxy_url
        self.logger.debug(f"Routing through ScraperAPI: {request.url}")

class RotateUserAgentMiddleware(UserAgentMiddleware):
    """
    Middleware to rotate user agents for each request.
    """

    def __init__(self, user_agents):
        self.user_agents = user_agents
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agents=crawler.settings.get('USER_AGENTS_LIST')
        )

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers.setdefault('User-Agent', user_agent)
        self.logger.debug(f"Using User-Agent: {user_agent}")
