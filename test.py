import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool


def get_orders(url):
    res = requests.get(url)
    bs = BeautifulSoup(res.text, 'lxml')
    h = bs.select('#billboard > div.billboard-hd > h2')[0]
    t = h.contents[0]
    orders = bs.select('#billboard > div.billboard-bd > table')[0]
    urls = []
    for order in orders.find_all('a'):
        urls.append((order['href'],order.string))
    return t, urls


def get_contents(url):
    url, name = url.split('|')
    res = requests.get(url)
    bs = BeautifulSoup(res.text, 'lxml')
    c = bs.select('#link-report')[0]

    return(name, c.text)



if __name__ == '__main__':
    import MySQLdb
    url = 'https://movie.douban.com/'
    t, urls = get_orders(url)

    with Pool(5) as p:
        contents = p.map(get_contents, [url[0] + '|' + url[1] for url in urls])

    db = MySQLdb.connect(host='localhost', user='root', database='test', charset='utf8')
    cursor = db.cursor()
    for content in contents:
        sql = 'insert into moive(name, content) values("%s", "%s")' % (content[0], content[1])
        print(sql)
        cursor.execute(sql)
        db.commit()
    cursor.close()
    db.close()