#
# Define our Spiders here
# Spiders are classes that Scrapy uses to scrape information from a website
#
# In this file we define spiders that scrape questions asked in Rajya Sabha
#
#

import scrapy
from scrapy.http import FormRequest
from parliamentsearch.items import RajyaSabhaQuestion
from ..models import PQDataModel
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from scrapy.selector import Selector


class RSQuestionSpider(scrapy.Spider):
    """
    This spider scrapes the questions asked in Rajya Sabha
    """

    name = "rs_questions"
    base_url = 'http://164.100.47.5/qsearch/qsearch.aspx'
    count = 0

    def start_requests(self):
        for i in range(5000, 241936):
            url = "http://164.100.47.5/QSearch/AccessQuestionIpad.aspx?qref={}"
            url = url.format(i)
            request = scrapy.Request(url, dont_filter=True, callback=self.parse_page)
            request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [301, 302]
            yield request

    def parse_page(self, response):
        self.logger.debug("(parse_page) response: status=%d, URL=%s" % (response.status, response.url))
        if response.status in (302,) and 'Location' in response.headers:
            self.parse_questions(response.url)

    def parse_questions(self, url):
        resp = requests.get(url, timeout=60)
        print(url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        question_ministry = soup.find(id="ctl00_ContentPlaceHolder1_Label1").text
        question_type = soup.find(id="ctl00_ContentPlaceHolder1_Label2").text
        question_no = soup.find(id="ctl00_ContentPlaceHolder1_Label3").text
        question_date = soup.find(id="ctl00_ContentPlaceHolder1_Label4").text
        question_subject = soup.find(id="ctl00_ContentPlaceHolder1_Label5").text
        question_member = soup.find(id="ctl00_ContentPlaceHolder1_Label7").text
        question_text = soup.find(id="ctl00_ContentPlaceHolder1_GridView2").text
        question_query = soup.find(id="ctl00_ContentPlaceHolder1_GridView2").find_all('td', class_="griditem")[0].text
        question_answer = soup.find(id="ctl00_ContentPlaceHolder1_GridView2").find_all('td', class_="griditem")[1].text
        question_annex = {a.text: a['href'] for a in soup.find_all('a', href=True)}

        q = dict()
        q['question_origin'] = 'rajyasabha'
        q['question_number'] = "".join(reversed(question_date.split("."))) + question_no
        q['question_type'] = question_type
        q['question_session'] = 0 

        q['question_date'] = question_date
        q['question_ministry'] = question_ministry
        member_list = list()
        member_list.append(question_member)
        q['question_member'] = member_list
        q['question_subject'] = question_subject

        q['question_annex'] = question_annex
        q['question_url'] = url
        q['question_text'] = question_text
        q['question_query'] = question_query
        q['question_answer'] = question_answer

        print(q)

        self.insert_in_db(q)

        return q

    def insert_in_db(self, q):
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
        record.question_query = q['question_query']
        record.question_answer = q['question_answer']
        record.question_url = q['question_url']
        record.question_date = datetime.strptime(q['question_date'], '%d.%m.%Y')
        record.save()
