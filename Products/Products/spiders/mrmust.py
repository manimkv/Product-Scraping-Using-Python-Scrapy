# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request
from datetime import date
import csv
from time import sleep

class ChennaibasketSpider(Spider):
    name = "mrmust"
    allowed_domains = ["mrmust.com"]
    start_urls = (
        'http://www.mrmust.com/',
    )   

    def parse(self, response):
        sel = Selector(response)
        self.today = date.today().strftime('%d-%m-%Y')
        xp = lambda x: sel.xpath(x)
        self.csv_file_header = 'mrmust'

        for cat in xp("//*[@class='cbp-hrsub']"):
            for url in cat.xpath('.//@href').extract():
                
                yield Request(url, meta={'csv_file': self.category}, callback=self.parse_url)


    def parse_url(self, response):
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
                 

