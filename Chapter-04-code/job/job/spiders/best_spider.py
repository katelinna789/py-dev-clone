import scrapy
from job.items import MovieItem

class BestSpider(scrapy.Spider):
   name = "moviebest"
   start_urls = [
       'https://movie.douban.com//review/best',
   ]

   def parse(self, response):
       for movie in response.css(".main-bd"):
           item = MovieItem()
           item['title'] = movie.css('h2>a::text').extract_first()
           item['short_content'] = movie.css('.short-content::text').extract_first()
           yield item

       next_page = response.css('span.next>a::attr(href)').extract_first()
       if next_page is not None:
           yield response.follow(next_page, callback=self.parse)
