import requests
import re
from requests.exceptions import RequestException
from selenium import webdriver
from lxml import etree
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
import pymongo

Client = pymongo.MongoClient('localhost', 27017)
db = Client['zgdx']
collection = db['te']


def get_page(i):

    url = 'https://gkcx.eol.cn/soudaxue/queryschool.html?&page={}'.format(i)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    browser = webdriver.Chrome(chrome_options=chrome_options)

    browser.get(url)
    # browser.close()
    return browser.page_source


def parse_page(response):

    try:
        response = etree.HTML(response)
        name = response.xpath('//tr[@class="lin-gettr"]//td[1]//text()')
        local = response.xpath('//tr[@class="lin-gettr"]//td[2]//text()')
        education = response.xpath('//tr[@class="lin-gettr"]//td[3]//text()')
        queue1 = response.xpath('//tr[@class="lin-gettr"]//td[4]//text()')
        if '2806' in queue1:
            education.append('普通本科')
        else:
            pass
        queue2 = response.xpath('//tr[@class="lin-gettr"]//td[5]//text()')
        for item in range(len(name)):
            yield{
                'name':name[item],
                'local':local[item],
                'education':education[item],
                'queue1':queue1[item],
                'queue2':queue2[item]
            }
    except IndexError:
        pass


def main(i):
    response = get_page(i)
    for item in parse_page(response):
        collection.insert(item)


if __name__ == "__main__":
    pool = Pool()
    pool.map(main, [i for i in range(1, 96)])