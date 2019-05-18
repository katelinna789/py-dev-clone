import scrapy


class QuotesSpider(scrapy.Spider):
    name = "douban"
    start_urls = [
        'https://movie.douban.com/',
    ]

    def parse(self, response):
        for quote in response.css('#billboard > div.billboard-bd > table > tr'):
            yield {
                'title': quote.css('.title>a::text').extract_first(),
                'order': quote.css('.order::text').extract_first(),
            }
