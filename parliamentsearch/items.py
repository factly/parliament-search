# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class MemberofParliament(scrapy.Item):
	"""
	Data structure to define Member of Parliament information
	"""
	mp_id = scrapy.Field()
	mp_name = scrapy.Field()
	mp_constituency = scrapy.Field()
	mp_party = scrapy.Field()
	mp_photo = scrapy.Field()
