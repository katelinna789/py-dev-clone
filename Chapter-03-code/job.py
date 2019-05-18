import requests
from bs4 import BeautifulSoup
import queue


def get_contest(url):
    urls = []
    r = requests.get(url)
    bs = BeautifulSoup(r.content, 'html.parser')
    for bd in bs.select('.main-bd'):
        title = bd.select('h2 > a')[0].text
        short_content = bd.select('.short-content')[0].text
        print(title, short_content)
    for a in bs.select('.paginator a'):
        next_url = a['href']
        urls.append(next_url)
    return urls


url_prefix = 'https://movie.douban.com'
start_url = '/review/best'
url_queue = queue.Queue()
seen = set()
seen.add(start_url)
url_queue.put(start_url)

while True:
    if not url_queue.empty():
        current_url = url_prefix + url_queue.get()
        print(current_url)
        for next_url in get_contest(current_url):
            if next_url not in seen:
                seen.add(next_url)
                url_queue.put(next_url)
    else:
        break



