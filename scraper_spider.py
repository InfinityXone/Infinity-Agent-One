import scrapy, asyncio
from scrapy.crawler import CrawlerProcess

class FaucetSpider(scrapy.Spider):
    name = "faucets"
    start_urls = ["https://faucetpay.io/faucet-list"]

    def parse(self, response):
        for link in response.css("a::attr(href)").getall():
            yield {"link": link}

    async def run(self):
        loop = asyncio.get_event_loop()
        process = CrawlerProcess(settings={"LOG_ENABLED": False})
        process.crawl(FaucetSpider)
        loop.run_in_executor(None, process.start, True)
        return "🕷️ Faucet spider executed"
