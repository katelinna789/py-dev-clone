import scrapy

class ProxySpider(scrapy.Spider):
   name = "proxyspider"
   start_urls = [
       'http://httpbin.org/ip',
   ]

   def parse(self, response):
       print(response.body)
