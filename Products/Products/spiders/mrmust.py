# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request
from datetime import date
import csv
import re
from itertools import izip


class MrmustSpider(Spider):
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
            url_part = re.findall('.com/(.*)/', cat.xpath('.//@href').extract()[0])[0]
            yield Request('%s%s' % (response.url, url_part), meta={'csv_file': re.search('\w+', url_part).group()}, callback=self.parse_url)


    def parse_url(self, response):
        sel = Selector(response)
        log.msg('Processing %s' % response.url)
        xp = lambda x: sel.xpath(x)
        csv_category = open('%s_%s.csv' % (self.csv_file_header, response.meta['csv_file']), 'wb')
        csv_writer = csv.writer(csv_category)
        csv_writer.writerow(['date', 'product with quantity', 'price'])
        products = zip(xp("//*[@class='li_product_name']"), xp('//*[@class="li_quantity"]'))
 
        for name_obj, price_obj in products:
            name = name_obj.xpath('.//@title').extract()[0]
            price = price_obj.xpath('.//span//text()').extract()[-1]
            csv_writer.writerow([self.today, name, price])
        
        return


