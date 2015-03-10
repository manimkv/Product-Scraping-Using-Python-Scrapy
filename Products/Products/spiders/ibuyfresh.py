# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request
from datetime import date
import csv
from time import sleep

class IbuyfreshSpider(Spider):
    name = "ibuyfresh"
    allowed_domains = ["ibuyfresh.com"]
    start_urls = (
        'http://www.ibuyfresh.com/',
    )   

    def parse(self, response):
        sel = Selector(response)
        self.today = date.today().strftime('%d-%m-%Y')
        xp = lambda x: sel.xpath(x)
        self.csv_file_header = 'ibuyfresh'
        cat_list = {'Fruits': 'Fruits', 'Vegetables': 'Vegetables', 'Organic': 'Organic', 'Grocery': 'Grocery', 'Bread & Dairy': 'Bread-Dairy-and-Frozen', 'Branded Foods': 'Branded-Foods', 'Personal Care': 'Personal-Care', 'House Hold': 'House-Hold'}
        
        for x in xp("//*[@class='title-cntr']"):
            self.category = x.xpath('.//span//text()').extract()[0]
            if self.category not in ['Recipes', 'Quick Shop', 'Help']:
                yield Request('%s%s' % (response.url, cat_list[self.category]), meta={'csv_file': self.category}, callback=self.parse_url)


    def parse_url(self, response):
        log.msg('Processing %s'%response.url)
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        csv_category = open('%s_%s.csv' % (self.csv_file_header, response.meta['csv_file']), 'wb')
        csv_writer = csv.writer(csv_category)
        csv_writer.writerow(['date', 'brand', 'product', 'quantity', 'price'])

        for item in xp("//*[@class='prod-item']"):
            product = item.re('alt="(.*)"')[0].strip()
            brand = item.xpath('.//*[@class="avail-at"]//text()').extract()[0].strip()
            try:
                price = item.xpath('.//*[@class="fa fa-inr tar"]//text()').extract()[0]
            except IndexError:
                price = item.xpath('.//*[@class="fa fa-inr tal"]//text()').extract()[0]
            product = product.encode('ascii', 'ignore')
            try:
                quantity = item.xpath('.//p/text()').extract()[0]
            except IndexError:
                quantity = item.re('"&nbsp;(\d+\w*)"')[0]
            price = price.encode('ascii', 'ignore')
            csv_writer.writerow([self.today, brand, product, quantity, price])

        return
                 

