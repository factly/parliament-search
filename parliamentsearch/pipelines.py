# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
import pymongo
from datetime import datetime
from .models import PQDataModel


class ParliamentSearchPipeline(object):
    def __init__(self):
        self.connection = None

    def process_item(self, items, spider):

        if spider.name == "ls_questions":
            questions = items['questions']

            # self.insert_in_db(questions)

        else:
            raise ValueError("Invalid collection:", spider.name)

        return items

    def insert_in_db(self, questions):

        with PQDataModel.batch_write() as batch:
            records = []
            for q in questions:
                record = PQDataModel()
                record.question_number = q['question_number']
                record.question_origin = q['question_origin']
                record.question_type = q['question_type']
                record.question_session = q['question_session']
                record.question_ministry = q['question_ministry']
                record.question_member = q['question_member']
                record.question_subject = q['question_subject']
                record.question_type = q['question_type']
                record.question_annex = q['question_annex']
                record.question_url = q['question_url']
                record.question_text = q['question_text']
                record.question_url = q['question_url']
                record.question_date = datetime.strptime(q['question_date'], '%d.%m.%Y')

                records.append(record)

            for record in records:
                batch.save(record)

