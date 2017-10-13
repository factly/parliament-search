# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from enum import Enum
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


class RajyaSabhaQuestion(scrapy.Item):
	"""
	Data structure to define a Rajya Sabha question
	"""
	q_no = scrapy.Field()
	q_type = scrapy.Field()
	q_date = scrapy.Field()
	q_ministry = scrapy.Field()
	q_member = scrapy.Field()
	q_subject = scrapy.Field()

class LSQnFields(Enum):
	NUM = 0
	TYPE = 1
	DATE = 2
	MINISTRY = 3
	MEMBERS = 4
	SUBJECT = 5
	ANNEX = 6

class LokSabhaQuestion(scrapy.Item):
	"""
	Data structure to define a Lok Sabha question
	"""
	q_no = scrapy.Field()
	q_session = scrapy.Field()
	q_type = scrapy.Field()
	q_date = scrapy.Field()
	q_ministry = scrapy.Field()
	q_member = scrapy.Field()
	q_subject = scrapy.Field()
	q_url = scrapy.Field()
	q_annex = scrapy.Field()
