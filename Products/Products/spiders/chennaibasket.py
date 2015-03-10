# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request
from urlparse import urljoin
# from lib.mongo_helpers import db
from datetime import date
import csv

class ChennaibasketSpider(Spider):
    name = "chennaibasket"
    allowed_domains = ["chennaibasket.com"]
    start_urls = (
        'http://www.chennaibasket.com/',
    )   

    def parse(self, response):
        sel = Selector(response)
        self.today = date.today().strftime('%d-%m-%Y')
        xp = lambda x: sel.xpath(x)
        
        for x in xp("//*[@class='tlli mkids']"):
            fetch_url = x.re('<a class="tll" href="(.*)"')
            yield Request(fetch_url[0], callback=self.parse_url)


    def parse_url(self, response):
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        rest_pages = list(set(xp("//*[@class='links']//@href").extract()))
        rest_pages.append('%s?page=1' % response.url)
        self.category = open('%s.csv' % response.url.split('/')[-1], 'wb')
        csv_writer = csv.writer(self.category)
        csv_writer.writerow(['date', 'product with quantity', 'price'])

        for page_url in rest_pages:
            yield Request(page_url, meta={'writer_obj': csv_writer}, callback=self.parse_page)            


    def parse_page(self, response):
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        csv_writer = response.meta['writer_obj']

        for x in xp('//*[@class="three mobile-two columns"]'):
            try:
                price = x.xpath('.//*[@class="price-new"]//text()').extract()[0]
            except IndexError:
                price = x.xpath('.//*[@class="price"]//text()').extract()[0].replace('\n', '').strip()
            product = x.xpath('.//*[@class="name"]//text()').extract()[0]
            product = product.encode('ascii', 'ignore')
            csv_writer.writerow([self.today, product, price])
        
        return
                 



