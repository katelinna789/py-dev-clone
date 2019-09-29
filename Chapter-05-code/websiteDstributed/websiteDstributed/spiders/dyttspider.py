from scrapy_redis.spiders import RedisSpider

import os.path
from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor



class DyttSpider(RedisSpider):
    name = 'dytt'
    allowed_domains = ['www.dytt8.net']
    #start_urls = ['https://www.dytt8.net']
    redis_key = 'dytt'

    def parse(self, response):
        urlpath= urlparse(response.url).path
        if not os.path.exists('./data'):
            os.mkdir("./data")
        dirpath = './data/' + '/'.join(urlpath.split('/')[:-1]).strip('/')
        filename = urlpath.split('/')[-1]
        if filename:
            filepath = os.path.join(dirpath, filename)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            with open(filepath,"wb") as f:
                f.write(response.body)
        linkextractor = LinkExtractor()
        links = linkextractor.extract_links(response)
        for link in links:
            next_page = link.url

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)