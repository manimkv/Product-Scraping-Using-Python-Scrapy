# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request
from datetime import date
import csv
import re
from itertools import izip


class KrocerySpider(Spider):
    name = "redcart"
    allowed_domains = ["redcart.in"]
    start_urls = (
        'http://www.redcart.in/',
    )   

    def parse(self, response):
        sel = Selector(response)
        self.today = date.today().strftime('%d-%m-%Y')
        xp = lambda x: sel.xpath(x) 
        self.csv_file_header = 'redcart'
        
        for x, category in izip(xp('//*[@class="level0 nav-5 first parent"]')[0].xpath('.//*[@class="col"]'), ['Grocery', 'Diary', 'Pantry', 'HomeCare', 'PersonalCare', 'Drinks', 'Breakfast']):
            csv_category = open('%s_%s.csv' % (self.csv_file_header, category), 'wb')
            csv_writer = csv.writer(csv_category)
            csv_writer.writerow(['date', 'product with quantity', 'price'])
            self.processed = []

            for url in x.xpath('.//@href').extract():
                yield Request(url, meta={'writer_obj': csv_writer, 'processed': self.processed}, callback=self.parse_url)


    def parse_url(self, response):
        sel = Selector(response)
        log.msg('Processing %s' % response.url)
        xp = lambda x: sel.xpath(x)
        csv_writer = response.meta['writer_obj']
        processed = response.meta['processed']
        prices = map(lambda x: x.xpath('.//*[@class="price"]//text()').extract()[-1].replace('\n', '').strip(), xp('//*[@class="price-box"]'))   
        names = xp('//*[@class="product-name"]//text()').extract()
       
        for name, price in izip(names, prices):
            if not self.processed.__contains__((name, price)):
                self.processed.append((name, price))
                csv_writer.writerow([self.today, name, price])
        return

