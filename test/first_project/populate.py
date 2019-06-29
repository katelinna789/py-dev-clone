import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'first_project.settings')
import django
django.setup()

from navigation.models import Category, Page

def populate():
    python_pages = [
        {"title": "Official Python Tutorial",
         "views": 20,
         "url":"http://docs.python.org/2/tutorial/"},
        {"title":"How to Think like a Computer Scientist",
         "views": 12,
         "url":"http://www.greenteapress.com/thinkpython/"},
        {"title":"Learn Python in 10 Minutes",
         "views": 15,
         "url":"http://www.korokithakis.net/tutorials/python/"} ]

    django_pages = [
        {"title": "Official Django Tutorial",
         "views": 15,
         "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/"},
        {"title": "Django Rocks",
         "views": 10,
         "url": "http://www.djangorocks.com/"},
        {"title": "How to Tango with Django",
         "views": 10,
         "url": "http://www.tangowithdjango.com/"}]
    other_pages = [
        {"title": "Bottle",
         "views": 10,
         "url":"http://bottlepy.org/docs/dev/"},
        {"title": "Flask",
         "views": 17,
         "url": "http://flask.pocoo.org"}]

    cats = {"Python": {"pages": python_pages},
            "Django": {"pages": django_pages},
            "Other Frameworks": {"pages": other_pages} }

    for cat, cat_data in cats.items():
        c = add_cat(cat)
        for p in cat_data["pages"]:
            # 修改
            add_page(c, p["title"], p["url"],p["views"])

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c),str(p)))


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p

def add_cat(name):
    if name == 'Python':
        c = Category.objects.get_or_create(name=name,views=128,likes=64)[0]
    elif name == "Django":
        c = Category.objects.get_or_create(name=name, views=64, likes=32)[0]
    elif name == "Other Frameworks":
        c = Category.objects.get_or_create(name=name, views=32, likes=16)[0]
    c.save()
    return c

if __name__ == '__main__':
    print("开始导入数据")
    populate()