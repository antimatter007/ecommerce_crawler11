import json

class EcommerceCrawlerPipeline:
    def open_spider(self, spider):
        self.product_data = {}

    def close_spider(self, spider):
        # Convert sets to lists for JSON serialization
        serializable_data = {domain: list(urls) for domain, urls in self.product_data.items()}
        with open('output/product_urls.json', 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)

    def process_item(self, item, spider):
        domain = item['domain']
        url = item['url']
        
        if domain not in self.product_data:
            self.product_data[domain] = set()
        
        self.product_data[domain].add(url)
        
        return item
