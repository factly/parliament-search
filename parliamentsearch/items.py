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


class RajyaSabhaQuestions():
	"""
	Data structure to define a Rajya Sabha question
	"""
	q_no = scrapy.Field()
	q_type = scrapy.Field()
	q_date = scrapy.Field()
	q_ministry = scrapy.Field()
	q_member = scrapy.Field()
	q_subject = scrapy.Field()
