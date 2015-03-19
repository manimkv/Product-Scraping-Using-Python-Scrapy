from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request
import re
import csv



class AaramShop(Spider):
    name = 'aaramshop'
    allowed_domains = ['aaramshop.com']
    start_urls = (
               'https://www.aaramshop.com/',
                )

    def parse(self, response):
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        menu = xp(".//*[@id='menu']")
        url = menu.xpath(".//li/a//@href").extract()
        category = [x for x in url if re.search('/category', x)]
        for cat in category:
            yield Request(cat, callback=self.parse_url)

    def parse_url(self, response):
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        self.csv_file_name = re.split('category/', response.url)[1]
        csv_category = open('%s_%s.csv' % ('aaramshop', self.csv_file_name), 'wb')
        csv_writer = csv.writer(csv_category)
        csv_writer.writerow(['name', 'weight', 'price'])
        ph = xp(".//*[@class='product_holder']")
        for i in ph:
            name = i.xpath(".//div[@class='name']/a//text()").extract()[0]
            sku = i.xpath(".//div[@class='sku']//text()").extract()[0]
            price = i.xpath(".//div[@class='price']//text()").extract()[0].replace('0930', '')
            csv_writer.writerow([name.encode('ascii', 'ignore'), sku.encode('ascii', 'ignore'), price.encode('ascii', 'ignore')])
        links = set(xp(".//*[@class='links']/a/@href").extract())
        for link in links:
            yield Request(link, meta={'writer_obj': csv_writer}, callback=self.parse_page)

    def parse_page(self, response):
        sel = Selector(response)
        xp = lambda x: sel.xpath(x)
        csv_writer = response.meta['writer_obj']
        ph = xp(".//*[@class='product_holder']")
        for i in ph:
            name = i.xpath(".//div[@class='name']/a//text()").extract()[0]
            sku = i.xpath(".//div[@class='sku']//text()").extract()[0]
            price = i.xpath(".//div[@class='price']//text()").extract()[0].replace('0930', '')
            csv_writer.writerow([name.encode('ascii', 'ignore'), sku.encode('ascii', 'ignore'), price.encode('ascii', 'ignore')])








