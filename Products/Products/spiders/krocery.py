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
    name = "krocery"
    allowed_domains = ["krocery.com"]
    start_urls = (
        'http://www.krocery.com/',
    )   

    def parse(self, response):
        sel = Selector(response)
        self.today = date.today().strftime('%d-%m-%Y')
        xp = lambda x: sel.xpath(x) 
        self.csv_file_header = 'krocery'
        category_urls = filter(None, xp('//*[@class="level0 full columns-5 mega"]')[0].re('href="(/*\w*/*\w*-*\w*)"'))
        master_url = response.url

        for url in category_urls:
            yield Request('%s%s' % (master_url, url[1:]), meta={'csv_file': url[1:].split('/')[-1], 'master_url': master_url}, callback=self.parse_url)


    def parse_url(self, response):
        sel = Selector(response)
        log.msg('Processing %s' % response.url)
        xp = lambda x: sel.xpath(x)
        csv_category = open('%s_%s.csv' % (self.csv_file_header, response.meta['csv_file']), 'wb')
        csv_writer = csv.writer(csv_category)
        csv_writer.writerow(['date', 'product with quantity', 'price'])
        title_page_range = xp('//*[@class="page-title"]')
        
        for count in range(1, len(title_page_range)+1):
            head_xpath = '//*[@id="ves-col-main"]/div/div/div[%d]//@href' % (count*2)
            for sub_category_url_part in xp(head_xpath).extract():
                yield Request('%s%s' % (response.meta['master_url'], sub_category_url_part[1:]), meta={'writer_obj': csv_writer}, callback=self.parse_item)
     
     
    def parse_item(self, response):
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        csv_writer = response.meta['writer_obj']

        for item in xp('//*[@class="pbox productscroll-item box-hover item-content"]'):
            product = item.xpath('.//*[@class="entry-title"]//text()').extract()[0]
            price = item.xpath('.//*[@class="price"]//text()').extract()[-1]
            csv_writer.writerow([self.today, product.encode('ascii', 'ignore'), price.strip()])

        return



