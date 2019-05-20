# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb

class MoviePipeline(object):
   def __init__(self, host, database, user, port,password):
       self.host = host
       self.database = database
       self.user = user
       self.port = port
       self.password = password
   @classmethod
   def from_crawler(cls, crawler):
       settings = crawler.settings
       return cls(
           settings.get('MYSQL_HOST'),
           settings.get('MYSQL_DATABASE'),
           settings.get('MYSQL_USER'),
           settings.get('MYSQL_PORT'),
           settings.get('MYSQL_PASSWORD')
           )
   def open_spider(self, spider):
       print(self.port,self.password)
       self.db = MySQLdb.connect(host=self.host,database=self.database,user=self.user, port=self.port,password=self.password, charset='utf8')
       self.cursor = self.db.cursor()
   def close_spider(self, spider):
       self.cursor.close()
       self.db.close()
   def process_item(self, item, spider):
       data = dict(item)
       sql = 'insert into movie(title, short_content) values("%s", "%s")' % (data['title'],data['short_content'])
       self.cursor.execute(sql)
       self.db.commit()
       return item




