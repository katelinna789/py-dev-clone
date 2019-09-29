# -*- coding: utf-8 -*-
import scrapy


class TrainscheduleSpider(scrapy.Spider):
    name = 'TrainSchedule'
    params = {
        'fs': '北京,BJP',
        'ts': '石家庄,SJP',
        'date': '2019-05-31',
    }
    url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%s&ts=%s&date=%s&flag=N,N,Y' % (
        params['fs'], params['ts'], params['date'])
    start_urls = [url]

    def parse(self, response):
        for item in response.css(".train"):
            print(item.css("div>a::text").extract_first())