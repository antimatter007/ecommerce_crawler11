from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ecommerce_crawler.spiders.product_spider import ProductSpider

def main():
    process = CrawlerProcess(get_project_settings())
    process.crawl(ProductSpider)
    process.start()  # the script will block here until the crawling is finished

if __name__ == '__main__':
    main()
