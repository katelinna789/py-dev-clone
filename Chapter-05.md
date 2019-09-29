# 第五天 爬虫实战

## ajax内容抓取
Ajax ，全称为 Asynchronous JavaScript and XML ，即异步的 JavaScript 和 XML 。 它不是一门编程语言，而是利用 JavaScript 在保证页面不被刷新、
页面链接不改变的情况下与服务器交换数据并更新部分网页的技术 。

对于传统的网页，如果想更新其内容，那么必须要刷新整个页面，但有了 Ajax ，便可以在页面不被全部刷新的情况下更新其内容。 在这个过程中，页面实际上是在后台与服务器进行了数据交互，获
取到数据之后，再利用 JavaScript 改变网页，这样网页内容就会更新了 。

### 爬取车票信息
```
import requests

data = {
    'leftTicketDTO.train_date': '2019-05-21',
    'leftTicketDTO.from_station': 'BJP',
    'leftTicketDTO.to_station': 'SJP',
    'purpose_codes': 'ADULT'
}
url = 'https://kyfw.12306.cn/otn/leftTicket/query'

r = requests.get(url,data)
result = r.json()["data"]["result"]
for item in result:
    item_list = item.split('|')
    print("车次：%s,出发时间：%s" % (item_list[3],item_list[8]))
```
## 使用已认证的cookie
对于一些需要认证的站点，我们可以使用cookie进行爬取
未使用cookie
```
import requests

url = "http://116.196.114.148:8000/admin/"
r = requests.get(url, allow_redirects=False)
print(r.headers)
```
使用cookies
```
import requests
from http import cookiejar
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
}

url = "http://116.196.114.148:8000/admin/"
cookie = cookiejar.MozillaCookieJar()
cookie.load('d://cookies.txt')
#cj = requests.utils.dict_from_cookiejar(cookie)
r = requests.get(url, headers=headers, cookies=cookie, allow_redirects=False)
print(r.status_code)

# 使用session保持cookie
import requests
from http import cookiejar
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
}

url = "http://116.196.114.148:8000/admin/"
cookie = cookiejar.MozillaCookieJar()
cookie.load('d://cookies.txt')
#cj = requests.utils.dict_from_cookiejar(cookie)
s = requests.session()
s.cookies = cookie
r = s.get(url, headers=headers, allow_redirects=False)
print(r.status_code)

```
## 动态生成内容抓取
使用selenium，抓取动态渲染内容
准备条件，安装selenium chromedriver
在群文件下载chromedriver
网络下载地址，注意对应的版本号
[chromdriver下载地址](http://chromedriver.storage.googleapis.com/index.html)

安装selenium
`pip install selenium`

```
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode
import time

chrome_options = Options()
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(executable_path=r'D:\python3\chromedriver.exe',
chrome_options=chrome_options)


params = {
    'fs': r'北京,BJP',
    'ts': r'石家庄,SJP',
    'date': '2019-05-31',
}

url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%s&ts=%s&date=%s&flag=N,N,Y' % (
    params['fs'],params['ts'],params['date'])
print(url)
driver.get(url)
time.sleep(10)
try:
    cdzs = driver.find_elements_by_css_selector(".cdz")
    trains = driver.find_elements_by_css_selector(".train")
    cds = driver.find_elements_by_css_selector(".cds")

except Exception as e:
    print(e.msg)
    driver.close()
for train in zip(cdzs, trains, cds):
    print(train[1].text,train[0].text,train[2].text)
#body = driver.page_source
#print(body)
driver.close()



```

## 使用代理
```
import requests

url = 'http://www.163.com'

proxies = {
    'http': 'www.saodaili.com:80'
}
r = requests.get(url,proxies=proxies)
print(r.content)
print(r.headers)
```

## scrapy 使用代理
创建项目
scrapy startproject proxyspider

启用 HttpProxyMiddleware 在 settings.py
```
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'proxyspider.middlewares.ProxyMiddleware': 543,
}
```
编写代理middleware,打开middlewares.py 添加ProxyMiddleware
```
class ProxyMiddleware(object):
    def process_request(self, request, spider):
        # Set the location of the proxy
        request.meta['proxy'] = "http://116.196.114.148:8000"


       # proxy_user_pass = "USERNAME:PASSWORD"
       # encoded_user_pass = base64.encodestring(proxy_user_pass)
       #request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
```
编写spider类
```
import scrapy

class ProxySpider(scrapy.Spider):
   name = "proxyspider"
   start_urls = [
       'http://httpbin.org/ip',
   ]

   def parse(self, response):
       print(response.body)
```

## 动态网站爬取 Scrapy+selenium+chrome handless

### 新建项目web12306
scrapy startproject web12306

### 编写自定义下载类

打开文件middlewares.py添加下面代码
```
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import time
class SeleniumMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == "TrainSchedule":
            chrome_options = Options()
            #chrome_options.add_argument('--headless')
            #chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(executable_path=r'D:\python3\chromedriver.exe',
            chrome_options=chrome_options)
            # driver = webdriver.Firefox()
            driver.get(request.url)
            time.sleep(5)
            body = driver.page_source
            return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        else:
                return
    def spider_closed(self, spider, reason):
        print ('close driver......')
        self.driver.close()
```
### 加载DOWNLOADER_MIDDLEWARES
修改settings.py
```
DOWNLOADER_MIDDLEWARES = {
    'web12306.middlewares.SeleniumMiddleware': 543,
}
```

### 编写spider类

在spiders下新建文件
TrainSchedule.py
```
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

```
### 运行spider
`scrapy.exe crawl TrainSchedule`

## 实例爬取整个网站
爬取整个完整并保存到本地
### 新建一个项目名称为website, 新建spider类
`scrapy startproject website`

### 编写spider类
在spiders 文件夹下新建dyttspider.py

```
import scrapy
import os.path
from urllib.parse import urlparse


class DyttSpider(scrapy.Spider):
    name = 'dytt'
    allowed_domains = ['www.dytt8.net']
    start_urls = ['https://www.dytt8.net']

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
        for ele in response.css('a[href$=html]::attr(href)'):
            next_page = ele.extract()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
```
allowed_domains 爬取的网站域名

以上代码只是爬取了html结尾的链接，不包括css和js和图片等

```
import scrapy
import os.path
from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor



class DyttSpider(scrapy.Spider):
    name = 'dytt'
    allowed_domains = ['www.dytt8.net']
    start_urls = ['https://www.dytt8.net']

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

```
LinkExtractor  类为链接提取类可以提取html中的所有链接

## 分布式爬虫
多台机器启动多个实例同事爬取

### 准备
安装scrapy-redis
`pip3 install scrapy-redis`

安装redis
```
# 安装epel yum源
yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# 安装redis
yum install redis

# 修改配置 默认只监听127.0.0.1 的 6379
vi /etc/redis.conf
bind 0.0.0.0

# 启动redis
systemctl start redis

# 确认服务启动端口
ss -tlnp | grep 6379
# 关掉防火墙
systemctl stop firewalld
systemctl disable firewalld
```

### 新建项目
scrapy startproject websiteDstributed

### 修改settings.py, 追加配置
```
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300
}
REDIS_URL = 'redis://ip:6379'
```

### 创建spider 类

```
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
```

### 创建任务
```
redis-cli

lpush dytt https://www.dytt8.net
```