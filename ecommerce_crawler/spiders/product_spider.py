import scrapy
from app.models import ProductURL
from app.database import SessionLocal
from scrapy.http import HtmlResponse
from urllib.parse import urlparse

class ProductSpider(scrapy.Spider):
    name = "product_spider"
    
    # Start URLs can be passed dynamically to the spider
    start_urls = []

    # To store the scraped URLs
    product_urls = []

    def parse(self, response: HtmlResponse):
        """
        The main parsing function that extracts product URLs from the page.
        """
        # Log the URL of the current page being scraped
        self.logger.info(f"Scraping page: {response.url}")

        # Example selectors (Modify based on actual website structure)
        product_links = response.css('a.product-link::attr(href)').getall()

        # Log the extracted links to verify
        self.logger.info(f"Found {len(product_links)} product links on the page.")

        for link in product_links:
            # Validate the link
            if link.startswith('http'):
                self.product_urls.append(link)
            else:
                # Ensure we get a valid URL
                link = response.urljoin(link)
                self.product_urls.append(link)

        # Log the collected URLs for debugging
        self.logger.info(f"Collected URLs: {self.product_urls}")

        # Follow pagination if available
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse)

    def closed(self, reason):
        """
        Once scraping is done, store the results in the database.
        """
        db = SessionLocal()
        for url in self.product_urls:
            # Extract domain from URL
            domain = urlparse(url).netloc
            db.add(ProductURL(url=url, domain=domain))  # Add the URL and its domain
        db.commit()

        # Clean up the URLs after the spider finishes
        self.product_urls = []
        print(f"Scraping finished. Stored {len(self.product_urls)} product URLs.")
