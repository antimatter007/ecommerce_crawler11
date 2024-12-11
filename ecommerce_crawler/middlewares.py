import random
import os

class RotateUserAgentMiddleware:
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
        # Add more user agents as needed
    ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)

class RotateProxyMiddleware:
    def __init__(self):
        proxies = os.getenv('PROXY_LIST', '')
        if proxies:
            self.proxies = proxies.split(',')
        else:
            self.proxies = []
    
    def process_request(self, request, spider):
        if self.proxies:
            request.meta['proxy'] = random.choice(self.proxies)
