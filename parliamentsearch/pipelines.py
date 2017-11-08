# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
import pymongo

class ParliamentSearchPipeline(object):
	def __init__(self):
		connection = pymongo.MongoClient(settings['MONGODB_URL'])
		if connection is None:
			print("Error connecting to mongodb")
			return

		self.db = connection[settings['MONGODB_DB']]
		self.ls_questions = self.db[settings['MONGODB_LS_COLLECTION']]

		# DROP THE COLLECTION TO START FRESH
		self.ls_questions.drop()

	def process_item(self, items, spider):

		if spider.name == "ls_questions":
			questions = items['questions']
			if len(questions) == 0:
				return

			inserted_ids = []
			try:
				result = self.ls_questions.insert_many(list(questions),
													   ordered=False)
			except pymongo.errors.OperationsFailure as exc:
				print("Operation failure during insert_many()")
			else:
				inserted_ids = result.inserted_ids
		else:
			raise ValueError("Invalid collection:", spider.name)

		return items
