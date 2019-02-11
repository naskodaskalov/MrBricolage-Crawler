# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MrbricolagecrawlerItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    price_without_currency = scrapy.Field()
    image = scrapy.Field()
    specifications = scrapy.Field()
    pass
